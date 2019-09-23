#!/bin/bash


rsync -a my_git /usr/lib/python2.7/
rsync -a hook/ /datapool/git_qnap/NasX86/.git/hooks/
rsync -a hook/ /datapool/git_qnap/linux/.git/hooks/
