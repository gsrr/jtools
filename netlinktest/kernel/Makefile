# SPDX-License-Identifier: GPL-2.0
#
# Makefile for the kernel software RAID and LVM drivers.
#

#obj-m		+= netlinktest.o
#obj-m		+= netlinkclient.o

#all:
#	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

#clean:
#	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

PWD := $(shell pwd) 
KVERSION := $(shell uname -r)
KERNEL_DIR = /home/jerrie/Build/linux-4.18/

MODULE_NAME = netlinkclient
obj-m := $(MODULE_NAME).o

all:
	make -C $(KERNEL_DIR) M=$(PWD) modules

clean:
	make -C $(KERNEL_DIR) M=$(PWD) clean
