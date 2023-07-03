from langchain.document_loaders import GitLoader

def load_git_resource():
    loader = GitLoader(
        clone_url="https://github.com/hwchase17/langchain",
        repo_path="./example_data/test_repo2/",
        branch="master",
    )
    data = loader.load()
    return len(data)

def filter_files_to_load():
    loader = GitLoader(repo_path="./example_data/test_repo1/", file_filter=lambda file_path: file_path.endswith(".py"))

# Add any other existing code here

# Add the new function calls here
load_git_resource()
filter_files_to_load()
