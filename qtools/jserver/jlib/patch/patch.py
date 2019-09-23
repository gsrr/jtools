import os


def exec_cmd(cmd):
    print cmd
    os.system(cmd)

def reverse():
    cmd = "patch -R -p1 -i %s -d %s"%(pfile, wkdir)
    exec_cmd(cmd)

def exec():
    cmd = "patch -p1 -i %s -d %s"%(pfile, wkdir)
    exec_cmd(cmd)




