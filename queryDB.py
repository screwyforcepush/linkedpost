# %%
import os
from langchain.tools import BaseTool, StructuredTool
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Type
from common_util.memory import load_memory_vars, split_json, get_entities, save_entities_to_long_cach
from common_util.llms import LLM_CHAT, LLM_FACT, LLM_FACT_4, LLM_CHAT_4
from common_util.get_content_from_db import get_content_from_db, get_latest_week_ai_research_abstracts
from common_util.memory import get_entity_def, tiktoken_len
from common_util.namespaceEnum import PineconeNamespaceEnum, PineconeNamespaceDescription, get_all_namespaces,get_all_namespace_values, NamespaceArg
from langchain import PromptTemplate
from langchain.tools import BaseTool
from common_util.customClasses import (ResearchInput, UpdateResearchMemoryInput)
import re
import json
import tiktoken
load_dotenv()
# %%

# Regular expression pattern to match paper titles
PAPER_PATTERN = r'paper "(.*?)"'
TITLES_FILENAME = './json/titles.json'
RESEARCH_FILENAME = './json/research_summaries.json'
SEED_QUERY="SEED QUERY PLACEHOLDER"
CONDUCTOR_KEY="NOT SET"
def set_seed_query(query):
    global SEED_QUERY
    SEED_QUERY=query

def get_seed_query():
    global SEED_QUERY
    return SEED_QUERY

def set_conductor_key(key):
    global CONDUCTOR_KEY
    CONDUCTOR_KEY=key

def get_conductor_key():
    global CONDUCTOR_KEY
    return CONDUCTOR_KEY

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
    content = json.dumps(get_reserach_from_file(RESEARCH_FILENAME,CONDUCTOR_KEY)['summaries'])
    print("Start content length", tiktoken_len(content))
    if tiktoken_len(content)>4000:
        if tiktoken_len(content)<6000:
            content = summarise(content,query,{})
        else:
            cont1,cont2 = split_json(content)
            content= {**cont1, **cont2}
        print("End content length", tiktoken_len(content))

    # TODO refine this prompt
    template = """
        Act as an expert in {topic}. You answer questions and provide insight into the content.

        # constraints
        Only use the factual information from the Content to form a response.
        If you feel like you don't have enough information to respond truthfully, say "I don't know".
        Your responses should be verbose and detailed.
        Draw upon your working knowledge to enrich your response

        # Working knowledge
        {entities}

        # Content
        {content}

        # question
        {question}
        """
    prompt = PromptTemplate(template=template, input_variables=["content", "question", "entities", "topic"])

    chain = LLMChain(llm=LLM_CHAT_4, prompt=prompt)

    entities=get_entities(use_long_cache=True,query=query)
    response = chain.run(content=content, question=query, topic=namespace, entities=entities)
    response = response.replace("\n", "")
    return response

def summarise(content,question,entities={}):
    prompt_template = """[System][Temperature=0][Persona]You are the Research Purifier. 
    You love to deeply understand the inner workings behind Research, then distill the applicable essence. You maximally compress the meaningful takeaways, while staying unambiguous to the model in a bare context.
    [TASK]
    Your task is to share your subject matter expertise on the topic "{question}".
    Concisely summarise the underlying principles and facts from the Research provided.
    Include specifics about how and why the concept, method, technique works.
    Include an application execution example if applicable.
    You have access to some additional relevant entity Context.
    Include in your summary any points of interest connected to the given Context.
    *Distill* *Summarise* *Purify*
    [/TASK]

    # Context
    {entities}

    # Research 
    {content}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["content", "question", "entities"])

    summary_chain = LLMChain(
        prompt=prompt,
        llm=LLM_FACT_4
    )
    return(summary_chain.run(content=content,question=question, entities=entities)) 



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

def add_research_to_file(summary, raw, filename, key=CONDUCTOR_KEY):
    data = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)

    # Add the new metadata
    for item in data:
        if 'key' in item and item['key'] == key:
            if 'summaries' in item:
                item['summaries'].append(summary)
            else:
                item['summaries']=[summary]
            if 'raw' in item:
                item['raw'].append(raw)
            else:
                item['raw']=[raw]
            item['seed']=SEED_QUERY
            break
    else:
        data.append({'key':key,'seed':SEED_QUERY,'summaries':[summary],'raw':[raw]})

    # Write the data back to the file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def add_to_research_file(property, value, key=CONDUCTOR_KEY, filename=RESEARCH_FILENAME, isArray=False):
    data = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)

    # Add the new metadata
    for item in data:
        if 'key' in item and item['key'] == key:
            if isArray:
                if property in item:
                    item[property].append(value)
                else:
                    item[property]=[value]
            else:
                item[property]=(value)
            break
    else:
        data.append({'key':key,property:value})

    # Write the data back to the file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_reserach_from_file(key, filename=RESEARCH_FILENAME):
    data = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)

    # Add the new metadata
    for item in data:
        if 'key' in item and item['key'] == key:
            return item
    else:
        return None



def update_research_memory(query:str, namespace:NamespaceArg)->str:
    """Get new research on a topic.
    
    Args:
        query: The question to be answered by research assistant.
        namespace: A NamespaceArg object that is the research domain.
    """
    #entities are used for multiquery, tokens used for output doc length
    docs=get_content_from_db(namespace, query, 
                             entities=get_entities(use_long_cache=True,entity_tokens=3000,query=query),
                             tokens=5000)
    sumer = summarise(docs, query, entities=get_entities(use_long_cache=True,entity_tokens=1000,query=query))
    add_research_to_file(sumer,docs, RESEARCH_FILENAME,CONDUCTOR_KEY)
    load_memory_vars(sumer)
    save_entities_to_long_cach()

    return sumer

def get_latest_ai_research():
    docs=get_latest_week_ai_research_abstracts()
    sumer = summarise(docs, "novel, breakthrough, and unique methods and technology")

    add_research_to_file(sumer,docs, RESEARCH_FILENAME,CONDUCTOR_KEY)
    load_memory_vars(sumer)
    save_entities_to_long_cach()
    return sumer
# %%
tools = [
    # StructuredTool.from_function(
    #     func=answer_from_resource,
    #     name = "answer_from_learnings",
    #     description="useful for when you need to answer a question based on learnings so far",
    #     args_schema= ResearchInput
    # ),
    StructuredTool.from_function(
        func=update_research_memory,
        name = "get_new_learnings",
        description="get new research on a topic",
        args_schema= UpdateResearchMemoryInput
    ),
    # StructuredTool.from_function(
    #     func=get_latest_ai_research,
    #     name = "get_latest_ai_research",
    #     description="get the latest AI news and research",
    # ),
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

ENTITY_TOOL = StructuredTool.from_function(
        func=get_entity_def,
        name = "search_database_for_term_definition",
        description="""quickly returns definition of a term if it is in the database. Useful for "What is <term>?" questions""",
    )

def reserach_ai(query:str):
    return update_research_memory(query=query, namespace=PineconeNamespaceEnum.AI_RESEARCH.value)

AI_RESEARCH_TOOL = StructuredTool.from_function(
        func=reserach_ai,
        name = "research_ai",
        description=f"learn from ai research database containing {PineconeNamespaceDescription.AI_RESEARCH.value}",
    )

def reserach_video_streaming(query:str):
    return update_research_memory(query=query, namespace=PineconeNamespaceEnum.VIDEO_STREAMING_ANALYTICS.value)

VIDEO_STREAMING_RESEARCH_TOOL = StructuredTool.from_function(
        func=reserach_ai,
        name = "research_video_streaming",
        description=f"learn from video streaming database containing {PineconeNamespaceDescription.VIDEO_STREAMING_ANALYTICS.value}",
    )

def reserach_ai_engineering(query:str):
    return update_research_memory(query=query, namespace=PineconeNamespaceEnum.AI_ENGINEERING_DOCUMENTATION.value)

AI_ENGINEERING_TOOL = StructuredTool.from_function(
        func=reserach_ai_engineering,
        name = "research_ai_engineering",
        description=f"learn from ai engineering database containing {PineconeNamespaceDescription.AI_ENGINEERING_DOCUMENTATION.value}",
    )

# %%
