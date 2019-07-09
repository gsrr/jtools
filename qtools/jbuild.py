import sys

def build():
    path = sys.argv[2]
    op = sys.argv[3]
    print path, op

def main():
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

if __name__ == "__main__":
    main()
