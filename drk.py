# drk - Debian Rolling Kit
# Licensed under the GNU General Public License version 2, or (at your option) any later version.
#
# drk.py - Main entry point

from drk_lib import *
import drk_generate_dep_list
import sys

def print_usage():
    print_noisy("""Usage: drk COMMAND [...]
Run DRK commands.

Available commands:
  list-versions      Shows the versions of a package in Testing, Rolling, and Unstable
  generate-dep-list  Get a list containing a package and its dependencies
  add-package        Copy a package and its dependencies from Unstable to Rolling
  remove-package     Removes a package from Rolling
  clean-archive      Automatically removes obsolete packages from Rolling""")

def main():
    match drk_command:
        case "list-versions":
            print(1)
        case "generate-dep-list":
            drk_generate_dep_list.run_command()
        case "add-package":
            print(3)
        case "remove-package":
            print(4)
        case "clean-archive":
            print(5)
        case default:
            print_usage()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    drk_command = sys.argv[1]
    main()