filename = './json/metadata.json'

import re
from common_util.embeddingsFromResource import (
    get_docs_from_resource,
    is_content_related_to_topic_from_resource,
    process_document_metadata_from_resource,
    get_chunks_from_pdf_url_from_resource,
    upsert_chunks_from_resource,
    check_if_exists_from_resource,
    add_metadata_from_resource,
    get_doc_queries_from_resource,
    remove_doc_query_from_resource,
    published_to_int,
    get_chunks_from_loader_data_from_resource
)
from common_util.loadGitResource import load_git_resource, add_new_week_papers
from langchain.document_loaders import DiffbotLoader
import os
from dotenv import load_dotenv
from common_util.namespaceEnum import PineconeNamespaceEnum
from langchain.document_loaders import UnstructuredPDFLoader
from common_util.researchAssistant import research_condense
import time

from queryDB import add_to_research_file


load_dotenv()
DIFFBOT_API_KEY = os.getenv("DIFFBOT_API_KEY")
RESEARCH_PAPERS_FILENAME = './json/ai_research_papers.json'


def process_arxv(namespace = PineconeNamespaceEnum.AI_RESEARCH.value):
    doc_queries_filename = './json/titles.json'
    newerthan = 20230000
    doc_queries = get_doc_queries_from_resource(doc_queries_filename)

    # %%
    for query in doc_queries:
        print("getting research for ", query)
        docs = get_docs_from_resource(query)
        kept_docs = []
        for doc in docs:
            if published_to_int(doc.metadata["Published"])>newerthan and not check_if_exists_from_resource(doc.metadata, filename):
                keep = is_content_related_to_topic_from_resource(doc.metadata["Summary"], namespace)
                print(keep, namespace, doc.metadata["Title"])
                if keep:
                    kept_docs.append(doc)

        print("kept",len(kept_docs),"out of",len(docs))
        for doc in kept_docs:
            pdfLink, docMetadata = process_document_metadata_from_resource(doc.metadata)
            if not not pdfLink:
                # TODO get the doc content  for condenced = concept_condence
                chunks, content = get_chunks_from_pdf_url_from_resource(pdfLink, docMetadata)
                if docMetadata['Title']:
                    add_to_research_file(property="source", value=docMetadata['source'], key=docMetadata['Title'], filename=RESEARCH_PAPERS_FILENAME)
                    summary = research_condense(content[0].page_content)
                    add_to_research_file(property="summary", value=summary, key=docMetadata['Title'], filename=RESEARCH_PAPERS_FILENAME)
                upsert_chunks_from_resource(chunks, namespace)
                doc.metadata['namespace']=namespace
                add_metadata_from_resource(doc.metadata, filename)
        remove_doc_query_from_resource(doc_queries_filename, query)
    print("process_arxv complete")

# %%
def process_git():
    git_queries_filename = './json/git_urls.json'
    namespace = PineconeNamespaceEnum.AI_ENGINEERING_DOCUMENTATION.value
    git_queries = get_doc_queries_from_resource(git_queries_filename)
    for query in git_queries:
        metadata={}
        metadata['source']=query
        metadata['namespace']=namespace
        if check_if_exists_from_resource(metadata, filename):
            print("git docs exist ", query)
        else:
            print("getting git docs for ", query)
            data = load_git_resource(query)
            chunks = get_chunks_from_loader_data_from_resource(data, metadata, source_merge=True)
            upsert_chunks_from_resource(chunks, namespace)
            add_metadata_from_resource(metadata, filename)
        remove_doc_query_from_resource(git_queries_filename, query)
    print("process_git complete")

# %%\

def get_data_loader(loader:DiffbotLoader):
    MAX_RETRIES = 20
    for i in range(MAX_RETRIES):
        data = loader.load()
        if i < MAX_RETRIES - 1 and len(data)==0:  # i is zero indexed
                print("URL scape failed... retrying")
                time.sleep(1)  # wait a bit before trying again
                continue
        else:
            return data
            break

def process_scrape_urls(namespace = PineconeNamespaceEnum.VIDEO_STREAMING_ANALYTICS.value):
    url_queries_filename = './json/scrape_urls.json'
    
    url_queries = get_doc_queries_from_resource(url_queries_filename)
    keep_queries = []
    for query in url_queries:
        metadata={}
        metadata['source']=query
        metadata['namespace']=namespace
        if check_if_exists_from_resource(metadata, filename):
            print("URL docs exist ", query)
        else:
            loader = DiffbotLoader(urls=[query], api_token=DIFFBOT_API_KEY)
            data = get_data_loader(loader)
            if len(data)>0:
                chunks = get_chunks_from_loader_data_from_resource(data)
                upsert_chunks_from_resource(chunks, namespace)
                keep_queries.append(query)
                metadata={}
                metadata['source']=query
                add_metadata_from_resource(metadata, filename)
                remove_doc_query_from_resource(url_queries_filename, query)
                print("URL processed", query)
            else:
                print("URL scrape failed",query)
        
    print("process_scrape_urls complete", len(keep_queries), "failed or exists", len(url_queries)-len(keep_queries))

def process_local_pdfs(namespace = PineconeNamespaceEnum.VIDEO_STREAMING_ANALYTICS.value):
    pdfs_folder_path = './pdfs/'
    processed_pdfs_folder_path = './pdfs_processed/'
    for file in os.listdir(pdfs_folder_path):
        if file.endswith(".pdf"):
            metadata={}
            metadata['source']=file
            metadata['namespace']=namespace
            if check_if_exists_from_resource(metadata, filename):
                print("PDF docs exist ", file)
            else:
                loader = UnstructuredPDFLoader(f"{pdfs_folder_path}{file}")
                data = loader.load()
                chunks = get_chunks_from_loader_data_from_resource(data)
                upsert_chunks_from_resource(chunks, namespace)
                add_metadata_from_resource(metadata, filename)
                os.rename(f"{pdfs_folder_path}{file}", f"{processed_pdfs_folder_path}{file}")
    print("process_local_pdfs complete")

# %%
add_new_week_papers()
process_arxv(namespace = PineconeNamespaceEnum.AI_RESEARCH.value)
#%%
process_git()
process_scrape_urls(PineconeNamespaceEnum.AI_ENGINEERING_DOCUMENTATION.value)
process_local_pdfs(namespace = PineconeNamespaceEnum.AI_RESEARCH.value)

# %%
