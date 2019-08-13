import diskinfo
import os
import time
import glob

diskinfo.get_diskinfo()
info = diskinfo.gdiskinfo

cnt = 0
while True:
    for hdd in info['hdd']:
        dev = hdd.split("/")[2]
        cmds = [
            #"ls -al /sys/block/%s/device/"%(dev),
            "echo 1 > /sys/block/%s/device/delete"%(dev),
        ]
        for cmd in cmds:
            print cmd
            os.system(cmd)

    for i in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        print 'echo "- - -" > /sys/class/scsi_host/host%d/scan'%i
        os.system('echo "- - -" > /sys/class/scsi_host/host%d/scan'%i)
    cnt += 1
    print cnt
