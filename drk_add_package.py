# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option)
# any later version.
#
# drk_add_package.py - Implements the add-package command.

import drk_lib
from drk_lib import *
from debian.debian_support import NativeVersion

def run_command():
    no_list_recommends = False
    no_list_suggests = False
    target_pkg_name = ""
    arg_list = sys.argv[2:len(sys.argv)]

    for arg in arg_list:
        if arg == "--no-list-recommends":
            no_list_recommends = True
        elif arg == "--no-list-suggests":
            no_list_suggests = True
        else:
            target_pkg_name = arg

    if target_pkg_name == "":
        print_noisy("ERROR: No package provided!")
        sys.exit(1)

    is_src_pkg = True if re.match("src:", target_pkg_name) else False
    if is_src_pkg:
        target_pkg_name = target_pkg_name[4:len(target_pkg_name)]

    unstable_bin_db = get_binary_db("unstable")
    testing_bin_db = get_binary_db("testing")
    rolling_bin_db = get_binary_db("rolling")
    unstable_src_db = get_source_db("unstable")
    testing_src_db = get_source_db("testing")
    rolling_src_db = get_source_db("rolling")

    unstable_pkg_version = NativeVersion("0")
    testing_pkg_version = NativeVersion("0")
    rolling_pkg_version = NativeVersion("0")

    if is_src_pkg:
        if target_pkg_name in unstable_src_db:
            unstable_pkg_version = NativeVersion(unstable_src_db[target_pkg_name]["Version"])
        if target_pkg_name in testing_src_db:
            testing_pkg_version = NativeVersion(testing_src_db[target_pkg_name]["Version"])
        if target_pkg_name in rolling_src_db:
            rolling_pkg_version = NativeVersion(rolling_src_db[target_pkg_name]["Version"])
    else:
        if target_pkg_name in unstable_bin_db:
            unstable_pkg_version = NativeVersion(unstable_bin_db[target_pkg_name]["Version"])
        if target_pkg_name in testing_bin_db:
            testing_pkg_version = NativeVersion(testing_bin_db[target_pkg_name]["Version"])
        if target_pkg_name in rolling_bin_db:
            rolling_pkg_version = NativeVersion(rolling_bin_db[target_pkg_name]["Version"])

    rolling_pkg_info_version = NativeVersion("0")
    rolling_pkg_info_no_recommends = False
    rolling_pkg_info_no_suggests = False

    if target_pkg_name in drk_lib.rolling_pkg_list_dict:
        rolling_pkg_list_info = drk_lib.rolling_pkg_list_dict[target_pkg_name]
        rolling_pkg_info_version = NativeVersion(rolling_pkg_list_info["version"])
        rolling_pkg_info_no_recommends = bool(rolling_pkg_list_info["no_recommends"])
        rolling_pkg_info_no_suggests = bool(rolling_pkg_list_info["no_suggests"])

    if rolling_pkg_info_version is not NativeVersion("0") and rolling_pkg_info_version >= unstable_pkg_version:
        if rolling_pkg_info_no_recommends and not no_list_recommends:
            pass
        elif rolling_pkg_info_no_suggests and not no_list_suggests:
            pass
        else:
            print_noisy("This package is already present and up-to-date in Rolling.")
            sys.exit(0)
    elif testing_pkg_version == unstable_pkg_version:
        print_noisy("This package is already present and up-to-date in Testing.")
        sys.exit(0)
    elif rolling_pkg_version == unstable_pkg_version:
        print_noisy("ERROR: This package is already present and up-to-date in Rolling, but the local package list is out-of-date.")
        sys.exit(1)
    elif rolling_pkg_version > unstable_pkg_version:
        print_noisy("ERROR: The version of this package in Rolling is newer than the version in Unstable!")
        sys.exit(1)

    rolling_pkg_list_pkg_name = "{}{}".format("src:" if is_src_pkg else "", target_pkg_name)
    drk_lib.rolling_pkg_list_dict.pop(rolling_pkg_list_pkg_name, None)
    drk_lib.rolling_pkg_list_dict.update({
        target_pkg_name: {
            "version": str(unstable_pkg_version),
            "no_recommends": str(no_list_recommends),
            "no_suggests": str(no_list_suggests)
        }
    })

    dep_pkg_dict = drk_lib.generate_dep_list(no_list_recommends, no_list_suggests, is_src_pkg, unstable_bin_db, [testing_bin_db, rolling_bin_db], unstable_src_db, target_pkg_name)

    drk_lib.save_rolling_pkg_list()
    print("\n".join(dep_pkg_dict.keys()))