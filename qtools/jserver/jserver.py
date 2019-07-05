import time
import sys
import socket
import configparser
import os
import glob
import xml.etree.cElementTree as ET
import subprocess


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
    config = configparser.ConfigParser()
    config.read('jserver.conf')
    for section in config.sections():
        hosts = config[section]['host'].split(",")
        for host in hosts:
            print (section, host.strip())
            init_remote_client(host.strip(), config[section])
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
    fpath = os.path.abspath('patches/%s'%sys.argv[2])
    tree = ET.ElementTree(file='%s/manifest'%fpath)
    root = tree.getroot()
    src = "/mnt_%s"%root.attrib['src']
    basedir = os.getcwd()
    for proj in root:
        print (proj.tag, proj.attrib)
        src_repo = "%s/%s"%(src, proj.attrib['name'])
        os.chdir(src_repo)
        cmd = gen_patch_cmd(proj.attrib['revision'])
        print ("\tgenerate patch : %s"%(os.getcwd()))
        os.system("%s > %s/%s.patch"%(cmd, fpath, proj.attrib['name']))

def do_commit_patch():
    pass

def read_manifest():
    fpath = os.path.abspath('patches/%s'%sys.argv[2])
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
        src = "/mnt_%s"%root.attrib['src']
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
                fw.write("%s\n"%cfg['title'])
            else:
                fw.write("%s\n"%key)
                fw.write(" " * 4 + "%s\n"%cfg[key])

@decor_gen_commit_msg
def gen_commit_msg(name, files):
    ppath = os.path.abspath('patches/%s'%sys.argv[2])
    msg_cfg = read_file("%s/README"%ppath)
    msg_cfg['related files'] = files
    dump_dic_to_file("%s/%s.msg"%(ppath, name), msg_cfg)

def gen_patch():
    base_num = int(sys.argv[2])
    ps = [ int(x) for x in os.listdir("./patches") ]
    max_ps = max(ps) + 1

    base_dir = "./patches/%d"%(base_num)
    dst_dir = "./patches/%d"%(max_ps)
    os.mkdir(dst_dir)
    os.system("cp %s/manifest %s"%(base_dir, dst_dir))
    os.system("cp %s/README %s"%(base_dir, dst_dir))

def help():
    cmds = [
        'python3 jserver.py init',
        'python3 jserver.py gen_patch $base_num',
        'python3 jserver.py gen_commit_msg $patch_num',
        'python3 jserver.py gen_commit_patch $patch_num',
    ]
    for cmd in cmds:
        print(cmd)

def main():
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
