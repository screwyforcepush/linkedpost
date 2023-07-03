from langchain.document_loaders import GitLoader
import shutil

__all__ = ['load_git_resource']

DEFAULT_REPO_PATH = "./example_data/test_repo/"
DEFAULT_FILE_FILTER = lambda file_path: file_path.endswith(".md")

def load_git_resource(clone_url, repo_path=DEFAULT_REPO_PATH, file_filter=DEFAULT_FILE_FILTER):
    loader = GitLoader(clone_url=clone_url, repo_path=repo_path, file_filter=file_filter, branch="master")
    data = loader.load()
    shutil.rmtree(repo_path)
    return data
