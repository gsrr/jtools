import sys


def dump_element(fw, dic, arr):
    for key in dic.keys():
        fw.write('%s [label="%s"]\n'%(key, key))

    history = {}
    for line in arr:
        if history.has_key(line) == False:
            history[line] = True        
            fw.write('%s\n'%(line))


def main():
    data = []
    with open("rest-hal.csv", "r") as fr:
        lines = fr.readlines()
        for line in lines:
            line = line.strip()
            data.append(line)

    arr = []
    dic = {}
    for line in data:
        items = line.split(",")[1].split()
        
        if "GET" in items[0]:
            es = items[1].split("/")
            i = 0
            lens = len(es)
            while i < lens:
                e = es.pop(0)
                e = e.strip()
                if e.startswith(":"):
                    i += 1
                    continue
                e = e.split("?")[0]
                if len(e) != 0:
                    dic[e] = True
                    es.append(e)
                i += 1
            for i in xrange(len(es) - 1):
                arr.append("->".join([es[i], es[i + 1]]))

    for key in dic.keys():
        print key
    
    for line in arr:
        print line
    with open("hal-input.dot", "w") as fw:
        fw.write("digraph L {\n")
        fw.write("graph [layout = dot,rankdir = LR]\n")
        fw.write("node [shape=circle fontname=Arial];\n")
        dump_element(fw, dic, arr)

        fw.write("}\n")



if __name__ == "__main__":
    main()
