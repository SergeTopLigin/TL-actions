from github import Github

# Authentication is defined via github.Auth
from github import Auth

# using an access token
auth = Auth.Token("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")

# Public Web Github
g = Github(auth=auth)

repo = g.get_repo("SergeTopLigin/TL-actions")
repo.create_file("test.txt", "test", "test", branch="main")