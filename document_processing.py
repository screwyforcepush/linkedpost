from langchain.document_loaders import GitLoader

def load_data_from_git(clone_url, repo_path, branch="master"):
    loader = GitLoader(clone_url=clone_url, repo_path=repo_path, branch=branch)
    data = loader.load()
    return data

def filter_files_to_load(repo_path, file_filter):
    loader = GitLoader(repo_path=repo_path, file_filter=file_filter)
    data = loader.load()
    return data

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

def get_chunks_from_pdf_url(pdfLink, docMetadata):
    loader = OnlinePDFLoader(pdfLink)
    data = loader.load()
    chunks = text_splitter.split_documents(data)
    for chunk in chunks:
        chunk.metadata = docMetadata
    return chunks

def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

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
