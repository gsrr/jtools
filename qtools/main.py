import os
import sys
import subprocess

gdiskinfo = {}







def execute_cmd(cmd):
    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    lines = proc.stdout.readlines()
    return lines

def get_diskinfo():
    global gdiskinfo
    gdiskinfo['dom'] = []
    gdiskinfo['hdd'] = []
    cmd = "fdisk -l 2> /dev/null | grep Disk"
    lines = execute_cmd(cmd)
    for line in lines:
        items = line.split()
        #print items
        devname = items[1].strip(":")
        if devname.startswith("/dev/sd"):
            devsize = int(items[4]) / (10 ** 6)
            if devsize - 500 <= 100:
                print "%s is DOM, size = %d MB"%(devname, devsize)
                gdiskinfo['dom'].append(devname)
            else:
                print "%s is HDD or SSD, size = %d MB"%(devname, devsize)
                gdiskinfo['hdd'].append(devname)
                 

def get_info():
    get_diskinfo()

def ioping():
    global gdiskinfo
    cmd = "%s/bin/ioping %s"%(os.getcwd(), gdiskinfo['hdd'][0])
    print cmd
    os.system(cmd)

def test_latency():
    global gdiskinfo
    devname = gdiskinfo['hdd'][0].split("/")[2]
    cmd = "echo 1 > /sys/block/%s/device/qnap_param_latency"%(devname)
    print cmd
    os.system(cmd)
    ioping()
    cmd = "echo 100 > /sys/block/%s/device/qnap_param_latency"%(devname)
    os.system(cmd)


def main():
    get_info()
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
