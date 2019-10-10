import subprocess
import os
import xml.etree.cElementTree as ET
import jlib.jconf as jconf

def read_manifest(patch_dir):
    local = jconf.get_local()
    tree = ET.ElementTree(file='%s/manifest'%patch_dir)
    root = tree.getroot()
    return root

# patch -R -p1 -i ../CVE-2015-1038.patch
def reverse_patch(paras):
    bconfig = jconf.get_local()
    lconfig = jconf.get_build_server()
    root = read_manifest(paras['patch_dir'])
    for proj in root:
        if len(proj.attrib['revision']) == 0:
            continue
        cmd = "patch -R -p1 -i %s -d %s"
        patch_path = '%s/%s.patch'%(paras['patch_dir'], proj.attrib['name'])
        if os.path.exists(patch_path) == False:
            continue

        target_path = "/mnt_%s/%s/%s/%s/"%(lconfig['host'], lconfig['working_dir'], lconfig['build_dir'], proj.attrib['path'])
        cmd = cmd%(patch_path, target_path)
        print (cmd)
        os.system(cmd)
    return 0

def get_start_end_commid(repo):
    cmd = "git reflog show --no-abbrev %s"%repo
    lines = subprocess.getoutput(cmd).splitlines()
    return (lines[0].split()[0], lines[-1].split()[0])

def gen_cmd_for_patch(repo):
    commid_end, commid_start = get_start_end_commid(repo)
    cmd = "git diff %s..%s"%(commid_start, commid_end)
    return cmd

def _gen_patch(src, name, revision, patch_dir):
    src_repo = "%s/%s"%(src, name)
    tmpdir = os.getcwd()
    os.chdir(src_repo)
    cmd = gen_cmd_for_patch(revision)
    os.system("%s > %s/%s.patch"%(cmd, patch_dir, name))
    os.chdir(tmpdir)

def gen_patch(paras):
    lconfig = jconf.get_local()
    root = read_manifest(paras['patch_dir'])

    for proj in root:
        if len(proj.attrib['revision']) == 0:
            continue

        _gen_patch(root.attrib['src'], proj.attrib['name'], proj.attrib['revision'], paras['patch_dir'])
    return 0

def _exec_patch(patch_path, target_path):
    cmd = "patch -p1 -i %s -d %s"
    cmd = cmd%(patch_path, target_path)
    print (cmd)
    os.system(cmd)

# patch -p1 -i ../CVE-2015-1038.patch
def exec_patch(paras):
    bconfig = jconf.get_local()
    lconfig = jconf.get_build_server()
    root = read_manifest(paras['patch_dir'])
    for proj in root:
        if len(proj.attrib['revision']) == 0:
            continue

        patch_path = '%s/%s.patch'%(paras['patch_dir'], proj.attrib['name'])
        target_path = "/mnt_%s/%s/%s/%s/"%(lconfig['host'], lconfig['working_dir'], lconfig['build_dir'], proj.attrib['path'])
        _exec_patch(patch_path, target_path)
    return 0
