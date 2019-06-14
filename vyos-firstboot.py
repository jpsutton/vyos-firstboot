#!/usr/bin/env python3

import os
import sys
import pycdlib

def add_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
    return decorator

@add_method(pycdlib.PyCdlib)
def walk(self, path="/", dr=None, recurse=True):
    if path != "/":
        yield path, dr

    for child in self.list_children(iso_path=path):
        name = child.file_identifier().decode().split(";")[0]
        fullpath = os.path.join(path, name)

        if name in (".", ".."):
            continue

        if child.is_dir():
            if recurse:
                yield from self.walk(fullpath, child)
            else:
                yield ("%s/" % fullpath), child

        elif child.is_file():
            yield fullpath, child



def main():
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: Unable to locate CD/DVD device.\n")
        sys.exit(-1)

    iso = pycdlib.PyCdlib()

    with open(sys.argv[1], "rb") as cdfp:
        try:
            iso.open_fp(cdfp)
            for path, dr in iso.walk():
                if path == "/VYOSINIT.CFG":
                    with open("/tmp/vyos-firstboot.cfg", "wb") as dest_file:
                        print("Extracting first boot config...")
                        iso_path = dr.file_identifier().decode()
                        iso.get_file_from_iso_fp(dest_file, iso_path=("/%s" % iso_path))
            else:
                sys.stderr.write("WARN: Unable to locate first boot configuration file.\n")
                sys.exit(-2)

        finally:
            iso.close()

if __name__ == "__main__":
    main()
