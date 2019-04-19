#!/bin/bash

#要執行「apt-get source」這個動作，還有一個要注意的，就是「/etc/apt/sources.list」，裡面要有「deb-src」開頭的設定，設定Source Repository。

echo -e "deb-src http://tw.archive.ubuntu.com/ubuntu/ trusty main restricted universe multivers" >> /etc/apt/sources.list
