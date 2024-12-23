# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option)
# any later version.
#
# drk_remove_package.py - Implements the remove-package command.

import drk_lib
from drk_lib import *

def run_command():
    arg_list = sys.argv[2:len(sys.argv)]
    if len(arg_list) < 1:
        print_noisy("ERROR: No package provided!")
        sys.exit(1)

    target_pkg_name = arg_list[0]
    is_src_pkg = True if re.match("src:", target_pkg_name) else False
    rolling_bin_db = get_binary_db("rolling")
    rolling_src_db = get_source_db("rolling")

    if is_src_pkg:
        target_pkg_name = target_pkg_name[4:len(target_pkg_name)]
        if not target_pkg_name in rolling_src_db:
            print_noisy("The specified package does not exist in Rolling.")
            sys.exit(1)
    else:
        if not target_pkg_name in rolling_bin_db:
            print_noisy("The specified package does not exist in Rolling.")

    if not target_pkg_name in drk_lib.rolling_pkg_list_dict:
        print_noisy("The specified package is not in drk's rolling package list.")
        print_noisy("Ensure the package has no important reverse depends, then remove it with dak.")
        sys.exit(1)

    target_pkg_info = drk_lib.rolling_pkg_list_dict[target_pkg_name]
    target_no_recommends = target_pkg_info["no_recommends"]
    target_no_suggests = target_pkg_info["no_suggests"]

    remove_dep_list = generate_dep_list(target_no_recommends, target_no_suggests, is_src_pkg, rolling_bin_db, [], rolling_src_db, target_pkg_name)

    for other_pkg_name, other_pkg_info in drk_lib.rolling_pkg_list_dict:
        if other_pkg_name == target_pkg_name:
            continue
        other_no_recommends = other_pkg_info["no_recommends"]
        other_no_suggests = other_pkg_info["no_suggests"]
        other_dep_list = generate_dep_list(other_no_recommends, other_no_suggests,
        False, rolling_bin_db, [], rolling_src_db, other_pkg_name)
        for other_dep in other_dep_list:
            remove_dep_list.pop(other_dep, None)

    rolling_pkg_list_pkg_name = "{}{}".format("src:" if is_src_pkg else "", target_pkg_name)
    drk_lib.rolling_pkg_list_dict.pop(rolling_pkg_list_pkg_name, None)

    drk_lib.save_rolling_pkg_list()
    print("\n".join(remove_dep_list.keys()))
