import sys
import os

def execmds(cmds):
    for cmd in cmds:
        print (cmd)
        os.system(cmd)
        print

def show():
    cmds = [
        "multipath -ll",
        'dmsetup table',
    ]
    execmds(cmds)    

def create():
    cmd = "multipath"
    os.system(cmd)

def remove():
    cmd = "multipath -F"
    os.system(cmd)

def main():
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
