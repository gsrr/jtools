#!/bin/bash

# case 1: The function cannot work if /share/CACHEDEV1_DATA1(default volume) is not exist.
# (The functions include inc_err_cnt, iotest_set_val, gen_statistic_data)

# case 2: The /share/CACHEDEV1_DATA1/.disk_data will be created automatically if default volume is exist.
--> follow case 4 and case 5

# case 3: increase ata err count can work properly.
/root/hal_app --pd_inc_ata_errcnt value=BTLA721307LM256CGN:16:2

# case 4: iotest set val can work properly.
/root/hal_app --pd_set_ata_iotest_val value=BTLA721307LM256CGN:201:9:10

# case 5: get_statistic_data can work properly 
/root/hal_app --pd_get_disk_statistic_data enc_id=0,port_id=5,value=201
