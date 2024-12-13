# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option) any later version.
#
# drk_generate_dep_list.py - Implements the generate-dep-list command.

from drk_lib import *
import sys
from enum import Enum

class DrkDepListMode(Enum):
    FULL = 1
    FRESH = 2
    ROLLING = 3
    UNDEFINED = 4

def run_command():
    dep_list_mode = DrkDepListMode.UNDEFINED
    no_list_recommends = False
    no_list_suggests = False
    src_package_name = ""
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
            src_package_name = arg
            break

    unstable_pkg_db = dict()
    testing_pkg_db = dict()
    rolling_pkg_db = dict()
    if dep_list_mode >= DrkDepListMode.FULL:
        unstable_pkg_db = get_source_db("unstable")
    if dep_list_mode >= DrkDepListMode.FRESH:
        testing_pkg_db = get_source_db("testing")
    if dep_list_mode >= DrkDepListMode.ROLLING:
        rolling_pkg_db = get_source_db("rolling")