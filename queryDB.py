# %%
import os
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from typing import Optional, Type
from get_content_from_db import get_content_from_db
from namespaceEnum import PineconeNamespaceEnum, get_all_namespaces,get_all_namespace_values, NamespaceArg
from langchain import LLMMathChain, PromptTemplate, SerpAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, Tool, tool
from langchain.memory import ConversationEntityMemory
from customClasses import (ResearchInput, SQLiteEntityStore, 
                           CUSTOM_ENTITY_EXTRACTION_PROMPT, UpdateResearchMemoryDeeperInput, UpdateResearchMemoryInput)
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
import re
import json
import tiktoken


load_dotenv()
# %%

# Regular expression pattern to match paper titles
PAPER_PATTERN = r'paper "(.*?)"'
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
TITLES_FILENAME = './json/titles.json'
RESEARCH_FILENAME = './json/research_summaries.json'
NAMESPACE_AI=PineconeNamespaceEnum.AI_RESEARCH
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

# %%

from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain

# %%


def answer_from_resource(query: str, namespace: NamespaceArg) -> str:
    """Get answer from research already performed.
    
    Args:
        query: The question to be answered by research assistant.
        namespace: A NamespaceArg object that is the research domain.
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

        # question
        {question}
        """
    prompt = PromptTemplate(template=template, input_variables=["content", "question", "entities", "topic"])

    chain = LLMChain(llm=LLM_CHAT, prompt=prompt)
    response = chain.run(content=content, question=query, topic=namespace, entities=get_entities(cache=entity_memory_long_cache))
    response = response.replace("\n", "")
    return response

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



def update_research_memory(query:str, namespace:NamespaceArg)->str:
    """Get new research on a topic.
    
    Args:
        query: The question to be answered by research assistant.
        namespace: A NamespaceArg object that is the research domain.
    """
    docs=get_content_from_db(namespace, query, entities=get_entities(cache=entity_memory_long_cache))
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
def get_entities(cache = ENTITY_MEMORY.entity_cache):
    entity_summaries = {}
    for entity in cache:
        if ENTITY_MEMORY.entity_store.get(entity):
            entity_summaries[entity] = ENTITY_MEMORY.entity_store.get(entity, "")
    return entity_summaries
def save_entities_to_long_cach():
    for entity in ENTITY_MEMORY.entity_cache:
        if entity not in entity_memory_long_cache:
            entity_memory_long_cache.append(entity)
def key_words(query):
    prompt_template = """Act as a an SEO expert. 
    Your task is to extract key words from the given text. Output a capitalised array.
    
    # EXAMPLE
    ## Text
    What is a unique AI prompting strategy? How can it be applied to video streaming analytics?
    ## Output
    ["AI Prompting", "AI Prompting Strategy", "Video Streaming", Video Streaming Analytics"]
    END OF EXAMPLE

    # EXAMPLE
    ## Text
    How can chain of thought prompting be used to increase video ad revenue?
    ## Output
    ["Chain of Thought", "Chain of Thought Prompting", "Video Ads", "Video Ad Revenue", "Ad Revenue"]
    END OF EXAMPLE

    ## Text
    {query}
    ## Output
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["query"])

    key_words_chain = LLMChain(
        prompt=prompt,
        llm=LLM_FACT
    )
    return(key_words_chain.run(query=query)) 


def warm_cache(query):
    entities = json.loads(key_words(query))
    ENTITY_MEMORY.entity_cache = entities
    save_entities_to_long_cach()
    return get_entities(entities)
def get_entity_def(term:str)->str:
    """Look up definition of a term in entity database.
    
    Args:
        term: The entity key to query from the database.
    """
    return ENTITY_MEMORY.entity_store.get(term, "Not in Database")

tools = [
    StructuredTool.from_function(
        func=answer_from_resource,
        name = "answer_from_learnings",
        description="useful for when you need to answer a question based on learnings so far",
        args_schema= ResearchInput
    ),
    StructuredTool.from_function(
        func=update_research_memory,
        name = "get_new_learnings",
        description="get new research on a topic",
        args_schema= UpdateResearchMemoryInput
    ),
    StructuredTool.from_function(
        func=get_entity_def,
        name = "search_database_for_term_definition",
        description="""quickly returns definition of a term if it is in the database. Useful for "What is <term>?" questions""",
    )
]

open_funk = [
    answer_from_resource,
    update_research_memory,
    get_entity_def
]


class NewLearningsTool(BaseTool):
    name = "get_new_learnings"
    description = f"""Useful when you want your research assistant to get new research on a topic
    """
    args_schema: Type[BaseModel] = UpdateResearchMemoryInput

    def _run(self, query: str, namespace: NamespaceArg):
        response = update_research_memory(query, namespace)
        return response

    def _arun(self, query: str, namespace: NamespaceArg):
        raise NotImplementedError("get_new_learnings does not support async")
open_tools = [
    NewLearningsTool()
]

# %%
# _input = {"input": "what is a unique AI prompting technique? How can it be applied to video streaming analytics?"}
# ENTITY_MEMORY.load_memory_variables(_input)
# ENTITY_MEMORY.save_context(
#     _input,
#     {"output": ""}
# )
# %%
print(get_all_namespaces())

# %%
