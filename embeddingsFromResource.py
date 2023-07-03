# %%
import os
import time
from langchain import FewShotPromptTemplate
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import json
from langchain.document_loaders import OnlinePDFLoader
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.vectorstores import Pinecone
from dotenv import load_dotenv
from langchain.retrievers import ArxivRetriever
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

# %%
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(model_name="text-davinci-003", openai_api_key=OPENAI_API_KEY)
chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)

retriever = ArxivRetriever(load_max_docs=5, load_all_available_meta=True)

content_is_topic_template = """you are an expert in content categorization for the topic {topic}. You determine if the content provided is related to {topic}.
# Constraints
Limit response to a single word 'True' or 'False'
Do not include additional text in response
Do not include punctuation in response

"""

system_message_prompt = SystemMessagePromptTemplate.from_template(content_is_topic_template)

# Human question prompt
human_template = """# Content
{content}"""
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

chain = LLMChain(llm=chat, prompt=chat_prompt)

def is_content_related_to_topic(content, topic):
    response = chain.run(content=content, topic=topic)
    return response in ("True", "true", "True.", "true.")

tokenizer = tiktoken.get_encoding("cl100k_base")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""],
)

def upsert_chunks(chunks, namespace):
    docsearch = Pinecone.from_documents(
        chunks, embeddings, index_name=index_name, namespace=namespace
    )
    time.sleep(1)
    print(index.describe_index_stats())
    return docsearch

def check_if_exists(metadata, filename):
    # If file doesn't exist, document hasn't been added yet
    if not os.path.exists(filename):
        return False

    with open(filename, 'r') as f:
        data = json.load(f)

    # Check if the metadata is in the file
    for item in data:
        if item['Published'] == metadata['Published'] and item['Title'] == metadata['Title']:
            return True

    return False

def add_metadata(metadata, filename):
    data = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)

    # Add the new metadata
    data.append(metadata)

    # Write the data back to the file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

namespace = "ai-research"
newerthan = 20230000
filename = 'metadata.json'
doc_queries_filename = 'titles.json'
doc_queries = get_doc_queries(doc_queries_filename)

for query in doc_queries:
    print("getting research for ", query)
    docs = get_docs(query="generative ai prompt engineering")
    kept_docs = []
    for doc in docs:
        if published_to_int(doc.metadata["Published"])>newerthan and not check_if_exists(doc.metadata, filename):
            keep = is_content_related_to_topic(doc.metadata["Summary"], namespace)
            print(keep, namespace, doc.metadata["Title"])
            if keep:
                kept_docs.append(doc)

    print("kept",len(kept_docs),"out of",len(docs))
    for doc in kept_docs:
        pdfLink, docMetadata = process_document_metadata(doc.metadata)
        if not not pdfLink:
            chunks = get_chunks_from_pdf_url(pdfLink, docMetadata)
            docsearch = upsert_chunks(chunks, namespace)
            add_metadata(doc.metadata, filename)
    remove_doc_query(doc_queries_filename, query)
