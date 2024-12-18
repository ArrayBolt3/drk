# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option)
# any later version.
#
# drk_lib.py - Shared functions

import sys
import os
import re
from enum import Enum
from debian.deb822 import Packages
from debian.deb822 import Sources
from debian.debian_support import NativeVersion

rolling_pkg_list_path = "~/.local/config/drk_rolling_pkg_list"
rolling_pkg_list_dict = dict()

def print_noisy(msg: str):
    print(msg, file=sys.stderr)

def load_rolling_pkg_list():
    with open(rolling_pkg_list_path, "r") as rolling_pkg_list_file:
        for rolling_pkg_list_line in rolling_pkg_list_file:
            rolling_pkg_list_parts = rolling_pkg_list_line.split(" ")
            rolling_pkg_name = ""
            rolling_pkg_version = ""
            rolling_pkg_no_recommends = ""
            rolling_pkg_no_suggests = ""
            if len(rolling_pkg_list_parts) >= 1:
                rolling_pkg_name = rolling_pkg_list_parts[0]
            if len(rolling_pkg_list_parts) >= 2:
                rolling_pkg_version = rolling_pkg_list_parts[1]
            if len(rolling_pkg_list_parts) >= 3:
                rolling_pkg_no_recommends = True if rolling_pkg_list_parts[2] == "no_recommends" else False
                rolling_pkg_no_suggests = True if rolling_pkg_list_parts[2] == "no_suggests" else False
            if len(rolling_pkg_list_parts) >= 4:
                rolling_pkg_no_suggests = True if rolling_pkg_list_parts[2] == "no_suggests" else False

            rolling_pkg_list_dict.update({
                rolling_pkg_name: {
                    "version": rolling_pkg_version,
                    "no_recommends": rolling_pkg_no_recommends,
                    "no_suggests": rolling_pkg_no_suggests
                }
            })

def save_rolling_pkg_list():
    with open(rolling_pkg_list_path, "w") as rolling_pkg_list_file:
        for pkg_name, pkg_info in rolling_pkg_list_dict:
            build_line = pkg_name
            if "version" in pkg_info:
                build_line = build_line + " " + pkg_info["version"]
            if "no_recommends" in pkg_info and pkg_info["no_recommends"] != "":
                build_line = build_line + " " + "no_recommends"
            if "no_suggests" in pkg_info and pkg_info["no_suggests"] != "":
                build_line = build_line + " " + "no_suggests"
            rolling_pkg_list_file.write(build_line + "\n")

def get_source_db(release: str):
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

def get_binary_db(release: str):
    if release != "unstable" and release != "rolling" and release != "testing":
        raise ValueError("Invalid release specified.")

    bin_package_dict = dict()
    packages_file_list = []
    for filename in os.listdir("/var/lib/apt/lists"):
        file = os.path.join("/var/lib/apt/lists", filename)
        if os.path.isfile(file):
            find_sources_regex = re.compile(".*" + release + "_.*_binary-.*_Packages")
            if re.match(find_sources_regex, file):
                packages_file_list.append(file)

    for file in packages_file_list:
        with open(file, "r") as fh:
            for bin_package in Packages.iter_paragraphs(fh):
                if not "Package" in bin_package:
                    continue

                if not "Version" in bin_package:
                    continue

                if not bin_package["Package"] in bin_package_dict:
                    bin_package_dict[bin_package["Package"]] = bin_package
                    continue

                orig_version = NativeVersion(bin_package_dict[bin_package["Package"]]["Version"])
                new_version = NativeVersion(bin_package["Version"])
                if orig_version < new_version:
                    bin_package_dict[bin_package["Package"]] = bin_package

    return bin_package_dict

def filter_db(merge_pkg_dict: dict, main_pkg_db: dict, filter_pkg_db: dict):
    pkg_remove_list = []

    for merge_pkg_name in merge_pkg_dict.keys():
        merge_pkg = main_pkg_db[merge_pkg_name]
        if merge_pkg_name in filter_pkg_db:
            main_version = NativeVersion(merge_pkg["Version"])
            filter_version = NativeVersion(filter_pkg_db[merge_pkg_name]["Version"])
            if filter_version < main_version:
                continue
            elif filter_version == main_version:
                pkg_remove_list.append(merge_pkg_name)
            else:
                print_noisy("filter_pkg_db ERROR: filter_pkg_db has a package newer than main_pkg_db?!")
                print_noisy("Package: " + merge_pkg_name)
                print_noisy("Main version: " + str(main_version))
                print_noisy("Filter version: " + str(filter_version))
                pkg_remove_list.append(merge_pkg_name)

    output_pkg_dict = merge_pkg_dict.copy()

    for pkg_remove_name in pkg_remove_list:
        output_pkg_dict.pop(pkg_remove_name)

    return output_pkg_dict


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

def generate_dep_list(dep_list_mode: DrkDepListMode, no_list_recommends: bool, no_list_suggests: bool, is_src_pkg: bool, unstable_bin_db: dict, testing_bin_db: dict, rolling_bin_db: dict, unstable_src_db: dict, unstable_pkg_name: str):

    if is_src_pkg:
        if not unstable_pkg_name in unstable_src_db:
            raise KeyError("The specified package does not exist in Debian Unstable!")
    else:
        if not unstable_pkg_name in unstable_bin_db:
            raise KeyError("The specified package does not exist in Debian Unstable!")

    output_pkg_dict = dict()
    handled_virtual_pkg_set = set()

    if is_src_pkg:
        unstable_pkg = unstable_src_db[unstable_pkg_name]
    else:
        unstable_pkg = unstable_bin_db[unstable_pkg_name]
        output_pkg_dict.update(unstable_pkg["Package"])

    if "Build-Depends" in unstable_pkg:
        output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Build-Depends"])))
    if "Binary" in unstable_pkg:
        output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Binary"])))
    if "Pre-Depends" in unstable_pkg:
        output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Pre-Depends"])))
    if "Depends" in unstable_pkg:
        output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Depends"])))
    if "Recommends" in unstable_pkg and not no_list_recommends:
        output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Recommends"])))
    if "Suggests" in unstable_pkg and not no_list_suggests:
        output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Suggests"])))

    idx = 0
    while idx < len(output_pkg_dict):
        unstable_pkg_name = list(output_pkg_dict.keys())[idx]
        if unstable_pkg_name == "":
            idx += 1
            continue
        if unstable_pkg_name in unstable_bin_db: # Normal package
            unstable_pkg = unstable_bin_db[unstable_pkg_name]
            # No need to take Build-Depends and Binary into account here,
            # we're only dealing with binary packages now.
            if "Pre-Depends" in unstable_pkg:
                output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Pre-Depends"])))
            if "Depends" in unstable_pkg:
                output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Depends"])))
            if "Recommends" in unstable_pkg and not no_list_recommends:
                output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Recommends"])))
            if "Suggests" in unstable_pkg and not no_list_suggests:
                output_pkg_dict.update(dict.fromkeys(convert_to_pkg_list(unstable_pkg["Suggests"])))
        elif unstable_pkg_name not in handled_virtual_pkg_set: # Virtual package
            provide_pkg_list = []
            for search_pkg_name, search_pkg in unstable_bin_db.items():
                if "Provides" in search_pkg:
                    search_pkg_provide_list = convert_to_pkg_list(search_pkg["Provides"])
                    if unstable_pkg_name in search_pkg_provide_list:
                        provide_pkg_list.append(search_pkg_name)
            output_pkg_dict.update(dict.fromkeys(provide_pkg_list))
            handled_virtual_pkg_set.add(unstable_pkg_name)

        idx += 1

    for remove_pkg_name in handled_virtual_pkg_set:
        output_pkg_dict.pop(remove_pkg_name)

    if dep_list_mode == DrkDepListMode.FULL:
        return output_pkg_dict
#        print("\n".join(output_pkg_dict.keys()))
#        return

    output_pkg_dict = filter_db(output_pkg_dict, unstable_bin_db, testing_bin_db)
    if dep_list_mode == DrkDepListMode.FRESH:
        return output_pkg_dict
#        print("\n".join(output_pkg_dict.keys()))
#        return

    output_pkg_dict = filter_db(output_pkg_dict, unstable_bin_db, rolling_bin_db)
    if dep_list_mode == DrkDepListMode.ROLLING:
        return output_pkg_dict
#        print("\n".join(output_pkg_dict.keys()))
#        return