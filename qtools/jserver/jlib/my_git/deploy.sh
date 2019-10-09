#!/bin/bash


rsync -a my_git /usr/lib/python3/dist-packages/
rsync -a hook/ /datapool/git_qnap/NasX86/.git/hooks/
rsync -a hook/ /datapool/git_qnap/linux/.git/hooks/
rsync -a hook/ /datapool/git_qnap/nasdriver/.git/hooks/
