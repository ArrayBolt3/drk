# drk - Debian Rolling Kit

drk is a set of tools intended to assist in maintaining the Debian Rolling archive. It is designed to be used alongside
dak, the Debian Archive Kit.

drk is designed to run on a machine with a functional dak instance. It may misbehave if run without dak available.

## Synposis

```
drk <action> <argument1> [<argument2> ...]
```

## Actions

* `list-versions <binary-package|src:src-package>` - Shows the versions of a package available in the Unstable, Rolling,
 and Testing archives.
* `generate-dep-list <--full|--fresh|--rolling> [--no-list-recommends] [--no-list-suggests] <src-package>` - Generates a 
  list containing a package and its dependencies. All possible alternative dependencies and all packages providing a
  virtual package are taken into consideration. If `--full` is specified, a complete dependency list is generated based
  on the contents of Unstable. If `--fresh` is specified, only those packages which have updated versions in Unstable
  that aren't already in Testing are listed. If `--rolling` is specified, only those packages that need to be copied
  from Sid to Rolling to introduce the package into Rolling are listed. The `--no-list-recommends` and
  `--no-list-suggests` arguments can be used to suppress showing recommended or suggested packages in the list.
* `add-package [--no-copy-recommends] [--no-copy-suggests] [--restrict-architectures=arch1[,arch2,...]] <src-package>` -
  Copies a source package, all of its binary  packages, and all the source and binary packages of its dependencies from
  Unstable into Rolling, omitting the specified list of architectures.
* `remove-package [--try-remove-depends] [--try-remove-recommends] [--try-remove-suggests]
  [--restrict-architectures=arch1[,arch2,...]] <src-package>` - Removes a package from Rolling, optionally attempting to
  remove as many of its dependencies as possible. Architectures that are specified in `--restrict-architectures` do not
  have the specified packages removed. See section "Cleaning the Archive" below for details on how package removal
  works.
* `clean-archive` - Finds all packages in Rolling that can be safely removed and their dependencies satisfied by
  Testing, and removes them from Rolling. See section "Cleaning the Archive" below for details on how package removal
  works.

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