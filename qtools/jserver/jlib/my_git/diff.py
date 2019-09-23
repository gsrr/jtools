import subprocess


def _get_branch_commit_renage(repo):
    cmd = "git reflog show --no-abbrev %s"%repo
    lines = subprocess.getoutput(cmd).splitlines()
    return (lines[0].split()[0], lines[-1].split()[0])

def diff_branch(repo):
    re, rs = _get_branch_commit_renage(repo)
    cmd = "git diff %s..%s"%(rs, re)
    data = subprocess.getoutput(cmd)
    return data
