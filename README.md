# drk - Debian Rolling Kit

drk is a set of tools intended to assist in maintaining the Debian Rolling
archive. It is designed to be used alongside dak, the Debian Archive Kit.

drk does not require a functional dak instance to function. It only gives info
about *what* to do with packages, it doesn't actually do any of it, for safety
reasons.

## Synposis

```
drk <action> <argument1> [<argument2> ...]
```

## Actions

* `list-versions <binary-package|src:src-package>` - Shows the versions of a
  package available in the Unstable, Rolling, and Testing archives.
* `generate-dep-list <--full|--fresh|--rolling> [--no-list-recommends]
  [--no-list-suggests] <bin-package|src:src-package>` - Generates a list
  containing a package and its dependencies (including build dependencies for
  source packages). All possible alternative dependencies and all packages
  providing a virtual package are taken into consideration. If `--full` is
  specified, a complete dependency list is generated based on the contents of
  Unstable. If `--fresh` is specified, only those packages which have updated
  versions in Unstable that aren't already in Testing are listed. If `--rolling`
  is specified, only those packages which have updated versions in Unstable that
  aren't already in Testing *or* Rolling are listed. The `--no-list-recommends`
  and `--no-list-suggests` arguments can be used to suppress showing recommended
  or suggested packages in the list.
* `add-package [--no-list-recommends] [--no-list-suggests]
  <bin-package|src:src-package>` - Adds a package to drk's rolling package list,
  and prints out the full list of packages that need imported into the Rolling
  archive to introduce the package into the archive. This is very similar to
  `generate-dep-list`, but with the rolling package list taken into account.
* `remove-package <bin-package|src:src-package>` - Removes a package from drk's
  rolling package list, and prints out the full list of packages that need
  removed from the Rolling archive to remove the package from the archive. This
  will avoid breaking the installability of any other explicitly introduced
  packages in Rolling, but may remove packages in Rolling that do not yet have
  equal or newer versions present in Testing. Requires drk's rolling package
  list to be up-to-date, and makes permanent changes to that list. Use with
  care!
* `clean-archive` - Finds all packages in Rolling with equal or newer versions
  present in Testing, and lists them. Also removes outdated packages from drk's
  rolling package list.

## drk Rolling Package List File Format

`bin-package version no-recommends no-suggests`
`src-package version no-recommends no-suggests`

## License

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, see <https://www.gnu.org/licenses/>.