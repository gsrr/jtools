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

int call_function_by_index(int index)
{
    int ret = -EINVAL;
    
    ret = func_array[index].func(optarg);
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

	if (arg)
    {
        bmap = parse_cmd_parms(param_ary, arg);
        if (UINT_TEST_BIT(bmap, PARAM_ENC_ID) && UINT_TEST_BIT(bmap, PARAM_PORT_ID))
        {
            enc_id = atoi(param_ary[PARAM_ENC_ID].param_value);
            port_id = atoi(param_ary[PARAM_PORT_ID].param_value);
        }
    }
    call_fio();
    printf("This function is for iotest:(%d, %d)\n", enc_id, port_id);
    return 0;
}

void init_options()
{
    int i;
    int cnt = 0;

    while (func_array[cnt].param[0] != '\0')
    {
        cnt += 1;
    }
    options = (struct option*)malloc(sizeof(struct option) * (cnt + 1));
     
    for(i = 0 ; i < cnt ; i++)
    {
        options[i].name = func_array[i].param;
        options[i].has_arg = required_argument;
        options[i].flag = NULL;
        options[i].val = 0;
        
    }
    options[cnt].name = 0;
    options[cnt].has_arg = 0;
    options[cnt].flag = 0;
    options[cnt].val = 0;
}

int main(int argc, char *argv[])
{
    int ret = -1;
    int index = -1;
    
    init_options();

    while ((ret = getopt_long(argc, argv, "", options, &index)) >= 0)
    {
        if(ret != 0)
        {
            printf("option is not exist\n");
            break;
        }
        ret = call_function_by_index(index);
    }
    free(options);
    return 0;
}
