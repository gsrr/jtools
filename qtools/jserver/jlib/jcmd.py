def exec_cmds(cmds, paras):
    for cmd in cmds:
        ret = cmd(paras)
        print (ret, cmd)
        if ret != 0:
            break
    print (paras)
