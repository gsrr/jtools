#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <scsi/sg.h> /* take care: fetches glibc's /usr/include/scsi/sg.h */


#define PAGE_LEN_COMB(v1, v2) ((v1 & 0xff) << 8) | (v2 & 0xff)
#define DEFECT12_LEN_COMB(v1, v2, v3, v4) ((v1 & 0xff) << 24) | ((v2 & 0xff) << 16) | ((v3 & 0xff) << 8) | (v4 & 0xff)


#define INQ_REPLY_LEN 96
#define INQ_CMD_CODE 0x12
#define INQ_CMD_LEN 6

#define LOG_SENSE_REPLY_LEN 65535
#define LOG_SENSE_SUPPORT_REPLAY_LEN 256
#define LOG_SENSE_CMD_CODE 0x4D
#define LOG_SENSE_CMD_LEN 10

#define READ_CAPACITY_10_CMD_LEN 10
#define READ_CAPACITY_10_REPLY_LEN 8
#define READ_CAPACITY_10 0x25

#define READ_CAPACITY_16_CMD_LEN 16
#define READ_CAPACITY_16_REPLY_LEN 32
#define READ_CAPACITY_16 0x9E

#define READ_DEFECT_DATA_12_CMD_LEN 12
#define READ_DEFECT_DATA_12_REPLY_LEN 8
#define READ_DEFECT_DATA_12 0xB7
#define READ_DEFECT_DATA_12_BUFFER 65536

#define VPD_PAGE_Unit_Serial_Number 0x80
#define VPD_PAGE_Device_Identification 0x83
#define VPD_PAGE_Extended_INQUIRY_Data 0x86
#define VPD_PAGE_Mode_Page_Policy 0x87
#define VPD_PAGE_SCSI_Ports 0x88
#define VPD_PAGE_Protocol_Specific_Logical_Unit_Information 0x90
#define VPD_PAGE_Protocol_Specific_Port_Information 0x91
#define VPD_PAGE_Block_Limits 0xb0
#define VPD_PAGE_Block_Device_Characteristics 0xb1
#define PAGE_CODE_WRITE_ERROR_COUNTER   0x02
#define PAGE_CODE_READ_ERROR_COUNTER   0x03
#define PAGE_CODE_VERIFY_ERROR_COUNTER   0x05
#define PAGE_CODE_NON_MEDIUM_ERROR   0x06
#define PAGE_CODE_FORMAT_STATUS   0X08
#define PAGE_CODE_TEMPERATURE   0X0D
#define PAGE_CODE_START_STOP_CYCLE_COUNTER   0X0E
#define PAGE_CODE_APPLICATION_CLIENT   0X0F
#define PAGE_CODE_SELF_TEST_RESULT   0X10
#define PAGE_CODE_SOLID_STATE_MEDIA   0X11
#define PAGE_CODE_BACKGROUND_SCAN_RESULTS   0X15
#define PAGE_CODE_NON_VOLATILE_CACHE   0X17
#define PAGE_CODE_PROTOCOL_SPECIFIC_PORT   0X18
#define PAGE_CODE_GENERAL_STATISTICS_AND_PERFORMANCE   0X19
#define PAGE_CODE_INFORMATIONAL_EXCEPTIONS   0X2F

struct scsi_paras {
    char *buf;
    int buf_len;
    unsigned char *cmd;
    int cmd_len;
};

struct datainfo {
    int len;
    int temp_num;
    unsigned char op;
};

struct sasfunc {
    unsigned char opcode;
    int temp_num;
    int (*func)(int sg_fd, unsigned char op, int data_fd); 
};

int send_log_sense_command(int sg_fd, unsigned char op, int data_fd);
int send_inquiry_vpd_command(int sg_fd, unsigned char op, int data_fd);
int send_read_capacity_10(int sg_fd, unsigned char op, int data_fd);
int send_read_capacity_16(int sg_fd, unsigned char op, int data_fd);
int send_read_defect_data_12(int sg_fd, unsigned char op, int data_fd);

#define SAS_FUNC_NUM 27

struct sasfunc funcs[SAS_FUNC_NUM] = {
    {PAGE_CODE_WRITE_ERROR_COUNTER, 301, send_log_sense_command},
    {PAGE_CODE_READ_ERROR_COUNTER, 302, send_log_sense_command},
    {PAGE_CODE_VERIFY_ERROR_COUNTER, 303, send_log_sense_command},
    {PAGE_CODE_NON_MEDIUM_ERROR, 304, send_log_sense_command},
    {PAGE_CODE_FORMAT_STATUS, 305, send_log_sense_command},
    {PAGE_CODE_TEMPERATURE, 306, send_log_sense_command},
    {PAGE_CODE_START_STOP_CYCLE_COUNTER, 307, send_log_sense_command},
    {PAGE_CODE_APPLICATION_CLIENT, 308, send_log_sense_command},
    {PAGE_CODE_SELF_TEST_RESULT, 309, send_log_sense_command},
    {PAGE_CODE_SOLID_STATE_MEDIA, 310, send_log_sense_command},
    {PAGE_CODE_BACKGROUND_SCAN_RESULTS, 311, send_log_sense_command},
    {PAGE_CODE_NON_VOLATILE_CACHE, 312, send_log_sense_command},
    {PAGE_CODE_PROTOCOL_SPECIFIC_PORT, 313, send_log_sense_command},
    {PAGE_CODE_GENERAL_STATISTICS_AND_PERFORMANCE, 314, send_log_sense_command},
    {PAGE_CODE_INFORMATIONAL_EXCEPTIONS, 315, send_log_sense_command},
    {VPD_PAGE_Unit_Serial_Number, 320, send_inquiry_vpd_command},
    {VPD_PAGE_Device_Identification, 321, send_inquiry_vpd_command},
    {VPD_PAGE_Extended_INQUIRY_Data, 322, send_inquiry_vpd_command},
    {VPD_PAGE_Mode_Page_Policy, 323, send_inquiry_vpd_command},
    {VPD_PAGE_SCSI_Ports, 324, send_inquiry_vpd_command},
    {VPD_PAGE_Protocol_Specific_Logical_Unit_Information, 325, send_inquiry_vpd_command},
    {VPD_PAGE_Protocol_Specific_Port_Information, 326, send_inquiry_vpd_command},
    {VPD_PAGE_Block_Limits, 327, send_inquiry_vpd_command},
    {VPD_PAGE_Block_Device_Characteristics, 328, send_inquiry_vpd_command},
    {READ_CAPACITY_10, 330, send_read_capacity_10},
    {READ_CAPACITY_16, 331, send_read_capacity_16},
    {READ_DEFECT_DATA_12, 332, send_read_defect_data_12},
};
int len_sup_pages = 0;
unsigned char *sup_pages;

int len_sup_vpds = 0;
unsigned char *sup_vpds;


