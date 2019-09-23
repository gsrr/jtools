
import git
from urlparse import urlparse
import os


def get_origin_url():
    repo = git.Repo.init(path='.')
    return repo.remotes.origin.url

def get_repo_name():
    repo = git.Repo.init(path='.')
    url = repo.remotes.origin.url
    o = urlparse(url)
    return os.path.basename(o.path)

def main():
    print "url:", get_origin_url()
    print "repo name:", get_repo_name()

if __name__ == "__main__":
    main()
