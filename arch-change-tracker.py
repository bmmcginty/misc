import argparse
import gzip
import hashlib
import os
import re
import subprocess
import sys


keep = [
    "/root/",
    "/etc/"]


def pif(label, obj, output=sys.stdout):
    if obj:
        if isinstance(obj, list):
            obj = ", ".join(sorted(obj))
        print("%s %s" % (label, obj,), file=output)


def check(args):
    ret = []
    pmdir = "/var/lib/pacman/local"
    dirs = os.listdir(pmdir)
    dirs = [os.path.join(pmdir, i) for i in dirs if not i.startswith(".")]
    db = {}
    for i in dirs:
        if not os.path.isdir(i):
            continue
        fh = gzip.open(os.path.join(i, "mtree"), "r")
        lines = fh.read().decode("utf-8").split("\n")
        fh.close()
        l = {}
        defaults = {}
        for line in lines:
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ")
            d = dict([p.split("=", 1) for p in parts[1:]])
            fn = parts[0]
            if fn == "/set":
                defaults.update(d)
                continue
            for k in defaults:
                if k not in d:
                    d[k] = defaults[k]
            escapes = re.findall(r"\\[0-9]{3,3}", fn)
            for escape in escapes:
                fn = fn.replace(escape, chr(int(escape[1:], 8)))
            if fn.startswith("./"):
                fn = fn[1:]
            parent, child = fn.rsplit("/", 1)
            if parent == "":
                parent = "/"
            if parent not in l:
                l[parent] = []
            d["fn"] = child
            l[parent].append(d)

        keys = list(l.keys())
        for parent in keys:
            for child in l[parent]:
                t = os.path.join(parent, child["fn"])
                if child["type"] == "dir" and t not in l:
                    l[t] = []

        db[i] = l

    gchildren = {}
    for pkg in db:
        for parent in db[pkg]:
            children = db[pkg][parent]
            if parent not in gchildren:
                gchildren[parent] = {}
            for c in children:
                gchildren[parent][c["fn"]] = c

    for parent in sorted(list(gchildren.keys())):
        ld = os.listdir(parent)
        should_have = set([j["fn"] for j in gchildren[parent].values()])
        extra = [i for i in ld if i not in should_have]
        missing = [i for i in should_have if i not in ld]
        different = []
        for i in should_have:
            if i in missing:
                continue
            expect = gchildren[parent][i]
            stat = os.stat(os.path.join(parent, i), follow_symlinks=False)
            if expect["type"] != "file":
                continue
            ta = int(expect["time"].split(".")[0])
            tb = int(stat.st_mtime)
            if ta != tb:
                different.append(i)
                continue
            ta = int(expect["size"])
            tb = stat.st_size
            if ta != tb:
                different.append(i)
                continue
            if args.hash:
                ta = expect["sha256digest"]
                tb = hashlib.sha256()
                with open(os.path.join(parent, i), "rb") as fh:
                    while 1:
                        fc = fh.read(4096)
                        if not fc:
                            break
                        tb.update(fc)
                tb = tb.hexdigest()
                if ta != tb:
                    different.append(i)
        if extra or missing or different:
            pif("parent", parent, output=args.output)
            pif("different", different, output=args.output)
            pif("missing", missing, output=args.output)
            pif("extra", extra, output=args.output)
        ret.append({
            "different": different,
            "extra": extra,
            "missing": missing,
            "parent": parent
        })

    return ret


def do_copy(args, result):
    parent = result["parent"]
    for name in ["different", "extra"]:
        for t in result[name]:
            path = os.path.join(parent, t)
            if not [i for i in keep if path.startswith(i)]:
                continue
            newpath = os.path.join(args.copy, path.lstrip("/"))
            cmd = ["/usr/bin/cp", "-R", path, newpath]
            if args.dry_run:
                cmd = ["/usr/bin/echo"]+cmd
            else:
                os.makedirs(os.path.dirname(newpath), exist_ok=True)
            subprocess.run(cmd, check=True, stdout=args.output)


def arg_file(path):
    return open(path, "w")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", action="store_true", default=False)
    parser.add_argument("--exclude", action="append")
    parser.add_argument("--copy", action="store")
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--output", type=arg_file, default=sys.stdout)
    args = parser.parse_args()
    results = check(args)
    if args.copy:
        [do_copy(args, result) for result in results]


if __name__ == "__main__":
    main()
