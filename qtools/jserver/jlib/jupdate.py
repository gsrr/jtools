import configparser
import sys
import os
import time
import traceback

class JUpdate:
    def __init__(self):
        self.cfg = None
        self.conf = "/etc/jupdate.conf"

    def read_conf(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(self.conf)
    
    def show_options(self):
        opts = [
            'hal',
            'hal_util',
            'kernel'
        ]
        for opt in opts:
            print(opt)

    def update_kernel(self):
        pass

'''
def exec_remote_cmd(user, ip, cmd):
    print (cmd)
    rcmd = 'ssh %s@%s "%s"'%(user, ip, cmd)
    return os.system(rcmd)

def exec_cmd(cmd):
    print (cmd)
    return os.system(cmd)

def get_dom_dev(devs):
    if len(devs) > 0:
        return devs[0]
    return raw_input("Can not find dom device, input manually:")

def _mount_dom(user, ip):
    global gloc
    diskinfo.remote_get_diskinfo(user, ip)
    dom = get_dom_dev(diskinfo.gdiskinfo['dom'])
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
    qts = jconf.get_qts()
    _mount_dom(qts['user'], qts['host'])
    return 0

def _do_update_kernel(model, source, dst):
    global gloc
    ret = -1
    source = source + "/NasX86/Model/%s"%(model)
    for i in [2, 3]:
        for name in ['bzImage', 'bzImage.cksum']:
            tsrc = source + "/build/" + name
            tdst = dst + "/root/%s/%d/boot/%s"%(gloc, i, name)
            cmd = "rsync %s %s"%(tsrc, tdst)
            ret = exec_cmd(cmd)
    return ret

def initrd_backup(path):
    size = os.path.getsize(path)/10**6
    if size < 20:
        return -1
    print("size of initrd.boot = %dM"%size)
    exec_cmd("rsync -a %s /tmp/backup/"%path)
    return 0

def unzip_initrd(dst):
    global gloc
    tmp = dst + "/root/%s/2/boot/initrd.boot"%gloc
    if initrd_backup(tmp) != 0:
        return -1
    if os.path.exists("/tmp/initrd"):
        exec_cmd("rm -rf /tmp/initrd*")
    os.mkdir("/tmp/initrd")
    exec_cmd("rsync -a %s /tmp/initrd/"%tmp)
    os.chdir("/tmp/initrd")  
    exec_cmd("xz -dc initrd.boot | cpio -id")
    exec_cmd("rm initrd.boot")
    return 0

def zip_and_copy_initrd(dst):
    os.chdir("/tmp/initrd")  
    exec_cmd("find . | sudo cpio -H newc -o  | lzma -9 > ../initrd.boot; cd ..; cksum initrd.boot > initrd.boot.cksum")
    os.chdir("/tmp")  
    for i in [2, 3]:
        idst = dst + "/root/%s/%d/boot/"%(gloc, i)
        for name in ["initrd.boot", "initrd.boot.cksum"]:
            tsrc = "/tmp/" + name
            tdst = idst + "/" + name
            cmd = "rsync --inplace %s %s"%(tsrc, tdst)
            exec_cmd(cmd)
        

def _do_update_hal_util(model, source, dst):
    global gloc
    if unzip_initrd(dst) != 0:
        return -1
    source = source + "/NasX86/NasUtil/hal_util/"
    for f in ["/sbin/hal_util"]:
        tsrc = source + os.path.basename(f)
        tdst = "/tmp/initrd/" + f
        cmd = "rsync %s %s"%(tsrc, tdst)
        exec_cmd(cmd)
    zip_and_copy_initrd(dst)
    return 0

def _do_update_hal(model, source, dst):
    global gloc
    if unzip_initrd(dst) != 0:
        return -1

    source = source + "/NasX86/NasLib/hal/"
    for f in ["/lib/libuLinux_hal.so", "/sbin/hal_app"]:
        tsrc = source + os.path.basename(f)
        tdst = "/tmp/initrd/" + f
        cmd = "rsync %s %s"%(tsrc, tdst)
        exec_cmd(cmd)
    zip_and_copy_initrd(dst)
    return 0

def _do_update(model, source, dst, items):
    for it in items:
        func = getattr(sys.modules[__name__], "_do_update_%s"%it)
        if func(model, source, dst) != 0:
            print ("Fail to _do_update")
            break

def do_update(items):
    #_do_update("TS-X71", "/mnt_172.17.22.179/home/root/working/jerry_alpha/", "/mnt_172.17.22.121/", ["kernel"])
    #return _do_update("TS-X71", "/mnt_172.17.22.179/home/root/working/jerry_alpha_test/", "/mnt_172.17.22.206/", ["hal"])
    qts = jconf.get_qts()
    bs = jconf.get_build_server()
    return _do_update(qts['model'], "/mnt_%s/%s/%s/"%(bs['host'], bs['working_dir'], bs['build_dir']), "/mnt_%s/"%(qts['host']), items)

def get_opts(options):
    ret = []
    for i in xrange(len(options)):
        print i + 1, ":", options[i]

    opts = raw_input("Please enter your option (ex: 1,2,3) :")
    for opt in opts.split(","):
        opt = opt.strip()
        ret.append(options[int(opt) - 1])
    return ",".join(ret)
    

def main():
    options = ["kernel", "hal", "hal_util"]
    opts = get_opts(options)
    mount_dom()
    cmds = [
        'do_update',
    ]
    for cmd in cmds:
        func = getattr(sys.modules[__name__], cmd)
        ret = func(opts.split(","))
        if ret != 0:
            break
'''

def main2():
    obj = JUpdate()
    obj.read_conf()
    obj.show_options()


if __name__ == "__main__":
    main2()
