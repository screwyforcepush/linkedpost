import json
import re
from langchain.document_loaders import GitLoader
import shutil
import os

__all__ = ['load_git_resource']

DEFAULT_REPO_PATH = "./example_data/test_repo/"
DEFAULT_FILE_FILTER = lambda file_path: file_path.endswith(".md")
TITLES_FILENAME = './input_knowledge/titles.json'
EXCLUDE_TITLES_FILENAME = './ai_memory/ml_papers_of_the_week_searched.json'


def load_git_resource(clone_url, repo_path=DEFAULT_REPO_PATH, file_filter=DEFAULT_FILE_FILTER):
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
    loader = GitLoader(clone_url=clone_url, repo_path=repo_path, file_filter=file_filter, branch="main")
    data = loader.load()
    shutil.rmtree(repo_path)
    return data


def add_string_to_filearray(str, filename):
    arr = []

    # If file exists, load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            arr = json.load(f)

    # Add the new title
    arr.append(str)

    # Write the data back to the file
    with open(filename, 'w') as f:
        json.dump(arr, f, indent=4)

def add_new_week_papers():
    data = load_git_resource("https://github.com/dair-ai/ML-Papers-of-the-Week")
    
    # Regular expression pattern to match the arxiv ids
    pattern = r"https://arxiv\.org/abs/(\d+\.\d+)"

    # Use re.findall to get all matches in the text
    arxiv_ids = re.findall(pattern, data[0].page_content)

    # Load existing titles
    with open(TITLES_FILENAME, 'r') as f:
        existing_titles = json.load(f)

    # Load excluded titles
    with open(EXCLUDE_TITLES_FILENAME, 'r') as f:
        excluded_titles = json.load(f)
    count = 0
    # Add each arxiv_id to the titles file if it's not already there and not in the excluded titles
    for arxiv_id in arxiv_ids:
        if arxiv_id not in existing_titles and arxiv_id not in excluded_titles:
            add_string_to_filearray(arxiv_id, TITLES_FILENAME)
            add_string_to_filearray(arxiv_id, EXCLUDE_TITLES_FILENAME)
            count = count + 1
    print(count, "new ml papers added")