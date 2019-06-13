#include "da_util.h"


unsigned int parse_cmd_parms(cmd_param *param_ary, char *params)
{
    int i;
    unsigned int index_bmp = 0;
    char *opt, *value;
    char *opteq;

    for (opt = strtok(params, ","); opt; opt = strtok(NULL, ","))
    {
        opteq = strchr(opt, '=');
        if (opteq)
        {
            value = opteq + 1;
            *opteq = '\0';

            for (i = 0; param_ary[i].param_name != 0; i++)
            {
                if (!strcmp(param_ary[i].param_name, opt))
                {
                    param_ary[i].param_value = value;
                    UINT_SET_BIT(index_bmp, i);
                }
            }
        }
    }

    return index_bmp;
}

int parse_long_options(int index)
{
    int ret = -EINVAL;
    
    ret = func_array[index] (optarg);
    return ret;
}

/*
Example:
./da_util --iotest enc_id=0,port_id=1

*/
int da_iotest(char* arg)
{
	unsigned int bmap;
    //PD_INFO pd_info;
    int enc_id = -1;
    int port_id = -1;

    printf("iotest argument:%s\n", arg);
	if (arg)
    {
        bmap = parse_cmd_parms(param_ary, arg);
        if (UINT_TEST_BIT(bmap, PARAM_ENC_ID) && UINT_TEST_BIT(bmap, PARAM_PORT_ID))
        {
            enc_id = atoi(param_ary[PARAM_ENC_ID].param_value);
            port_id = atoi(param_ary[PARAM_PORT_ID].param_value);
        }
    }
    printf("This function is for iotest:(%d, %d)\n", enc_id, port_id);
    return 0;
}


int main(int argc, char *argv[])
{
    int ret = -1;
    int index = -1;

    while ((ret = getopt_long(argc,
                                  argv,
                                  "",
                                  options,
                                  &index)) >= 0)
    {
        switch (ret)
        {
            case 0: 
                ret = parse_long_options(index);
                break;
            default:
                printf("option is not exist\n");
                break;
        }
    }
    return 0;
}