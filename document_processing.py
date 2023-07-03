namespace = "ai-research"
newerthan = 20230000
filename = './json/metadata.json'
doc_queries_filename = './json/titles.json'
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
    published_to_int
)

doc_queries = get_doc_queries_from_resource(doc_queries_filename)
# %%
for query in doc_queries:
    print("getting research for ", query)
    docs = get_docs_from_resource(query="generative ai prompt engineering")
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
            docsearch = upsert_chunks_from_resource(chunks, namespace)
            add_metadata_from_resource(doc.metadata, filename)
    remove_doc_query_from_resource(doc_queries_filename, query)
# %%
