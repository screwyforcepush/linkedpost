from langchain.document_loaders import GitLoader

def load_data_from_git(clone_url, repo_path, branch="master"):
    loader = GitLoader(clone_url=clone_url, repo_path=repo_path, branch=branch)
    data = loader.load()
    return data

def filter_files_to_load(repo_path, file_filter):
    loader = GitLoader(repo_path=repo_path, file_filter=file_filter)
    data = loader.load()
    return data
