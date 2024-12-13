# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option) any later version.
#
# drk_lib.py - Shared functions

import sys
import os
import re
from debian.deb822 import Packages
from debian.deb822 import Sources
from debian.debian_support import NativeVersion

def print_noisy(msg):
    print(msg, file=sys.stderr)

def get_source_db(release):
    if release != "unstable" and release != "rolling" and release != "testing":
        raise ValueError("Invalid release specified.")

    src_package_dict = dict()
    sources_file_list = []
    for filename in os.listdir("/var/lib/apt/lists"):
        file = os.path.join("/var/lib/apt/lists", filename)
        if os.path.isfile(file):
            find_sources_regex = re.compile(".*" + release + "_.*_source_Sources")
            if re.match(find_sources_regex, file):
                sources_file_list.append(file)

    for file in sources_file_list:
        with open(file, "r") as fh:
            for src_package in Sources.iter_paragraphs(fh):
                if not "Package" in src_package:
                    continue

                if not "Version" in src_package:
                    continue

                if not src_package["Package"] in src_package_dict:
                    src_package_dict[src_package["Package"]] = src_package
                    continue

                orig_version = NativeVersion(src_package_dict[src_package["Package"]]["Version"])
                new_version = NativeVersion(src_package["Version"])
                if orig_version < new_version:
                    src_package_dict[src_package["Package"]] = src_package

    return src_package_dict