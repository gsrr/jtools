#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <unistd.h>
#include <dirent.h>

#define MYPROTO NETLINK_USERSOCK
#define MYMGRP 21

#define EVENT_DIR   "/etc/events"

int open_netlink(void)
{
    int sock;
    struct sockaddr_nl addr;
    int group = MYMGRP;

    sock = socket(AF_NETLINK, SOCK_RAW, MYPROTO);
    if (sock < 0) {
        printf("sock < 0.\n");
        return sock;
    }

    memset((void *) &addr, 0, sizeof(addr));
    addr.nl_family = AF_NETLINK;
    addr.nl_pid = getpid();

    if (bind(sock, (struct sockaddr *) &addr, sizeof(addr)) < 0) {
        printf("bind < 0.\n");
        return -1;
    }

    /*
     * 270 is SOL_NETLINK. See
     * http://lxr.free-electrons.com/source/include/linux/socket.h?v=4.1#L314
     * and
     * http://stackoverflow.com/questions/17732044/
     */
    if (setsockopt(sock, SOL_NETLINK, NETLINK_ADD_MEMBERSHIP, &group, sizeof(group)) < 0) {
        printf("setsockopt < 0\n");
        return -1;
    }

    return sock;
}

void fork_exec(char *cmd, char *params)
{
    //printf("%s, %s, %s\n", __func__, cmd, params);
    pid_t p;
    int ret;

    p = fork();
    if(p == 0)
    {
        char *args[] = {cmd, params, NULL};
        ret = execv(cmd, args);
        printf("%s, %d\n", __func__, ret);
    }
}

void call_register_fork(char *edir, char *params)
{
    DIR *dir;
    struct dirent *entry;
    char cmd[512] = {0};

    if ((dir = opendir(edir)) == NULL)
    {
        return;
    }

    while ((entry = readdir(dir)) != NULL)
    {
        if(strcmp(".", entry->d_name) == 0 || strcmp("..", entry->d_name) == 0)
            continue;

        snprintf(cmd, sizeof(cmd), "%s/%s", edir, entry->d_name); 
        fork_exec(cmd, params);
    }
}

void dispatch_event(char *buffer)
{
    char* event;
    char* params;
    char edir[256] = {0};

    printf("%s, %s\n", __func__, buffer);
    event = strtok_r(buffer, ";", &params);

    snprintf(edir, sizeof(edir), "%s/%s", EVENT_DIR, event);
    call_register_fork(edir, params);
}

/*
 * event:param1,param2,...
*/
void read_event(int sock)
{
    struct sockaddr_nl nladdr;
    struct msghdr msg;
    struct iovec iov;
    char buffer[8192];
    int ret;

    iov.iov_base = (void *) buffer;
    iov.iov_len = sizeof(buffer);
    msg.msg_name = (void *) &(nladdr);
    msg.msg_namelen = sizeof(nladdr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    ret = recvmsg(sock, &msg, 0);
    if (ret < 0)
        perror("Error: ");
    else
    {
        dispatch_event(NLMSG_DATA((struct nlmsghdr *) buffer));
    }
}

int main(int argc, char *argv[])
{
    int nls;

    nls = open_netlink();
    if (nls < 0)
        return nls;

    system("rm -rf /tmp/test.log");
    printf("listening...\n");
    while (1)
        read_event(nls);

    return 0;
}
