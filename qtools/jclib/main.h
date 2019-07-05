#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef int (*file_fobj) (char *path);

int open_new(char *path);
int is_dir_exist(char *path);
int is_mnt_exist(char *mntname);
int read_line_by_line(char *path);

struct file_func_obj {
    char name[32];
    file_fobj func;
};


static struct file_func_obj file_func_arr[] = {
    {"open_new", open_new},
    {"is_dir_exist", is_dir_exist},
    {"is_mnt_exist", is_mnt_exist},
    {"read_line_by_line", read_line_by_line},
    {"", NULL},
};
