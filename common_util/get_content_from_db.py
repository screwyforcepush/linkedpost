import pinecone
import os
from langchain.vectorstores import Pinecone
from langchain.document_transformers import EmbeddingsRedundantFilter,EmbeddingsClusteringFilter
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.merger_retriever import MergerRetriever
from common_util.multi_query import MultiQueryRetriever, DEFAULT_QUERY_PROMPT
from common_util.llms import LLM_FACT, EMBEDDINGS
import tiktoken
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
tokens_gpt_4 = 8192
tokens_gpt_3 = 4096

import logging
logging.basicConfig()
logging.getLogger('custom.multi_query').setLevel(logging.INFO)
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index_name = "langchain-demo"
filter = EmbeddingsRedundantFilter(embeddings=EMBEDDINGS)

# This filter will divide the documents vectors into clusters or "centers" of meaning.
# Then it will pick the closest document to that center for the final results.
# By default the result document will be ordered/grouped by clusters.
filter_ordered_cluster = EmbeddingsClusteringFilter(
            embeddings=EMBEDDINGS,
            num_clusters=10,
            num_closest=1,
        )

pipeline = DocumentCompressorPipeline(transformers=[filter_ordered_cluster])

#%% 
tokenizer = tiktoken.get_encoding("cl100k_base")
# create the length function
def tiktoken_len(text:str):
    global tokenizer
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

max_doc_content_tokens=3000
def get_docs_content(docs,tokens=max_doc_content_tokens):
    joined_content = ""
    temp_joined = ""
    docs_page_content = []
    unique_docs = {}
    for d in docs:
        if d.page_content not in unique_docs:
            unique_docs[d.page_content] = True
            docs_page_content.append(d.page_content)
            temp_joined = "\n".join(docs_page_content)
            if tiktoken_len(temp_joined)>tokens:
                break
            joined_content = "\n".join(docs_page_content)
    print("max tokens reached ->",tiktoken_len(joined_content),tiktoken_len(temp_joined))
    return joined_content

def get_content_from_db(namespace, db_query, entities={}, tokens=max_doc_content_tokens, k=20):
    db = Pinecone.from_existing_index(index_name, EMBEDDINGS, namespace=namespace)
    # Define 2 diff retrievers with 2 diff embeddings and diff search type.
    retriever_all = db.as_retriever(
        search_type="similarity", search_kwargs={"k": k}
    )
    retriever_multi_qa = db.as_retriever(
        search_type="mmr", search_kwargs={"k": k}
    )
    # The Lord of the Retrievers will hold the ouput of boths retrievers and can be used as any other
    # retriever on different types of chains.
    lotr = MergerRetriever(retrievers=[retriever_all, retriever_multi_qa])

    retriever_from_llm = MultiQueryRetriever.from_llm(retriever=lotr,llm=LLM_FACT,entities=entities)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=pipeline, base_retriever=retriever_from_llm)
    docs = compression_retriever.get_relevant_documents(db_query)
    return get_docs_content(docs, tokens)

# %%
def get_latest_week_ai_research_abstracts():
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y%m%d')
    db = Pinecone.from_existing_index(index_name, EMBEDDINGS, namespace='ai-research')
    retriever_all = db.as_retriever(
        search_type="similarity", search_kwargs={"k": 20, "filter": { "date": { '$gt': int(two_weeks_ago) } }}
    )
    docs = retriever_all.get_relevant_documents("in conclusion the main findings are summarised")
    return get_docs_content(docs)
# %%
# %%
