import re
import sys
import os
import copy

def freadlines(path):
    ret = []
    with open(path, "r") as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip()
            ret.append(line)
    return ret


def event_get_functions():
    cwd = os.getcwd()
    os.chdir("./eventproj")
    cmds = [
        'find . -name "*.c" > cscope.files',
        'cscope -R -L -2 ".*" > event.funcs',
    ]
    for cmd in cmds:
        os.system(cmd)
    lines = freadlines("event.funcs")
    os.chdir(cwd)

    ret = {}
    for line in lines:
        items = line.split()
        key = "%s@%s"%(items[1], items[0])
        ret[key] = [items[0], items[1]]
    return ret

def func_get_define(fname):
    cwd = os.getcwd()
    os.chdir("./qnapproj")
    cmds = [
        'find . -name "*.c" > cscope.files',
        'cscope -R -L -1 "%s" > funcs.define'%fname,
    ]
    for cmd in cmds:
        os.system(cmd)
    lines = freadlines("funcs.define")
    os.chdir(cwd)
    if len(lines) == 0:
        return ""
    return lines[0].split()[0]

def func_get_childfunc(event, fname):
    cwd = os.getcwd()
    os.chdir("./qnapproj")
    cmds = [
        'find . -name "*.c" > cscope.files',
        'cscope -R -L -2 "%s" > funcs.child'%fname,
    ]
    for cmd in cmds:
        os.system(cmd)
    lines = freadlines("funcs.child")
    os.chdir(cwd)
    if len(lines) == 0:
        return []
    
    ret = []
    for line in lines:
        line = line.strip()
        ret.append(line.split()[1])
    return ret
    

def event_category():
    efuncs = event_get_functions()

    keys = copy.deepcopy(efuncs.keys())
    for key in keys:
        cfuncs = func_get_childfunc(efuncs[key][0], efuncs[key][1])
        for cfunc in cfuncs:
            nkey = "%s@%s"%(cfunc, efuncs[key][0])
            if efuncs.has_key(nkey) == True:
                continue
            efuncs[nkey] = [efuncs[key][1], cfunc]

    for key in efuncs.keys():
        fdef = func_get_define(efuncs[key][1])
        efuncs[key].append(fdef)
        efuncs[key].append(os.path.dirname(fdef))

    with open("event.category", "w") as fw:
        for key in efuncs.keys():
            print key, efuncs[key]
            fw.write("%s,%s\n"%(key, ",".join(efuncs[key])))
    
def func_filter():
    filters = freadlines("filters")
    tmp_list = []
    data = []
    with open("event.category", "r") as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip()
            tmp_list.append(line)
    for line in tmp_list:
        items = line.split(",")
        name, event = items[0].split("@")
        if name in filters:
            continue
        if items[-1] == "/usr/include":
            continue
        print "%s: %-20s: %-50s"%(event, items[-1], name)

    
def func_filter_dry_run():
    filters = freadlines("filters")
    tmp_list = []
    data = []
    with open("event.category", "r") as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip()
            tmp_list.append(line)
    for line in tmp_list:
        items = line.split(",")
        name, event = items[0].split("@")
        if name in filters:
            continue
        print "%s"%(name)

def main():
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
