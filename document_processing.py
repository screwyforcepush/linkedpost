namespace = "ai-research"
newerthan = 20230000
filename = 'metadata.json'
doc_queries_filename = 'titles.json'
doc_queries = get_doc_queries(doc_queries_filename)
# %%
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
# %%
