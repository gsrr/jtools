
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>



#define EINVAL 1
#define UINT_SET_BIT(uint, pos)		((uint) |= (0x00000001 << (pos)))
#define UINT_TEST_BIT(uint, pos)			((uint) & (0x00000001 << (pos)))

/* HAL Upper Layer Function */
int da_iotest(char* arg);

typedef int (*fobj) (char* arg);

static fobj func_array[] = {

    da_iotest,
    NULL,
};

static struct option options[] = {
	
    {"iotest", required_argument, NULL, 0},
    {0, 0, 0, 0},
};

typedef struct _cmd_param {
    const char *param_name;
    char *param_value;
} cmd_param;

static cmd_param param_ary[] =
{
    { "enc_id", NULL},
    { "port_id", NULL},
    { NULL, NULL}
};

enum PARAM_HAL_APP_PARAM_ARY {
    PARAM_ENC_ID = 0,
    PARAM_PORT_ID,
};
