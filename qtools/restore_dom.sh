#!/bin/bash

#apt-get install cifs-utils 
mount -t cifs -o username="read",password="read" //172.17.21.5/pub /mnt
rsync /mnt/NAS_FULL_IMAGE/TVS-X71/F_TVS-X71_20141126-1.2.8.img /root/
dd if=F_TVS-X71_20141126-1.2.8.img of=/dev/sdc