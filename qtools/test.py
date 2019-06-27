

i = 0
with open("test.txt", "r") as fr:
    lines = fr.readlines()
    for line in lines:
        items = line.split()
    print i, items[4], " ".join(items[6:])
        i += 1


a = 5

    


