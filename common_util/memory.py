# %%
import json

from langchain import PromptTemplate
from langchain.chains import LLMChain
from common_util.customClasses import CUSTOM_ENTITY_EXTRACTION_PROMPT, SQLiteEntityStore
from common_util.llms import LLM_FACT
from langchain.memory import ConversationEntityMemory



entity_store=SQLiteEntityStore()
print(entity_store.conn)

ENTITY_MEMORY = ConversationEntityMemory(llm=LLM_FACT, entity_store=entity_store, entity_extraction_prompt=CUSTOM_ENTITY_EXTRACTION_PROMPT, k=0)
entity_memory_long_cache=[]

def set_entity_memory_long_cache(cache):
    global entity_memory_long_cache
    entity_memory_long_cache=cache

def get_entity_memory_long_cache():
    global entity_memory_long_cache
    return entity_memory_long_cache


def save_entities_to_long_cach():
    global ENTITY_MEMORY, entity_memory_long_cache
    for entity in ENTITY_MEMORY.entity_cache:
        if entity not in entity_memory_long_cache:
            entity_memory_long_cache.append(entity)


def get_entities(use_long_cache:bool=False):
    global ENTITY_MEMORY, entity_memory_long_cache
    cache = ENTITY_MEMORY.entity_cache
    if use_long_cache:
        cache = entity_memory_long_cache
    entity_summaries = {}
    for entity in cache:
        if ENTITY_MEMORY.entity_store.get(entity):
            entity_summaries[entity] = ENTITY_MEMORY.entity_store.get(entity, "")
    return entity_summaries

def load_memory_vars(from_text:str):
    global ENTITY_MEMORY
    _input = {"input": from_text}
    ENTITY_MEMORY.load_memory_variables(_input)
    ENTITY_MEMORY.save_context(
        _input,
        {"output": ""}
    )
    save_entities_to_long_cach()


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
    global ENTITY_MEMORY
    entities = json.loads(key_words(query))
    ENTITY_MEMORY.entity_cache = entities
    save_entities_to_long_cach()
    return get_entities()


def get_entity_def(term:str)->str:
    """Look up definition of a term in entity database.
    Args:
        term: The entity key to query from the database.
    """
    global ENTITY_MEMORY
    return ENTITY_MEMORY.entity_store.get(term, "Not in Database")
