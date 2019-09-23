import git
from urlparse import urlparse
import os


def get_repo_name():
    repo = git.Repo.init(path='.')
    url = repo.remotes.origin.url
    o = urlparse(url)
    return os.path.basename(o.path)

def get_branch_name():
    repo = git.Repo.init(path='.')
    branch_name = str(repo.head.ref)
    return branch_name

def is_branch_name_valid(name):
    if name == "master":
        return False

    if name.startswith("local") == False:
        return False

    return True
