filename = './json/metadata.json'

from embeddingsFromResource import (
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
from loadGitResource import load_git_resource
from langchain.document_loaders import DiffbotLoader
import os
from dotenv import load_dotenv
from namespaceEnum import PineconeNamespaceEnum
from langchain.document_loaders import UnstructuredPDFLoader

load_dotenv()
DIFFBOT_API_KEY = os.getenv("DIFFBOT_API_KEY")

def process_arxv():
    doc_queries_filename = './json/titles.json'
    namespace = PineconeNamespaceEnum.AI_RESEARCH.value
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
                chunks = get_chunks_from_pdf_url_from_resource(pdfLink, docMetadata)
                upsert_chunks_from_resource(chunks, namespace)
                add_metadata_from_resource(doc.metadata, filename)
        remove_doc_query_from_resource(doc_queries_filename, query)
# %%
def process_git():
    git_queries_filename = './json/git_urls.json'
    namespace = PineconeNamespaceEnum.AI_ENGINEERING_DOCUMENTATION.value
    git_queries = get_doc_queries_from_resource(git_queries_filename)
    for query in git_queries:
        metadata={}
        metadata['source']=query
        if check_if_exists_from_resource(metadata, filename):
            print("git docs exist ", query)
        else:
            print("getting git docs for ", query)
            data = load_git_resource(query)
            chunks = get_chunks_from_loader_data_from_resource(data, metadata, source_merge=True)
            upsert_chunks_from_resource(chunks, namespace)
            add_metadata_from_resource(metadata, filename)
        remove_doc_query_from_resource(git_queries_filename, query)
# %%
def process_scrape_urls():
    url_queries_filename = './json/scrape_urls.json'
    namespace = PineconeNamespaceEnum.VIDEO_STREAMING_ANALYTICS.value
    url_queries = get_doc_queries_from_resource(url_queries_filename)
    keep_queries = []
    for query in url_queries:
        metadata={}
        metadata['source']=query
        if check_if_exists_from_resource(metadata, filename):
            print("URL docs exist ", query)
        else:
            keep_queries.append(query)
    loader = DiffbotLoader(urls=keep_queries, api_token=DIFFBOT_API_KEY)
    data = loader.load()
    chunks = get_chunks_from_loader_data_from_resource(data)
    upsert_chunks_from_resource(chunks, namespace)
    for query in keep_queries:
        metadata={}
        metadata['source']=query
        add_metadata_from_resource(metadata, filename)
        remove_doc_query_from_resource(url_queries_filename, query)

def process_local_pdfs():
    pdfs_folder_path = './pdfs/'
    namespace = PineconeNamespaceEnum.VIDEO_STREAMING_ANALYTICS.value
    processed_pdfs_folder_path = './pdfs_processed/'
    for file in os.listdir(pdfs_folder_path):
        if file.endswith(".pdf"):
            metadata={}
            metadata['source']=file
            if check_if_exists_from_resource(metadata, filename):
                print("PDF docs exist ", file)
            else:
                loader = UnstructuredPDFLoader(f"{pdfs_folder_path}{file}")
                data = loader.load()
                chunks = get_chunks_from_loader_data_from_resource(data)
                upsert_chunks_from_resource(chunks, namespace)
                add_metadata_from_resource(metadata, filename)
                os.rename(f"{pdfs_folder_path}{file}", f"{processed_pdfs_folder_path}{file}")

# %%
process_arxv()
process_git()
process_scrape_urls()
process_local_pdfs()


# %%
