# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option)
# any later version.
#
# drk.py - Main entry point
import drk_lib
from drk_lib import *
import drk_list_versions
import drk_generate_dep_list
import drk_add_package
import sys

def print_usage():
    print_noisy("""Usage: drk COMMAND [...]
Run DRK commands.

Available commands:
  list-versions      Shows the versions of a package in Testing, Rolling, and Unstable
  generate-dep-list  Get a list containing a package and its dependencies
  add-package        Adds a package to Rolling
  remove-package     Removes a package from Rolling
  clean-archive      Automatically removes obsolete packages from Rolling""")

def main():
    drk_lib.load_rolling_pkg_list()
    match drk_command:
        case "list-versions":
            drk_list_versions.run_command()
        case "generate-dep-list":
            drk_generate_dep_list.run_command()
        case "add-package":
            drk_add_package.run_command()
        case "remove-package":
            print(5)
        case "clean-archive":
            print(6)
        case default:
            print_usage()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    drk_command = sys.argv[1]
    main()