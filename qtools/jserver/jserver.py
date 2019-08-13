import time
import sys
import socket
import os
import glob
import xml.etree.cElementTree as ET
import subprocess
from jlib import jconf 


def get_patch_path():
    local = jconf.get_local()
    return '%s/patches/%s'%(local['jserver_path'], sys.argv[2])

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.settimeout(20)
    while True:
        result = sock.connect_ex(('172.17.22.116', port))
        if result == 0:
           print ("Port is open")
           break
        else:
           print ("Port is not open")
        time.sleep(1)
    sock.close()

def gen_expect_temp(cmd, pwd):
    fw = open("exec.exp", "w")
    with open("template.exp", "r") as fr:
        lines = fr.readlines()
        for line in lines:
            if "execcmd" in line:
                line = line.replace("[execcmd]", cmd)
            elif "password" in line:
                line = line.replace("[password]", pwd)
            fw.write(line)
    fw.close()

def copy_ssh_id(host, sect):
    cmd = "ssh-copy-id %s@%s"%(sect['user'], host)
    gen_expect_temp(cmd, sect['password'])
    os.system("expect exec.exp")

def is_mnt_exist(mpath):
    with open("/etc/mtab", "r") as fr:
        lines = fr.readlines()
        for line in lines:
            items = line.split()
            if mpath == items[1]:
                return True
    return False

def mount_host(host, sect):
    mpath = "/mnt_%s"%host
    if is_mnt_exist(mpath) == True:
        return
    if os.path.exists(mpath) == False:
        os.mkdir(mpath)
    cmd = "sshfs %s@%s:/ /%s/"%(sect['user'], host, mpath)
    print (cmd)
    os.system(cmd)

def init_remote_client(*paras):
    funcs = [
        copy_ssh_id,
        mount_host,
    ]
    for f in funcs:
        f(*paras)

def rm_redund_mnt():
    mnts = glob.glob("/mnt_*")
    for m in mnts:
        if is_mnt_exist(m) == True:
            continue
        os.rmdir(m)

def init():
    gconf = jconf.gconfig
    for section in gconf.sections():
        if section == "local":
            continue
        host = gconf[section]['host']
        init_remote_client(host.strip(), gconf[section])
    rm_redund_mnt()

def get_start_end_commid(repo):
    cmd = "git reflog show --no-abbrev %s"%repo
    lines = subprocess.getoutput(cmd).splitlines()
    return (lines[0].split()[0], lines[-1].split()[0])

# or "git diff $start..."
def gen_patch_cmd(repo):
    commid_end, commid_start = get_start_end_commid(repo)
    cmd = "git diff %s..%s"%(commid_start, commid_end)
    return cmd

# python3 gen_commit_patch 1 (1 stands for bug number)
def gen_commit_patch():
    lconfig = jconf.get_local()
    fpath = '%s/patches/%s'%(lconfig['jserver_path'], sys.argv[2])
    tree = ET.ElementTree(file='%s/manifest'%fpath)
    root = tree.getroot()
    src = root.attrib['src']
    basedir = os.getcwd()
    for proj in root:
        print (proj.tag, proj.attrib)
        src_repo = "%s/%s"%(src, proj.attrib['name'])
        tmpdir = os.getcwd()
        os.chdir(src_repo)
        cmd = gen_patch_cmd(proj.attrib['revision'])
        print ("\tgenerate patch : %s"%(os.getcwd()))
        os.system("%s > %s/%s.patch"%(cmd, fpath, proj.attrib['name']))
        os.chdir(tmpdir)

def gen_patch_cmd_with_remote(repo):
    cmd = "git diff origin/%s..HEAD"%repo
    return cmd

# python3 gen_commit_patch_with_remote 1 (1 stands for bug number)
def gen_commit_patch_with_remote():
    fpath = os.path.abspath('patches/%s'%sys.argv[2])
    tree = ET.ElementTree(file='%s/manifest'%fpath)
    root = tree.getroot()
    src = "/mnt_%s"%root.attrib['src']
    basedir = os.getcwd()
    for proj in root:
        print (proj.tag, proj.attrib)
        src_repo = "%s/%s"%(src, proj.attrib['name'])
        os.chdir(src_repo)
        cmd = gen_patch_cmd_with_remote(proj.attrib['revision'])
        print ("\tgenerate patch : %s"%(os.getcwd()))
        os.system("%s > %s/%s.patch"%(cmd, fpath, proj.attrib['name']))

def do_commit_patch():
    pass

def read_manifest():
    local = jconf.get_local()
    fpath = '%s/patches/%s'%(local['jserver_path'], sys.argv[2])
    tree = ET.ElementTree(file='%s/manifest'%fpath)
    root = tree.getroot()
    return root

def read_file(rpath):
    dic = {}
    with open(rpath, "r") as fr:
        lines = fr.readlines()
        print (lines)
        for line in lines:
            line = line.strip()
            key = line.split("=", 1)[0].strip()
            val = line.split("=", 1)[1].strip()
            dic[key] = val
    return dic

def gen_diff_files(repo):
    ret = ""
    diffcmd = gen_patch_cmd(repo)
    cmd = "%s --name-only"%diffcmd
    lines = subprocess.getoutput(cmd).splitlines()
    return "\n\t".join(lines)



def decor_gen_commit_msg(func):
    def wrap_func():
        root = read_manifest()
        src = root.attrib['src']
        basedir = os.path.abspath(os.getcwd())
        for proj in root:
            print (proj.tag, proj.attrib)
            src_repo = "%s/%s"%(src, proj.attrib['name'])
            os.chdir(src_repo)
            files = gen_diff_files(proj.attrib['revision'])
            os.chdir(basedir)
            func(proj.attrib['name'], files)

    return wrap_func

def dump_dic_to_file(dst, cfg):
    order = ['title', 'model', 'description', 'related files']
    with open(dst, "w") as fw:
        for key in order:
            if key == "title":
                fw.write("%s\n\n"%cfg['title'])
            else:
                fw.write("%s\n"%key)
                fw.write(" " * 4 + "%s\n"%cfg[key])

@decor_gen_commit_msg
def gen_commit_msg(name, files):
    msg_cfg = read_file("%s/README"%get_patch_path())
    msg_cfg['related files'] = files
    dump_dic_to_file("%s/%s.msg"%(get_patch_path(), name), msg_cfg)

def gen_new_number():
    base_num = int(sys.argv[2])
    ps = [ int(x) for x in os.listdir("./patches") ]
    max_ps = max(ps) + 1

    base_dir = "./patches/%d"%(base_num)
    dst_dir = "./patches/%d"%(max_ps)
    os.mkdir(dst_dir)
    os.system("cp %s/manifest %s"%(base_dir, dst_dir))
    os.system("cp %s/README %s"%(base_dir, dst_dir))
    print ("new number is %d"%max_ps)

# patch -p1 -i ../CVE-2015-1038.patch
def exec_patch():
    bconfig = jconf.get_local()
    lconfig = jconf.get_build_server()
    root = read_manifest()
    for proj in root:
        cmd = "patch -p1 -i %s -d %s"
        print (proj.attrib['path'], proj.attrib['name'])
        patch_path = '%s/patches/%s/%s.patch'%(bconfig['jserver_path'], sys.argv[2], proj.attrib['name'])
        target_path = "/mnt_%s/%s/%s/%s/"%(lconfig['host'], lconfig['working_dir'], lconfig['build_dir'], proj.attrib['path'])
        cmd = cmd%(patch_path, target_path)
        print (cmd)
        os.system(cmd)

# patch -R -p1 -i ../CVE-2015-1038.patch
def reverse_patch():
    bconfig = jconf.get_local()
    lconfig = jconf.get_build_server()
    root = read_manifest()
    for proj in root:
        cmd = "patch -R -p1 -i %s -d %s"
        print (proj.attrib['path'], proj.attrib['name'])
        patch_path = '%s/patches/%s/%s.patch'%(bconfig['jserver_path'], sys.argv[2], proj.attrib['name'])
        if os.path.exists(patch_path) == False:
            continue

        target_path = "/mnt_%s/%s/%s/%s/"%(lconfig['host'], lconfig['working_dir'], lconfig['build_dir'], proj.attrib['path'])
        cmd = cmd%(patch_path, target_path)
        print (cmd)
        os.system(cmd)

def copy_patch():
    cmd = "rsync -a %s %s"
    patch_path = os.path.abspath('patches/%s'%(sys.argv[2]))
    lconfig = gconfig['git_server']
    target_path = "/mnt_%s/root/"%(lconfig['host'])
    cmd = cmd%(patch_path, target_path)
    print (cmd)
    os.system(cmd)

def re_exec_patch():
    reverse_patch()
    gen_commit_patch()
    exec_patch()

def gen_deploy_file():
    pass

def help():
    cmds = [
        'python3 jserver.py init',
        'python3 jserver.py gen_new_number $base_num',
        'python3 jserver.py gen_commit_msg $patch_num',
        'python3 jserver.py gen_commit_patch $patch_num',
        'python3 jserver.py gen_commit_patch_with_remote $patch_num',
        'python3 jserver.py exec_patch $patch_num',
        'python3 jserver.py reverse_patch $patch_num',
        'python3 jserver.py copy_patch $patch_num',
        'python3 jserver.py re_exec_patch $patch_num',
    ]
    for cmd in cmds:
        print(cmd)

def main():
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
