# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option)
# any later version.
#
# drk_generate_dep_list.py - Implements the generate-dep-list command.
import drk_lib
from drk_lib import *
import sys

def run_command():
    dep_list_mode = DrkDepListMode.UNDEFINED
    no_list_recommends = False
    no_list_suggests = False
    unstable_pkg_name = ""
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
            unstable_pkg_name = arg
            break

    is_src_pkg = True if re.match("src:", unstable_pkg_name) else False
    if is_src_pkg:
        unstable_pkg_name = unstable_pkg_name[4:len(unstable_pkg_name)]

    unstable_bin_db = dict()
    testing_bin_db = dict()
    rolling_bin_db = dict()
    if dep_list_mode == DrkDepListMode.FULL:
        unstable_bin_db = get_binary_db("unstable")
    elif dep_list_mode == DrkDepListMode.FRESH:
        unstable_bin_db = get_binary_db("unstable")
        testing_bin_db = get_binary_db("testing")
    elif dep_list_mode == DrkDepListMode.ROLLING:
        unstable_bin_db = get_binary_db("unstable")
        testing_bin_db = get_binary_db("testing")
        rolling_bin_db = get_binary_db("rolling")

    unstable_src_db = get_source_db("unstable")

    output_pkg_dict = drk_lib.generate_dep_list(dep_list_mode, no_list_recommends, no_list_suggests, is_src_pkg, unstable_bin_db, testing_bin_db, rolling_bin_db, unstable_src_db, unstable_pkg_name)

    print("\n".join(output_pkg_dict.keys()))