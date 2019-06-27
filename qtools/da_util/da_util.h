
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>

#include "func.h"


#define EINVAL 1
#define UINT_SET_BIT(uint, pos)		((uint) |= (0x00000001 << (pos)))
#define UINT_TEST_BIT(uint, pos)			((uint) & (0x00000001 << (pos)))

/* HAL Upper Layer Function */
int da_iotest(char* arg);

struct option *options;
typedef int (*fobj) (char* arg);

struct FuncStruct {
    char param[256];
    fobj func;
};

static struct FuncStruct func_array[] = {

    {"iotest", da_iotest},
    {"", NULL},
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
