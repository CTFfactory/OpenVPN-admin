#!/usr/bin/python3
# OpenVPN TLS Verify, but cooler

from sys import argv, exit


def is_match(users, depth, cn):
    try:
        d = int(depth)
    except ValueError:
        return False
    if d != 0:
        return True
    try:
        ul = open(users, "r")
        u = [l.strip().lower() for l in ul.read().split("\n")]
        ul.close()
        del ul
    except OSError:
        print('Cannot read users list "%s"!' % users)
        return False
    i = cn.find("CN=")
    if i < 0:
        return False
    i += len("CN=")
    c = cn.find(",", i)
    if c <= i:
        s = cn[i:].strip().lower()
    else:
        s = cn[i:c].strip().lower()
    return s in u


if __name__ == "__main__":
    if len(argv) != 4:
        print("%s <user_list> <depth> <cn>" % argv[0])
        exit(1)
    if is_match(argv[1], argv[2], argv[3]):
        exit(0)
    exit(1)
