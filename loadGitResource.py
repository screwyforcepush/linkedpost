from langchain.document_loaders import GitLoader

def load_git_resource(clone_url, repo_path):
    loader = GitLoader(
        clone_url=clone_url,
        repo_path=repo_path,
        branch="master",
    )
    data = loader.load()
    return len(data)

def filter_files_to_load(repo_path):
    loader = GitLoader(repo_path=repo_path, file_filter=lambda file_path: file_path.endswith(".py"))

# Add any other existing code here

# Add the new function calls here
load_git_resource("https://github.com/hwchase17/langchain", "./example_data/test_repo2/")
filter_files_to_load("./example_data/test_repo1/")
