from loadGitResource import load_git_resource

clone_url = "https://github.com/hwchase17/langchain"
data = load_git_resource(clone_url, file_filter=".py")
print(data)
