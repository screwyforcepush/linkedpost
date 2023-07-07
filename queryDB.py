# %%
import os
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from typing import Optional, Type
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from typing import Literal
from namespaceEnum import PineconeNamespaceEnum
from langchain import LLMMathChain, PromptTemplate, SerpAPIWrapper
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, Tool, tool
from langchain.chains.summarize import load_summarize_chain, map_reduce_prompt, refine_prompts, stuff_prompt
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory import ConversationEntityMemory
from langchain.memory import ConversationBufferMemory, CombinedMemory, ConversationSummaryMemory
from customClasses import (ResearchInput, SQLiteEntityStore, 
                           CUSTOM_ENTITY_EXTRACTION_PROMPT, UpdateResearchMemoryDeeperInput, UpdateResearchMemoryInput)
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
import re
import json
import tiktoken
from langchain.chains import ConversationChain


load_dotenv()
# %%

# Regular expression pattern to match paper titles
PAPER_PATTERN = r'paper "(.*?)"'
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
TITLES_FILENAME = './json/titles.json'
RESEARCH_FILENAME = './json/research_summaries.json'
NAMESPACE_AI=PineconeNamespaceEnum.AI_RESEARCH.value
SEED_QUERY="SEED QUERY PLACEHOLDER"
entity_memory_long_cache=[]

def set_seed_query(query):
    global SEED_QUERY
    SEED_QUERY=query

def get_seed_query():
    global SEED_QUERY
    return SEED_QUERY
    
def set_entity_memory_long_cache(cache):
    global entity_memory_long_cache
    entity_memory_long_cache=cache

openai = OpenAI(
    model_name="text-davinci-003",
    openai_api_key=OPENAI_API_KEY
)

LLM_FACT = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    temperature=0.0
)
LLM_CHAT = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

entity_store=SQLiteEntityStore()
print(entity_store.conn)
# %%
ENTITY_MEMORY = ConversationEntityMemory(llm=LLM_FACT, entity_store=entity_store, entity_extraction_prompt=CUSTOM_ENTITY_EXTRACTION_PROMPT, k=0)
READ_ONLY_ENTITY_MEMORY = ReadOnlySharedMemory(memory=ENTITY_MEMORY)


tokenizer = tiktoken.get_encoding("cl100k_base")


# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index_name = "langchain-demo"
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# %%
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain


template = """
        Act as a research assistant in {topic}.
        You dig deep into your research, and create detailed and thoughtful queries to be run on an extensive database of research.
        You will be presented with research content, and you will respond with a thought provoking query.
        Your query is progressive from your last query "{question}".
        If there is an unusually interesting research potential, you respond with multiple queries seperated by newline.
        """

system_message_prompt = SystemMessagePromptTemplate.from_template(template)

# Human question prompt
human_template = "Content: {docs}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

dig_deeper_chain = LLMChain(llm=LLM_CHAT, prompt=chat_prompt)
# %%


#TODO make a multi chain instead of nested llm
def answer_from_resource(ai_query, research_field):
    """
    gpt-3.5-turbo can handle up to 4097 tokens. Setting the chunksize to 1000 and k to 4 maximizes
    the number of tokens to analyze.
    """
    content = json.dumps(get_reserach_from_file(RESEARCH_FILENAME,SEED_QUERY)['summaries'])
    print("content length", tiktoken_len(content))
    # Template to use for the system message prompt
    template = """
        Act as an expert in {topic}. You answer questions and provide insight into the content.

        # constraints
        Only use the factual information from the content to form a response.
        If you feel like you don't have enough information to respond truthfully, say "I don't know".
        Your responses should be verbose and detailed.
        Draw upon your working knowledge to enrich your response

        # Working knowledge
        {entities}

        # content
        {content}
        """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    # Human question prompt
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = ConversationChain(llm=LLM_CHAT, prompt=chat_prompt)

    response = chain.run(question=ai_query, content=content, topic=research_field, entities=get_entities(cache=entity_memory_long_cache))
    response = response.replace("\n", "")
    return response

def get_content_from_db(namespace, db_query, k=4):
    db = Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
    docs = db.similarity_search(db_query,k=k)
    docs_page_content = " ".join([d.page_content for d in docs])
    # print(docs_page_content)
    return docs_page_content

def summarise(content,question):
    prompt_template = """Act as a research assistant. 
    Your task is to share your subject matter expertiese on the topic "{question}".
    Concisely summarise the key points from the abstract provided.
    Include specifics about how it works and how application can be executed.
    You have access to some additional relevant information provided in the Context section below.
    Draw upon your existing working knowledge of the subject to enrich your response.
    
    # Working knowledge
    {entities}

    # Abstract 
    {content}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["content", "question", "entities"])

    summary_chain = LLMChain(
        prompt=prompt,
        llm=LLM_FACT
    )
    return(summary_chain.run(content=content,question=question, entities=get_entities())) 



def extract_paper_title(question):
    match = re.search(PAPER_PATTERN, question)
    return match.group(1) if match else None

def check_if_exists(title, filename):
    # If file doesn't exist, document hasn't been added yet
    if not os.path.exists(filename):
        return False

    with open(filename, 'r') as f:
        data = json.load(f)

    # Check if the title is in the file
    return title in data

def add_string_to_filearray(str, filename):
    arr = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            arr = json.load(f)

    # Add the new title
    arr.append(str)

    # Write the data back to the file
    with open(filename, 'w') as f:
        json.dump(arr, f, indent=4)

def add_research_to_file(summary, raw, filename, seed_query):
    data = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)

    # Add the new metadata
    for item in data:
        if item['seed'] == seed_query:
            item['summaries'].append(summary)
            item['raw'].append(raw)
            break
    else:
        data.append({'seed':seed_query,'summaries':[summary],'raw':[raw]})

    # Write the data back to the file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_reserach_from_file(filename, seed_query):
    data = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)

    # Add the new metadata
    for item in data:
        if item['seed'] == seed_query:
            return item
    else:
        return None



def update_research_memory(query, namespace, dig_deeper=False):
    if dig_deeper:
        query = dig_deeper_chain.run(question=query, docs=get_content_from_db(namespace, query), topic=namespace)
        title = extract_paper_title(query)
        
        #TODO check datasource is not in metadata.json already, throw exception if it is
        if title and not check_if_exists(title, TITLES_FILENAME):
            add_string_to_filearray(title, TITLES_FILENAME)
    docs=get_content_from_db(namespace, query)
    sumer = summarise(docs, query)
    add_research_to_file(sumer,docs, RESEARCH_FILENAME,SEED_QUERY)
    _input = {"input": sumer}
    ENTITY_MEMORY.load_memory_variables(_input)
    ENTITY_MEMORY.save_context(
        _input,
        {"output": ""}
    )
    save_entities_to_long_cach()

    return sumer

# %%
def dig_deeper_research_wrapper(query, namespace):
    return update_research_memory(query, namespace, dig_deeper=True)
# %%
def get_entities(cache = ENTITY_MEMORY.entity_cache):
    entity_summaries = {}
    for entity in cache:
        entity_summaries[entity] = ENTITY_MEMORY.entity_store.get(entity, "")
    return entity_summaries
def save_entities_to_long_cach():
    for entity in ENTITY_MEMORY.entity_cache:
        if entity not in entity_memory_long_cache:
            entity_memory_long_cache.append(entity)


tools = [
    StructuredTool.from_function(
        func=answer_from_resource,
        name = "Answer from learnings",
        description=f"useful for when you need to answer a question based on learnings so far",
        args_schema= ResearchInput
    ),
    StructuredTool.from_function(
        func=update_research_memory,
        name = "Get new learnings",
        description=f"useful for when you need to learn more about {list(PineconeNamespaceEnum.get_all_namespaces())}",
        args_schema= UpdateResearchMemoryInput
    ),
    StructuredTool.from_function(
        func=dig_deeper_research_wrapper,
        name = "Get tangental learnings",
        description=f"useful for when you need to explore and learn about connected subject matter about {list(PineconeNamespaceEnum.__members__.values())}. Will not answer your direct question.",
        args_schema= UpdateResearchMemoryDeeperInput
    )
]


# %%
