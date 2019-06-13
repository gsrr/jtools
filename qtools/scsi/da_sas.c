
#include "da_sas.h"


void dump_datainfo(struct datainfo *dinfo)
{
    int i;
    for(i = 0 ; i < SAS_FUNC_NUM ; i++)
    {
        printf("(template, op, length) = (%d, %02x, %d)\n", dinfo[i].temp_num, dinfo[i].op, dinfo[i].len);
    }
}

void dump_buf_to_file(int fd, char *buf, int blen)
{
    write(fd, buf, blen);
}

void dump_log_page_buffer(char *buf)
{
    int i;
    int page_base = 4;
    int page_length = PAGE_LEN_COMB(buf[2], buf[3]);
    printf("page header: ");
    for(i = 0 ; i < 4 ; i++)
    {
        printf("%x ", buf[i] & 0xff);
    }
    printf("\n");
    int j = page_base;
    while(j < (page_length + page_base))
    {
        int parm_base = j + 4;
        int parm_len = buf[j + 3];
        for(j ; j < parm_base ; j++)
        {
            printf("%x ", buf[j] & 0xff);
        }
        printf("\n");
        for(j ; j < (parm_base + parm_len) ; j++)
        {
            printf("%02x ", buf[j] & 0xff);
        }
        printf("\n");
    }
    
}

void dump_vpd_buffer(char *p)
{
    int i;
    for(i = 0 ; i < 4 ; i++)
    {
        printf("%x\n", p[i] & 0xff);
    }
    for(i = 4 ; i < p[3] ; i++)
    {
        printf("%x ", p[i] & 0xff);
    }
    printf("\n");
    for(i = 0 ; i < p[3] ; i++)
    {
        printf("%c ", p[i + 4]);
    }
    printf("\n");

}

int send_scsi_command(int sg_fd, struct scsi_paras *sparas)
{
    unsigned char sense_buffer[32];
    sg_io_hdr_t io_hdr;

    memset(&io_hdr, 0, sizeof(sg_io_hdr_t));
    io_hdr.interface_id = 'S';
    io_hdr.cmd_len = sparas->cmd_len;
    io_hdr.mx_sb_len = sizeof(sense_buffer);
    io_hdr.dxfer_direction = SG_DXFER_FROM_DEV;
    io_hdr.dxfer_len = sparas->buf_len;
    io_hdr.dxferp = sparas->buf;
    io_hdr.cmdp = sparas->cmd;
    io_hdr.sbp = sense_buffer;
    io_hdr.timeout = 20000;     /* 20000 millisecs == 20 seconds */

    if (ioctl(sg_fd, SG_IO, &io_hdr) < 0) {
        perror("sg_simple0: Inquiry SG_IO ioctl error");
        return -1;
    }
    
    if ((io_hdr.info & SG_INFO_OK_MASK) != SG_INFO_OK) 
    {
        return -1;
    }
    return 0;
}

void gen_log_sense_cmd(unsigned char *cmd, unsigned char op, int len)
{
    cmd[0] = LOG_SENSE_CMD_CODE;
    cmd[1] = 0x00;
    cmd[2] = 0x40 | op;
    cmd[3] = 0x00;
    cmd[4] = 0x00;
    cmd[5] = 0x00;
    cmd[6] = 0x00;
    cmd[7] = 0xff & (LOG_SENSE_REPLY_LEN >> 8);
    cmd[8] = 0xff & LOG_SENSE_REPLY_LEN;
    cmd[9] = 0x00;
}

void get_sup_pages(int sg_fd)
{
    int i, ret, plen;
    unsigned char cmd[LOG_SENSE_CMD_LEN];
    unsigned char buf[LOG_SENSE_REPLY_LEN];
    struct scsi_paras sparas;
    
    gen_log_sense_cmd(cmd, 0x00, LOG_SENSE_REPLY_LEN);

    sparas.buf = buf;
    sparas.buf_len = LOG_SENSE_REPLY_LEN;
    sparas.cmd = cmd;
    sparas.cmd_len = LOG_SENSE_CMD_LEN;
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("get support pages fail : %d\n", ret);
        return;
    }

    plen = PAGE_LEN_COMB(buf[2], buf[3]);
    sup_pages = malloc(sizeof(unsigned char) * plen);
    printf("support pages: ");
    for(i = 0 ; i < plen ; i++)
    {
        sup_pages[i] = buf[4 + i];
        printf("%02x ", sup_pages[i]);
    }
    printf("\n");
    len_sup_pages = plen;
}

int is_support(unsigned char op, unsigned char *sup, int len)
{
    int i;
    for(i = 0 ; i < len ; i++)
    {
        if(sup[i] == op)
        {
            return 0;
        }
    }
    return -1;
}

int send_log_sense_command(int sg_fd, unsigned char op, int data_fd)
{
    int len = -1;
    int ret;
    unsigned char cmd[LOG_SENSE_CMD_LEN];
    unsigned char buf[LOG_SENSE_REPLY_LEN];
    struct scsi_paras sparas;
    int i;
    
    if(is_support(op, sup_pages, len_sup_pages) != 0)
    {
        printf("Log sense page: This opcode is not supported : %02x\n", op);
        return -2;
    }

    gen_log_sense_cmd(cmd, op, LOG_SENSE_REPLY_LEN);

    sparas.buf = buf;
    sparas.buf_len = LOG_SENSE_REPLY_LEN;
    sparas.cmd = cmd;
    sparas.cmd_len = LOG_SENSE_CMD_LEN;
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("send_log_sense_command fail : (%d, %d)\n", op, ret);
        return -1;
    }
    len = 4 + PAGE_LEN_COMB(buf[2], buf[3]);
    dump_buf_to_file(data_fd, buf, len);
    return len;
}

void gen_inquiry_vpd_cmd(unsigned char *cmd, unsigned char op, int len)
{
    cmd[0] = INQ_CMD_CODE;
    cmd[1] = 0x01;
    cmd[2] = op;
    cmd[3] = 0xff & (len >> 8);
    cmd[4] = 0xff & len;
    cmd[5] = 0x00;
}

void get_sup_vpds(int sg_fd)
{
    int i, ret, plen;
    unsigned char cmd[INQ_CMD_LEN];
    unsigned char buf[INQ_REPLY_LEN];
    struct scsi_paras sparas;
    
    gen_inquiry_vpd_cmd(cmd, 0x00, sizeof(buf));

    sparas.buf = buf;
    sparas.buf_len = sizeof(buf);
    sparas.cmd = cmd;
    sparas.cmd_len = sizeof(cmd);
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("get support vpds fail : %d\n", ret);
        return;
    }

    plen = buf[3];
    sup_vpds = malloc(sizeof(unsigned char) * plen);
    printf("support vpds: ");
    for(i = 0 ; i < plen ; i++)
    {
        sup_vpds[i] = buf[4 + i];
        printf("%02x ", sup_vpds[i]);
    }
    printf("\n");
    len_sup_vpds = plen;
}

int send_inquiry_vpd_command(int sg_fd, unsigned char op, int data_fd)
{
    int len = -1;
    int ret;
    unsigned char cmd[INQ_CMD_LEN];
    unsigned char buf[INQ_REPLY_LEN];
    struct scsi_paras sparas;
    int i;
    
    if(is_support(op, sup_vpds, len_sup_vpds) != 0)
    {
        printf("Inquiry VPD: This opcode is not supported : %02x\n", op);
        return -2;
    }

    gen_inquiry_vpd_cmd(cmd, op, sizeof(buf));

    sparas.buf = buf;
    sparas.buf_len = sizeof(buf);
    sparas.cmd = cmd;
    sparas.cmd_len = sizeof(cmd);
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("send_inquiry_vpd_command fail : (%d, %d)\n", op, ret);
        return -1;
    }
    len = 4 + buf[3];
    dump_buf_to_file(data_fd, buf, len);
    return len;
}

/*

void browse_read_funcs(char *dev, struct datainfo *dinfo)
{


    int sg_fd;
    if ((sg_fd = open(dev, O_RDONLY)) < 0) {
        perror("error opening given file name");
        return;
    }
    //send_read_command(sg_fd, cmd1, READ_CAPACITY_10_CMD_LEN, READ_CAPACITY_10_REPLY_LEN); 
    unsigned char buf[READ_DEFECT_DATA_12_REPLY_LEN];
    //unsigned char buf[READ_CAPACITY_16_REPLY_LEN];
    send_read_command(sg_fd, cmd, buf, sizeof(cmd), sizeof(buf)); 
    close(sg_fd);
}
*/

int send_read_capacity_10(int sg_fd, unsigned char op, int data_fd)
{
    int ret = -1;
    int len = -1; 
    struct scsi_paras sparas;
    unsigned char buf[READ_CAPACITY_10_REPLY_LEN];
    unsigned char cmd[READ_CAPACITY_10_CMD_LEN] = {
        READ_CAPACITY_10, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
    };
    sparas.buf = buf;
    sparas.buf_len = sizeof(buf);
    sparas.cmd = cmd;
    sparas.cmd_len = sizeof(cmd);
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("send_read_capacity_10 fail: (%d, %d)\n", op, ret);
        return -1;
    }
    len = sizeof(buf);
    dump_buf_to_file(data_fd, buf, len);
    return len;
}

int send_read_capacity_16(int sg_fd, unsigned char op, int data_fd)
{
    int ret = -1;
    int len = -1; 
    struct scsi_paras sparas;
    unsigned char buf[READ_CAPACITY_16_REPLY_LEN];
    unsigned char cmd[READ_CAPACITY_16_CMD_LEN] = {
        READ_CAPACITY_16, 
        0x10, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x00, 
        0x20, 
        0x00, 
        0x00, 
    };
    sparas.buf = buf;
    sparas.buf_len = sizeof(buf);
    sparas.cmd = cmd;
    sparas.cmd_len = sizeof(cmd);
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("send_read_capacity_16 fail: (%d, %d)\n", op, ret);
        return -1;
    }
    len = sizeof(buf);
    dump_buf_to_file(data_fd, buf, len);
    return len;
}

void gen_read_defect_data_12_cmd_and_buf(unsigned char *cmd, int index, int reply_len)
{
    cmd[0] = READ_DEFECT_DATA_12;
    cmd[1] = 0x14; //0x0c
    cmd[2] = 0xff & (index >> 24);
    cmd[3] = 0xff & (index >> 16);
    cmd[4] = 0xff & (index >> 8);
    cmd[5] = 0xff & (index >> 0);
    cmd[6] = 0xff & (reply_len >> 24);
    cmd[7] = 0xff & (reply_len >> 16);
    cmd[8] = 0xff & (reply_len >> 8);
    cmd[9] = 0xff & (reply_len >> 0);
    cmd[10] = 0x00;
    cmd[11] = 0x00;
    cmd[12] = 0x00;
    
}

int dump_defect_data_length(int sg_fd, int data_fd)
{
    int ret = -1;
    int len = -1; 
    int reply_len = READ_DEFECT_DATA_12_REPLY_LEN;
    struct scsi_paras sparas;
    unsigned char buf[reply_len];
    unsigned char cmd[READ_DEFECT_DATA_12_CMD_LEN];

    gen_read_defect_data_12_cmd_and_buf(cmd, 0, reply_len);
     
    sparas.buf = buf;
    sparas.buf_len = reply_len;
    sparas.cmd = cmd;
    sparas.cmd_len = sizeof(cmd);
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("get_defect_data_length fail: %d\n", ret);
        return -1;
    }
    len = DEFECT12_LEN_COMB(buf[4], buf[5], buf[6], buf[7]);
    dump_buf_to_file(data_fd, buf, reply_len);
    return len;
}

int send_read_defect_data_12_partial(int sg_fd, int data_fd, int index, unsigned char *buf, int buf_len)
{
    int ret = -1;
    struct scsi_paras sparas;
    unsigned char cmd[READ_DEFECT_DATA_12_CMD_LEN];

    gen_read_defect_data_12_cmd_and_buf(cmd, index, buf_len);
     
    sparas.buf = buf;
    sparas.buf_len = buf_len;
    sparas.cmd = cmd;
    sparas.cmd_len = sizeof(cmd);
    ret = send_scsi_command(sg_fd, &sparas);
    if (ret != 0)
    {
        printf("get_defect_data_length fail: (index, ret) = (%d, %d)\n", index, ret);
        return -1;
    }
    return 0;
    
}

int dump_defect_data_list(int sg_fd, int data_fd, int total_adds)
{
    unsigned char buf[READ_DEFECT_DATA_12_BUFFER] = {0};
    int buf_adds = READ_DEFECT_DATA_12_BUFFER / 8;
    int index = 0;
    int ret;
    int dump_bytes = READ_DEFECT_DATA_12_BUFFER;
    int total_bytes = 0;

    while (index < total_adds)
    {
        ret = send_read_defect_data_12_partial(sg_fd, data_fd, index, buf, READ_DEFECT_DATA_12_BUFFER);
        if(ret != 0)
        {
            break;
        }
        if((index + buf_adds) >= total_adds)
        {
            dump_bytes = (total_adds - index) * 8;
        }
        dump_buf_to_file(data_fd, buf, dump_bytes);
        index += buf_adds;
        total_bytes += dump_bytes;
        printf("(index, total_adds, dump, total) = (%d, %d, %d, %d)\n", index, total_adds, dump_bytes, total_bytes);
    }
    printf("(index, total_adds, dump, total) = (%d, %d, %d, %d)\n", index, total_adds, dump_bytes, total_bytes);
}

int send_read_defect_data_12(int sg_fd, unsigned char op, int data_fd)
{
    int ret = -1;
    int len = -1; 
    int llen = -1;
    llen = dump_defect_data_length(sg_fd, data_fd);
    if(llen < 0)
    {
        printf("send_read_capacity_16 fail(get list length): (%d, %d)\n", op, llen);
    }
    printf("get defect list length : (bytes, blocks) = (%d, %d)\n", llen, llen/8);
    ret = dump_defect_data_list(sg_fd, data_fd, llen/8);
    len = 8 + llen;
    return len;
}

void browse_all_funcs(int sg_fd, struct datainfo *dinfo, int data_fd)
{
    int i, len;

    for(i = 0 ; i < SAS_FUNC_NUM ; i++)
    {
        dinfo[i].temp_num = funcs[i].temp_num;
        dinfo[i].op = funcs[i].opcode;
        dinfo[i].len = funcs[i].func(sg_fd, funcs[i].opcode, data_fd);
    }
    dump_datainfo(dinfo);
}

void da_gen_sas_data_file(int sg_fd, int enc_id, int port_id)
{
    int i, data_fd;
    char fpath[512] = {0};
    struct datainfo dinfo[SAS_FUNC_NUM];
    
    sprintf(fpath,  "/tmp/smart/disk_data_%d_%d", enc_id, port_id);
    data_fd = open(fpath, O_CREAT | O_WRONLY, 0644);
    memset(dinfo, 0, sizeof(struct datainfo) * SAS_FUNC_NUM);

    get_sup_pages(sg_fd);
    get_sup_vpds(sg_fd);
     
    browse_all_funcs(sg_fd, dinfo, data_fd);
    /*
    browse_page_funcs(sg_fd, &dinfo[offset]);
    offset += SAS_PAGE_FUNC_NUM;
    browse_vpd_funcs(dev, &dinfo[offset]);
    offset += SAS_FUNC_NUM;
    browse_read_funcs(dev, &dinfo[offset]);
    dump_datainfo(dinfo, totalnum);
    */
    close(data_fd);
}

int main(int argc, char * argv[])
{
    if (2 != argc) {
        printf("Usage: 'sg_simple0 <sg_device>'\n");
        return 1;
    }
    int sg_fd;

    if ((sg_fd = open(argv[1], O_RDONLY)) < 0) {
        perror("error opening given file name");
    }

    da_gen_sas_data_file(sg_fd, 0, 1); //enc_id, port_id
    close(sg_fd);
    return 0;
}
