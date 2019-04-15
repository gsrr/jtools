#!/bin/bash

# Download source code of linux kernel
wget https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/linux/4.18.0-10.11/linux_4.18.0.orig.tar.gz
tar -zxvf linux_4.18.0.orig.tar.gz

# create .config
cp /boot/config-4.4.0-21-generic .
make menuconfig

# Compile kernel
make -j 4 clean
make -j 4
make modules -j 4
make modules_install
make install
