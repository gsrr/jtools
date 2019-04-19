#!/usr/bin/python
import sys
import os


def exec_cmd(cmd):
    print cmd
    os.system(cmd)

def create_loop_device():
    cmd = 'mknod -m 0660 /dev/loop0 b 7 0' # major=7, minor=0
    
def test_multi_remove():
    cmd = "dmsetup remove test-multi"
    os.system(cmd)

def test_loop_create():
    cmds = [
        'dd if=/dev/zero of=loopbackfile.img bs=100M count=10',
        'losetup -fP loopbackfile.img',
        'losetup -fP loopbackfile.img',
    ]
    for cmd in cmds:
        exec_cmd(cmd)
    
def main():
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
