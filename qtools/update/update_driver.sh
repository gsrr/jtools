#!/bin/bash

mkdir /root/2
mkdir /root/3
mount /dev/$1"2" /root/2
mount /dev/$1"3" /root/3

cp ./$2 ./2/boot/
cp ./$2.cksum ./2/boot/

cp ./$2 ./3/boot/
cp ./$2.cksum ./3/boot/
