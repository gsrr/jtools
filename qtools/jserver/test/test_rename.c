#include <stdio.h>

int main()
{
    int ret;
    ret = rename("/root/file.test", "/mnt_172.17.22.47/root/file.test.1");
    printf("ret = %d\n", ret);
    return 0;
}
