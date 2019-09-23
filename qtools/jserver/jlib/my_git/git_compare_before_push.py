import commands
import sys
import os

hashid = None

def get_hashid():
    global hashid
    cmd = "git log -1 --pretty=format:%h"
    hashid = commands.getoutput(cmd).strip()
    return hashid

def get_diff_between_commit():
    global hashid
    cmd = "git diff %s^ %s > /tmp/diff"%(hashid, hashid)
    return os.system(cmd)

def patch2msg(fpath):
    basename = os.path.basename(fpath)
    basedir = os.path.dirname(fpath)
    fpath = basedir + "/" + basename.replace("patch", "msg")
    return fpath

def git_add_files():
    files = []
    fetch = False
    fpath = patch2msg(sys.argv[1])
    with open(fpath, "r") as fr:
        lines = fr.readlines()
        for line in lines:
            if fetch:
                files.append(line)
            if "related files" in line:
                fetch = True
    for f in files:
        cmd = "git add %s"%f.strip()
        #print cmd
        os.system(cmd)

def git_do_commit():
    fpath = patch2msg(sys.argv[1])
    cmd = "git commit -F %s"%fpath
    #print cmd
    os.system(cmd)

cmds = [
    git_add_files,
    git_do_commit,
    get_hashid,
    get_diff_between_commit,
    "diff /tmp/diff %s"%(sys.argv[1])
]

for cmd in cmds:
    if type(cmd) == str:
        print cmd
        os.system(cmd)
    else:
        ret = cmd()
        print cmd, ret



