# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option)
# any later version.
#
# drk_list_versions.py - Implements the list-versions command.

from drk_lib import *
import sys
import re

def run_command():
    arg_list = sys.argv[2:len(sys.argv)]
    if len(arg_list) < 1:
        print_noisy("ERROR: No package provided!")
        sys.exit(1)

    pkg_name = arg_list[0]
    is_src_pkg = True if re.match("src:", pkg_name) else False

    if is_src_pkg:
        pkg_name = pkg_name[4:len(pkg_name)]

        unstable_pkg_db = get_source_db("unstable")
        testing_pkg_db = get_source_db("testing")
        rolling_pkg_db = get_source_db("rolling")
    else:
        unstable_pkg_db = get_binary_db("unstable")
        testing_pkg_db = get_binary_db("testing")
        rolling_pkg_db = get_binary_db("rolling")

    if pkg_name in unstable_pkg_db:
        unstable_pkg_ver = unstable_pkg_db[pkg_name]["Version"]
    else:
        unstable_pkg_ver = "Not present"

    if pkg_name in testing_pkg_db:
        testing_pkg_ver = testing_pkg_db[pkg_name]["Version"]
    else:
        testing_pkg_ver = "Not present"

    if pkg_name in rolling_pkg_db:
        rolling_pkg_ver = rolling_pkg_db[pkg_name]["Version"]
    else:
        rolling_pkg_ver = "Not present"

    print("Package name: {}".format(pkg_name))
    print("Source package: {}".format("True" if is_src_pkg else "False"))
    print("Versions:")
    print("  Unstable : {}".format(unstable_pkg_ver))
    print("  Testing  : {}".format(testing_pkg_ver))
    print("  Rolling  : {}".format(rolling_pkg_ver))