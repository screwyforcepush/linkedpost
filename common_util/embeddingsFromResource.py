# %%
import os
import time
import json
from langchain.document_loaders import OnlinePDFLoader
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone
from langchain.vectorstores import Pinecone
from dotenv import load_dotenv
from langchain.retrievers import ArxivRetriever
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from common_util.llms import LLM_CHAT, EMBEDDINGS

# %%
load_dotenv()

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

chain = LLMChain(llm=LLM_CHAT, prompt=chat_prompt)

def is_content_related_to_topic(content, topic):
    response = chain.run(content=content, topic=topic)
    return response in ("True", "true", "True.", "true.")


# %%
def get_docs(query):
    MAX_RETRIES = 100
    for i in range(MAX_RETRIES):
        try:
            docs = retriever.get_relevant_documents(query=query)
            return docs
            break
        except ConnectionResetError:
            if i < MAX_RETRIES - 1:  # i is zero indexed
                print("doc connection reset... retrying")
                time.sleep(1)  # wait a bit before trying again
                continue
            else:
                raise


# %%

def published_to_int(published):
    return int(published.replace("-", ""))

def process_document_metadata(metadata):
    pdfLink = False
    for string in metadata["links"]:
        if 'pdf' in string:
            pdfLink = string
    docMetadata = metadata
    if "entry_id" in docMetadata:
        docMetadata["source"] = docMetadata.pop("entry_id")
    docMetadata["date"] = published_to_int(docMetadata["Published"])
    docMetadata.pop("Summary")
    docMetadata = {
        k: v for k, v in docMetadata.items() if v is not None and v != ""
    }
    print(docMetadata)

    return pdfLink, docMetadata


# %%


tokenizer = tiktoken.get_encoding("cl100k_base")


# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""],
)


def get_chunks_from_pdf_url(pdfLink, docMetadata):
    loader = OnlinePDFLoader(pdfLink)
    data = loader.load()
    return get_chunks_from_loader_data(data, docMetadata)
 
def get_chunks_from_loader_data(data, metadata=False, source_merge=False): 
    chunks = text_splitter.split_documents(data)
    if metadata:
        for chunk in chunks:
            if(source_merge):
                chunk.metadata['source'] = metadata['source']
            else:
                chunk.metadata = metadata
    return chunks

# %%

texts = ["this is the first chunk of text", "then another second chunk of text is here"]

res = EMBEDDINGS.embed_documents(texts)
len(res), len(res[0])


# %%

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV")
)
index_name = "langchain-demo"
if index_name not in pinecone.list_indexes():
    # we create a new index
    pinecone.create_index(
        name=index_name,
        metric="cosine",
        dimension=len(res[0]),  # 1536 dim of text-embedding-ada-002
    )


# %%

index = pinecone.GRPCIndex(index_name)
# wait a moment for the index to be fully initialized
time.sleep(1)

index.describe_index_stats()


# %%
def upsert_chunks(chunks, namespace):
    try:
        docsearch = Pinecone.from_documents(
            chunks, EMBEDDINGS, index_name=index_name, namespace=namespace
        )
        time.sleep(1)
        print(index.describe_index_stats())
        return docsearch
    except ValueError as e: 
        print(repr(e))

    

def check_if_exists(metadata, filename):
    # If file doesn't exist, document hasn't been added yet
    if not os.path.exists(filename):
        return False

    with open(filename, 'r') as f:
        data = json.load(f)

    # Check if the metadata is in the file
    for item in data:
        if 'source' in metadata and 'source' in item and metadata['source'] == item['source']:
            return True
        elif 'Title' in metadata and 'Title' in item and metadata['Title'] == item['Title']:
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


def get_doc_queries(filename):
    # If file doesn't exist, document hasn't been added yet
    if not os.path.exists(filename):
        return False

    with open(filename, 'r') as f:
        docqueries = json.load(f)

    # Check if the title is in the file
    return docqueries
def remove_doc_query(filename, query):
    titles = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            titles = json.load(f)

    # Add the new title
    titles.remove(query)

    # Write the data back to the file
    with open(filename, 'w') as f:
        json.dump(titles, f, indent=4)

# Expose the functions as module-level functions
def get_docs_from_resource(query):
    return get_docs(query)

def is_content_related_to_topic_from_resource(content, topic):
    return is_content_related_to_topic(content, topic)

def process_document_metadata_from_resource(metadata):
    return process_document_metadata(metadata)

def get_chunks_from_loader_data_from_resource(data, metadata=False, source_merge=False):
    return get_chunks_from_loader_data(data, metadata, source_merge)

def get_chunks_from_pdf_url_from_resource(pdfLink, docMetadata):
    return get_chunks_from_pdf_url(pdfLink, docMetadata)

def upsert_chunks_from_resource(chunks, namespace):
    return upsert_chunks(chunks, namespace)

def check_if_exists_from_resource(metadata, filename):
    return check_if_exists(metadata, filename)

def add_metadata_from_resource(metadata, filename):
    return add_metadata(metadata, filename)

def get_doc_queries_from_resource(filename):
    return get_doc_queries(filename)

def remove_doc_query_from_resource(filename, query):
    return remove_doc_query(filename, query)
