
#define _XOPEN_SOURCE

#include <stdio.h>

#include <time.h>

int tm2days(char *tm_str)
{
    struct tm tm;
    time_t epoch;

    if ( strptime(tm_str, "%Y-%m-%d-%H-%M", &tm) != NULL )
    {
        epoch = mktime(&tm);
    }
    else
    {
        printf("Can not parse time string\n");
        return 0;
    }

    return epoch/(60*60*24);
}

int main()
{
    tm2days("1234");
    printf("%d\n", tm2days("2019-12-01-05-30"));
    return 0;
}

