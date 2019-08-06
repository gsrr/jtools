import ConfigParser
import os
import sys
import subprocess
import time

import qlib

def exec_cmd(cmd):
    print "# %s"%cmd
    os.system(cmd)

'''
#case3: scsi_times_out test
echo 1 > /sys/block/sdd/device/timeout
"unplug drive"
hexdump -C /share/CACHEDEV1_DATA/.system_disk_data/*_201
"index 0x0a"
"count 0x0a"
'''

def fork_process(cmd):
    pid = os.fork()
    if pid == 0:
        os.system(cmd)
    elif pid > 0:
        return pid
    else:
        return -1;
    return 0

def cmd_getoutput(cmd):
    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    lines = proc.stdout.readlines()
    return lines

def get_serial_no(devname):
    cmd = "hdparm -I %s | grep Serial"%devname
    lines = cmd_getoutput(cmd)
    line = lines[0]
    return line.split(":")[1].strip()

def test_case4():
    qlib.get_diskinfo()
    hdd = qlib.gdiskinfo['hdd'][0][0]
    serial = get_serial_no(hdd)
    exec_cmd("echo 1 > /sys/block/%s/device/timeout"%hdd.split("/")[2])
    pid = fork_process("/root/ioping %s > /dev/null"%hdd)
    if pid < 0:
        print "process fork fail"
    elif pid > 0:
        time.sleep(10)
        #exec_cmd("cat /dev/kmsg") 
        cmd = "hexdump -C /share/CACHEDEV1_DATA/.system_disk_data/disk_data_%s_201"%serial
        exec_cmd(cmd)
        os.system("kill -9 %d"%pid)
    exec_cmd("echo 30 > /sys/block/%s/device/timeout"%hdd.split("/")[2])

def test_case3():
    cmd = 'cat /var/log/hal_daemon.log | grep "dispatch latency"'
    print "# " + cmd
    lines = cmd_getoutput(cmd)
    line = lines[-1]
    print line

def test_case2():
    qlib.get_diskinfo()
    hdd = qlib.gdiskinfo['hdd'][0][0]
    serial = get_serial_no(hdd)
    exec_cmd("echo 1 > /sys/block/%s/device/qnap_param_latency"%hdd.split("/")[2])
    pid = fork_process("/root/ioping %s > /dev/null"%hdd)
    if pid < 0:
        print "process fork fail"
    elif pid > 0:
        time.sleep(10)
        #exec_cmd("cat /dev/kmsg") 
        cmd = "hexdump -C /share/CACHEDEV1_DATA/.system_disk_data/disk_data_%s_201"%serial
        exec_cmd(cmd)
        os.system("kill -9 %d"%pid)

    #os.system("echo 1000 > /sys/block/%s/device/qnap_param_latency"%hdd.split("/")[2])

def test_case1():
    cmd = "cat /sys/block/sdb/device/qnap_param_latency"
    exec_cmd(cmd)

def download_tools():
    pass

def main():
    download_tools()
    funcs = []
    for name in dir(sys.modules[__name__]):
        if name.startswith("test_case"):
            funcs.append([int(name[len("test_case"):]),name])
    for i, name in funcs:
        func = getattr(sys.modules[__name__], name)
        func()

if __name__ == "__main__":
    main()

