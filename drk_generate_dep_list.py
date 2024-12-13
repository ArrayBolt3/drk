# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option) any later version.
#
# drk_generate_dep_list.py - Implements the generate-dep-list command.

from drk_lib import *
import sys
from enum import Enum
from debian.deb822 import Packages
from debian.deb822 import Sources
from debian.debian_support import NativeVersion

class DrkDepListMode(Enum):
    FULL = 1
    FRESH = 2
    ROLLING = 3
    UNDEFINED = 4

def convert_to_pkg_list(pkg_str):
    output_list = []
    pkg_list = pkg_str.split(", ")
    for pkg in pkg_list:
        if "|" in pkg:
            inner_pkg_list = pkg.split("|")
            for inner_pkg in inner_pkg_list:
                val = inner_pkg.strip().split(" ")[0]
                if ":" in val:
                    val = val[0:val.find(":")]
                if val != "":
                    output_list.append(val)
        else:
            val = pkg.strip().split(" ")[0]
            if ":" in val:
                val = val[0:val.find(":")]
            if val != "":
                output_list.append(val)

    return output_list

def run_command():
    dep_list_mode = DrkDepListMode.UNDEFINED
    no_list_recommends = False
    no_list_suggests = False
    src_pkg_name = ""
    arg_list = sys.argv[2:len(sys.argv)]

    for arg in arg_list:
        if arg == "--full" or arg == "--fresh" or arg == "--rolling":
            if dep_list_mode != DrkDepListMode.UNDEFINED:
                print_noisy("FATAL ERROR: Can only specify one generation mode!")
                sys.exit(1)

        if arg == "--full":
            dep_list_mode = DrkDepListMode.FULL
        elif arg == "--fresh":
            dep_list_mode = DrkDepListMode.FRESH
        elif arg == "--rolling":
            dep_list_mode = DrkDepListMode.ROLLING
        elif arg == "--no-list-recommends":
            no_list_recommends = True
        elif arg == "--no-list-suggests":
            no_list_suggests = True
        else:
            src_pkg_name = arg
            break

    unstable_src_db = dict()
    testing_src_db = dict()
    rolling_src_db = dict()
    unstable_bin_db = dict()
    testing_bin_db = dict()
    rolling_bin_db = dict()
    if dep_list_mode == DrkDepListMode.FULL:
        unstable_src_db = get_source_db("unstable")
        unstable_bin_db = get_binary_db("unstable")
    elif dep_list_mode == DrkDepListMode.FRESH:
        unstable_src_db = get_source_db("unstable")
        unstable_bin_db = get_binary_db("unstable")
        testing_src_db = get_source_db("testing")
        testing_bin_db = get_binary_db("testing")
    elif dep_list_mode == DrkDepListMode.ROLLING:
        unstable_src_db = get_source_db("unstable")
        unstable_bin_db = get_binary_db("unstable")
        testing_src_db = get_source_db("testing")
        testing_bin_db = get_binary_db("testing")
        rolling_src_db = get_source_db("rolling")
        rolling_bin_db = get_binary_db("rolling")

    if not src_pkg_name in unstable_src_db:
        raise KeyError("The specified package does not exist in Debian Unstable!")

    unstable_src = unstable_src_db[src_pkg_name]
    output_pkg_dict = dict()
    handled_virtual_pkg_set = set()
    output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_src["Binary"])))
    # This pulls in an unbelievable pile of junk, don't bother with it
    # output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_src["Build-Depends"])))

    idx = 0
    while idx < len(output_pkg_dict):
        bin_pkg_name = list(output_pkg_dict.keys())[idx]
        if bin_pkg_name == "":
            idx += 1
            continue
        if bin_pkg_name in unstable_bin_db: # Normal package
            bin_pkg = unstable_bin_db[bin_pkg_name]
            if "Depends" in bin_pkg:
                output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(bin_pkg["Depends"])))
            if "Recommends" in bin_pkg and not no_list_recommends:
                output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(bin_pkg["Recommends"])))
            if "Suggests" in bin_pkg and not no_list_suggests:
                output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(bin_pkg["Suggests"])))
        elif bin_pkg_name not in handled_virtual_pkg_set: # Virtual package
            provide_pkg_list = []
            for search_bin_pkg_name, search_bin_pkg in unstable_bin_db.items():
                if "Provides" in search_bin_pkg:
                    search_bin_pkg_provide_list = convert_to_pkg_list(search_bin_pkg["Provides"])
                    if bin_pkg_name in search_bin_pkg_provide_list:
                        provide_pkg_list.append(search_bin_pkg_name)
            output_pkg_dict.update(dict.fromkeys(provide_pkg_list))
            handled_virtual_pkg_set.add(bin_pkg_name)

        idx += 1

    for remove_pkg_name in handled_virtual_pkg_set:
        output_pkg_dict.pop(remove_pkg_name)

    if dep_list_mode == DrkDepListMode.FULL:
        print("\n".join(output_pkg_dict.keys()))
        return

    pkg_already_in_testing_list = []

    for output_pkg_name in output_pkg_dict.keys():
        output_pkg = unstable_bin_db[output_pkg_name]
        if output_pkg_name in testing_bin_db:
            unstable_version = NativeVersion(output_pkg["Version"])
            testing_version = NativeVersion(testing_bin_db[output_pkg_name]["Version"])
            if testing_version < unstable_version:
                continue
            elif testing_version == unstable_version:
                pkg_already_in_testing_list.append(output_pkg_name)
            else:
                print_noisy("Testing has a package newer than Unstable?!");
                print_noisy("Package: " + output_pkg_name)
                print_noisy("Unstable version: " + output_pkg["Version"])
                print_noisy("Testing version: " + testing_bin_db[output_pkg_name]["Version"])
                pkg_already_in_testing_list.append(output_pkg_name)

    for remove_pkg_name in pkg_already_in_testing_list:
        output_pkg_dict.pop(remove_pkg_name)

    if dep_list_mode == DrkDepListMode.FRESH:
        print("\n".join(output_pkg_dict.keys()))
        return