#include <stdio.h>

typedef enum {
    TEST1,
    TEST2,
}TE;

typedef enum {
    TEST1 = 1,
    TEST2,
}TEE;

int main()
{
    printf("%d\n", TEST1);  
    printf("%d\n", TEST2);  
    return 0;
}