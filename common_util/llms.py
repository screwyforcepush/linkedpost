import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

LLM_FACT = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    temperature=0.0
)

LLM_FACT_DAV = ChatOpenAI(
    model_name='davinci-003',
    temperature=0.0
)

LLM_CHAT = ChatOpenAI(
    model_name="gpt-3.5-turbo", 
    temperature=0.2
)

EMBEDDINGS = OpenAIEmbeddings(disallowed_special=())

LLM_PLAN = ChatOpenAI(
    model_name='gpt-4',
    temperature=0.1
)

LLM_FACT_4 = ChatOpenAI(
    model_name='gpt-4',
    temperature=0.0
)

LLM_4_01 = ChatOpenAI(
    model_name='gpt-4',
    temperature=0.1
)

LLM_CHAT_4 = ChatOpenAI(
    model_name='gpt-4',
    temperature=0.2
)

LLM_BRAINSTORM = ChatOpenAI(
    model_name='gpt-4',
    temperature=0.7
)

LLM_FUNCTION = ChatOpenAI(
    model_name='gpt-4-0613',
    temperature=0.1
)
