# %%
import os
from langchain.tools import BaseTool, StructuredTool
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Type
from common_util.memory import load_memory_vars, get_entities, save_entities_to_long_cach
from common_util.llms import LLM_CHAT, LLM_FACT
from common_util.get_content_from_db import get_content_from_db
from common_util.memory import get_entity_def
from common_util.namespaceEnum import PineconeNamespaceEnum, get_all_namespaces,get_all_namespace_values, NamespaceArg
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
NAMESPACE_AI=PineconeNamespaceEnum.AI_RESEARCH
SEED_QUERY="SEED QUERY PLACEHOLDER"

def set_seed_query(query):
    global SEED_QUERY
    SEED_QUERY=query

def get_seed_query():
    global SEED_QUERY
    return SEED_QUERY
    
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
    response = chain.run(content=content, question=query, topic=namespace, entities=get_entities(use_long_cache=True))
    response = response.replace("\n", "")
    return response

def summarise(content,question):
    prompt_template = """Act as a research assistant. 
    Your task is to share your subject matter expertiese on the topic "{question}".
    Concisely summarise the key points from the abstract provided.
    Include specifics about how it works and how application can be executed.
    You have access to some additional relevant information provided in the Context section below.
    Include in your summary any points of interest connected to the given Context.
    
    # Context
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
    docs=get_content_from_db(namespace, query, entities=get_entities(use_long_cache=True))
    sumer = summarise(docs, query)
    add_research_to_file(sumer,docs, RESEARCH_FILENAME,SEED_QUERY)
    load_memory_vars(sumer)
    save_entities_to_long_cach()

    return sumer

# %%
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
