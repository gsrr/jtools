#!/usr/bin/python
import sys
import os


def exec_cmd(cmd):
    print cmd
    os.system(cmd)

def reload_multi():
    cmds = [
        'rmmod dm-service-time',
        'rmmod dm-multipath',
        'insmod drivers/md/dm-multipath.ko',
        'insmod drivers/md/dm-service-time.ko',
    ]

    for cmd in cmds:
        exec_cmd(cmd)
    
def test_multi_remove():
    cmd = "dmsetup remove test-multi"
    os.system(cmd)

def test_multi_create_multibus():
    cmd = "dmsetup create test-multi --table '0 1024000 multipath 0 0 1 1 service-time 0 2 2 7:2 1 1 7:3 1 1'"
    print cmd
    os.system(cmd)

def test_multi_create():
    cmd = "dmsetup create test-multi --table '0 102400 multipath 0 0 2 1 service-time 0 1 2 7:0 1 1 service-time 0 1 2 7:1 1 1'"
    print cmd
    os.system(cmd)
    
def test_recreate():
    cmds = [
        'multipath -F',
        'multipath -v3',
        'dmsetup table',
        'multipath -ll',
    ]
    for cmd in cmds:
        exec_cmd(cmd)

def main():
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
