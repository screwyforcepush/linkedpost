from langchain.document_loaders import GitLoader
import shutil

__all__ = ['load_git_resource']

def load_git_resource(clone_url, repo_path, file_filter):
    loader = GitLoader(clone_url=clone_url, repo_path=repo_path, file_filter=file_filter)
    data = loader.load()
    shutil.rmtree(repo_path)
    return data
