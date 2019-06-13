#!/bin/bash

mkdir /root/2
mkdir /root/3
mount /dev/$1"2" /root/2
mount /dev/$1"3" /root/3

cp ./bzImage ./2/boot/
cp ./bzImage.cksum ./2/boot/

cp ./bzImage ./3/boot/
cp ./bzImage.cksum ./3/boot/
