#include "main.h"
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <mntent.h>	/* for getmntent(), et al. */

int open_new(char *path)
{
    int fd;
    printf("start to open file:%s\n", path);
    if( access( path, F_OK ) != -1 ) 
    {
        printf("file exist\n");
        unlink(path);
    } 
    else 
    {
        printf("file doesn't exist\n");
    } 
    fd = open(path, O_CREAT | O_WRONLY, 0644);
    return fd;
}

int is_dir_exist(char *path)
{
    struct stat s;
    int err = stat(path, &s);
    if(err == -1) 
    {
        printf("%s is not exist\n", path);
        return err;
    }
    else
    {
        if(S_ISDIR(s.st_mode) == 0)
        {
            printf("%s is not a dir\n", path);
            return -1;
        }
        printf("%s is exist\n", path);
    }
    return 0;
}

/* print_mount --- print a single mount entry */

void print_mount(const struct mntent *fs)
{
	printf("%s %s %s %s %d %d\n",
		fs->mnt_fsname,
		fs->mnt_dir,
		fs->mnt_type,
		fs->mnt_opts,
		fs->mnt_freq,
		fs->mnt_passno);
}

int is_mnt_exist(char *mntdir)
{
	FILE *fp;
	struct mntent *fs;

	fp = setmntent("/etc/mtab", "r");	/* read only */
	if (fp == NULL) {
		fprintf(stderr, "%s: could not open: %s\n", mntdir, strerror(errno));
		return -1;
	}

	while ((fs = getmntent(fp)) != NULL)
	{
		if(strcmp(mntdir, fs->mnt_dir) == 0)
		{
			printf("%s is exist\n", mntdir);
			return 0;
		}
	}

	endmntent(fp);
	printf("%s is not exist\n", mntdir);
	return -1;
}

/*
 * you can use an asterisk (*) to pass the width specifier/precision to printf(), rather than hard coding it into the format string
 */
void split_str(char *line, int len, char del)
{
    printf("version 1\n");
    int i;
    for(i = 0 ; i < len ; i++)
    {
        if (line[i] == del)
        {
            break;
        }
    }
    printf("key = value : %.*s = %s\n", i, line, line + i + 1);
}

int read_line_by_line(char *path)
{
    FILE *fp = fopen(path, "r");
    char *line = NULL;
    size_t len = 0;
    char *pch = NULL;

    if(fp == NULL) {
        perror("Unable to open file!");
        return -1;
    }

    while(getline(&line, &len, fp) != -1) {
        printf("line length: %zd\n", strlen(line));
        split_str(line, len, '=');        
    }

    printf("\n\nMax line size: %zu\n", len);

    fclose(fp);
    free(line); 
    // getline will resize the input buffer as necessary
    // the user needs to free the memory when not needed!
    return 0;
}

int main(int argc, char *argv[])
{
    int cnt = 0;
    while(file_func_arr[cnt].name[0] != '\0')
    {
        if(strcmp(argv[1], file_func_arr[cnt].name) == 0)
        {
            file_func_arr[cnt].func(argv[2]);
            break;
        }
        cnt += 1;
    }
    return 0;
}
