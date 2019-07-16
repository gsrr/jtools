import sys
import os
import diskinfo
import time
import traceback

global gloc

def exec_remote_cmd(user, ip, cmd):
    print (cmd)
    rcmd = 'ssh %s@%s "%s"'%(user, ip, cmd)
    os.system(rcmd)

def exec_cmd(cmd):
    print (cmd)
    os.system(cmd)

def _mount_dom(user, ip):
    global gloc
    diskinfo.remote_get_diskinfo(user, ip)
    dom = diskinfo.gdiskinfo['dom'][0]
    cnt = 0
    while True:
        try:
            gloc = "update%d"%cnt
            path = "/mnt_%s/root/%s"%(ip, gloc)
            os.mkdir(path)
            for i in xrange(1, 6):
                mpath = "%s/%d"%(path, i)
                os.mkdir(mpath)
                cmd = "mount %s%d /root/%s/%d"%(dom, i, gloc, i)
                exec_remote_cmd(user, ip, cmd)
            break
        except:
            print (traceback.format_exc())
        cnt += 1
        time.sleep(1)

def mount_dom():
    user = sys.argv[1] 
    ip = sys.argv[2] 
    _mount_dom(user, ip)
    return 0

def _do_update_kernel(model, source, dst):
    global gloc
    source = source + "/NasX86/Model/%s"%(model)
    for i in [2, 3]:
        for name in ['bzImage', 'bzImage.cksum']:
            tsrc = source + "/build/" + name
            tdst = dst + "/root/%s/%d/boot/%s"%(gloc, i, name)
            cmd = "rsync %s %s"%(tsrc, tdst)
            exec_cmd(cmd)

def _do_update(model, source, dst, items):
    for it in items:
        func = getattr(sys.modules[__name__], "_do_update_%s"%it)
        func(model, source, dst)

def do_update():
    return _do_update("TS-X71", "/mnt_172.17.22.179/home/root/working/jerry_alpha/", "/mnt_172.17.22.121/", ["kernel"])

def main():
    cmds = [
        'mount_dom',
        'do_update',
    ]
    for cmd in cmds:
        print("[%s]"%cmd)
        func = getattr(sys.modules[__name__], cmd)
        ret = func()
        if ret != 0:
            break


if __name__ == "__main__":
    main()
