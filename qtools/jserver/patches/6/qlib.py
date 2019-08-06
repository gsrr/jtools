import subprocess

gdiskinfo = {}

def execute_cmd(cmd):
    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    lines = proc.stdout.readlines()
    return lines

def _get_diskinfo(lines):
    for line in lines:
        items = line.split()
        devname = items[1].strip(":")
        if devname.startswith("/dev/sd"):
            devsize = int(items[4]) / (10 ** 6)
            if devsize >= 500 and devsize - 500 <= 100:
                gdiskinfo['dom'].append([devname, "%dMB"%devsize])
            else:
                gdiskinfo['hdd'].append([devname, "%dMB"%devsize])
                 
def get_diskinfo():
    global gdiskinfo
    gdiskinfo['dom'] = []
    gdiskinfo['hdd'] = []
    cmd = "fdisk -l 2> /dev/null | grep Disk"
    lines = execute_cmd(cmd)
    _get_diskinfo(lines)
