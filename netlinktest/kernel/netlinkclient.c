#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/netlink.h>
#include <net/netlink.h>
#include <net/net_namespace.h>
#include <linux/delay.h>

/* Protocol family, consistent in both kernel prog and user prog. */
#define MYPROTO NETLINK_USERSOCK
/* Multicast group, consistent in both kernel prog and user prog. */
#define MYGRP 21

static struct sock *nl_sk = NULL;

static int send_to_user(char* msg)
{
    struct sk_buff *skb;
    struct nlmsghdr *nlh;
    int msg_size = strlen(msg) + 1;
    int res;

    skb = nlmsg_new(NLMSG_ALIGN(msg_size + 1), GFP_KERNEL);
    if (!skb) {
        pr_err("Allocation failure.\n");
        return -1;
    }

    nlh = nlmsg_put(skb, 0, 1, NLMSG_DONE, msg_size + 1, 0);
    strcpy(nlmsg_data(nlh), msg);

    res = nlmsg_multicast(nl_sk, skb, 0, MYGRP, GFP_KERNEL);
    if (res < 0)
    {
        pr_info("nlmsg_multicast() error: %d, msg=%s\n", res, msg);
        return -1;
    }
    else
    {
        return 0;
    }
}

static int __init hello_init(void)
{
    int i;
    char msg[1024] = {0};
    int ret;
    int cnt;

    nl_sk = netlink_kernel_create(&init_net, MYPROTO, NULL);
    if (!nl_sk) {
        pr_err("Error creating socket.\n");
        return -10;
    }

    for(i = 0 ; i < 5000 ; i++)
    {
        cnt = 0;
        sprintf(msg, "SCSI_CMD_ERROR;%d,param1,param2", i);
        while(cnt < 3)
        {
            ret = send_to_user(msg);
            if(ret != 0)
            {
                cnt += 1;
                msleep(1000);
            }
            else
                break;
        }
    }

    netlink_kernel_release(nl_sk);
    return 0;
}

static void __exit hello_exit(void)
{
    pr_info("Exiting hello module.\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
