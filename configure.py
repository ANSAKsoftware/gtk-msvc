#!/usr/bin/env python3

# #########################################################################
#
#  Copyright (c) 2025, Arthur N. Klassen
#  All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# #########################################################################
#
#  2022.02.20 - First version
#
#     May you do good and not evil.
#     May you find forgiveness for yourself and forgive others.
#     May you share freely, never taking more than you give.
#
# #########################################################################
#
#  configure.py -- Implement in Python3 what is unavailable on Windows
#                  (outside of MinGW / Cygwin), the minimal autoconf/automake-
#                  like behaviour of the config shell script provided for use
#                  in Linux / MinGW/Cygwin, macOS. For more, see
#
#                  python3 configure.py --help
#
# #########################################################################

import sys
import which
import os
import os.path
import argparse
import pathlib
from subprocess import STDOUT, PIPE
import subprocess

called_by = 'python'
compiler = None
v = False

DEFAULT_PREFIX = 'C:\\ProgramData'
DEFAULT_MAKENSIS_LOCATION = 'C:\\Program Files (x86)\\NSIS\\makensis.exe'


def run_it(*args):
    try:
        p = subprocess.Popen(args, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        return [line.decode('utf-8') for line in p.stdout.readlines()]
    except FileNotFoundError:
        return None


def ensure_yaml():
    try:
        import yaml     # noqa: F401
    except ModuleNotFoundError:
        print("project requires pyyaml, most easily done by running:")
        print("    pip3 install pyyaml")
        sys.exit(1)


def ensure_patch():
    try:
        import patch    # noqa: F401
    except ModuleNotFoundError:
        print("project requires patch, most easily done by running:")
        print("    pip3 install patch")
        sys.exit(1)


def ensure_gendef():
    # ensure presence of gendef.exe on the path
    try:
        which.which('gendef')
    except FileNotFoundError:
        print("project requires gendef, from the cygwin/mingw tools, or from:")
        print("    git clone https://.....")
        sys.exit(1)


def locate_vcvars_files():

    def drive_letters():
        letters = []
        for ch in range(ord('a'), ord('z') + 1):
            c = chr(ch)
            if os.path.exists('{}:'.format(c)):
                letters.append(c)
        return letters

    def find_files_by_name(drive_letter, file_glob):
        print("searching for {} in drive {}:".format(file_glob, drive_letter))
        search_target = r'{}:\{}'.format(drive_letter, file_glob)
        raw_lines = run_it('cmd.exe', '/c', 'dir', '/s', '/b', search_target)
        lines = [line.strip() for line in raw_lines]
        if len(lines) < 1:
            return []
        elif len(lines) == 1 and lines[0] == "File Not Found":
            return []
        return lines

    drives = drive_letters()
    vcvars_32 = []
    vcvars_64 = []
    for d in drives:
        vcvars_32 += find_files_by_name(d, 'vcvars32.*')
        vcvars_64 += find_files_by_name(d, 'vcvars64.*')
    if (len(vcvars_32) == 1 or len(vcvars_64) == 1) and (len(vcvars_32) <= 1
                                                         and len(vcvars_64) <=
                                                         1):
        return (vcvars_32[0] if len(vcvars_32) == 1 else '',
                vcvars_64[0] if len(vcvars_64) == 1 else '')
    elif len(vcvars_32) == 0 and len(vcvars_64) == 0:
        print("No settings batch files (e.g. vcvars32.bat) were found on your "
              "system. Re-run")
        print("configure with the --vcvars-32 and/or --vcvars-64 switches to "
              "choose them manually.")
        raise Exception("Could not choose vcvars files automatically (0,0)")
    else:
        print("Multiple settings batch files for 32-bit and 64-bit were found "
              "on your system:")
        print("These vcvars32 files were found: {}".format(
              ", ".join(vcvars_32)))
        print("These vcvars64 files were found: {}".format(
              ", ".join(vcvars_64)))
        print("Re-run configure with the --vcvars-32 and --vcvars-64 switches "
              "to choose them manually.")
        message = "Could not choose vcvars files automatically ({},{})"
        message = message.format(len(vcvars_32), len(vcvars_64))
        raise Exception(message)


def find_generator():
    cmake_help_lines = run_it('cmake', '--help')
    if v:
        print("Read {} lines from cmake --help".format(len(cmake_help_lines)))
    studio_lines = [line.strip() for line in cmake_help_lines
                    if "Visual Studio" in line]
    if v:
        print("Read {} Visual Studio generator lines from cmake --help".format(
              len(studio_lines)))
    starred = [line for line in studio_lines if line.startswith('*')]
    if v:
        print("Read {} starred generator line(s) from cmake --help".format(
              len(starred)))
        for s in starred:
            print("   {}".format(s))

    if len(starred) == 0:
        print("No default Visual Studio generator. Install Visual Studio")
        sys.exit(1)
    elif len(starred) > 1:
        print("{} default Visual Studio generators? Something is wrong".format(
              len(starred)))
        sys.exit(1)
    else:
        star_line = starred[0][1:]
        star_left_half = star_line.split('=')[0].strip()
        star_before_bracket = star_left_half.split('[')[0].strip()
        if v:
            print("Default Visual Studio generator found: {}".format(
                  star_before_bracket))
        return star_before_bracket


def find_make_nsis(loc):
    nsis_lines = run_it(loc, '/VERSION')
    if not nsis_lines:
        if v:
            print("""No makensis was found at {}, 'make package' will not be
available.

MakeNSIS can be downloaded from https://nsis.sourceforge.io/Download -- choose
version 3 or later""".format(loc))
        return None
    nsis_output = nsis_lines[0].strip()
    if nsis_output[0] != 'v':
        print("Unrecognized output from makensis /VERSION: {}".format(
              nsis_output))
        return None
    version_string = nsis_output[1:]
    version_parts = version_string.split('.')
    try:
        if int(version_parts[0]) < 3:
            print("Earlier version of makensis, may not work.")
    except ValueError:
        print("Unrecognized version from makensis /VERSION: {}".format(
              version_string))
        return None
    if v:
        print("Makensis was found at {}, 'make package' will be available.".
              format(loc))
    return loc


def main(argv=sys.argv):
    global v

    parser = argparse.ArgumentParser(
            description="Configure script for ansak-string on Windows")
    parser.add_argument('--prefix',
                        help='non-default location to install files (does not '
                             'affect \'make package\')',
                        type=str,
                        default=DEFAULT_PREFIX)
    parser.add_argument('--compiler',
                        help='alternative C++ compiler to use',
                        type=str)
    parser.add_argument('--make-nsis',
                        help='location of package builder, NullSoft '
                             'Installation System',
                        type=str, default=DEFAULT_MAKENSIS_LOCATION)
    parser.add_argument('-v', '--verbose',
                        help='more detailed progress messages',
                        action='store_true')

    args = parser.parse_args()
    v = bool(args.verbose)

    ensure_yaml()
    ensure_patch()
    ensure_gendef()
    (vcvars32, vcvars64) = locate_vcvars_files()
    vcvars = vcvars64 if vcvars64 is not None else vcvars32

    # determine ... prefix, compiler, MSDev generator
    prefix = os.path.realpath(args.prefix)
    if not os.path.isdir(prefix):
        pathlib.Path(prefix).mkdir(parents=True, exist_ok=True)
    if not os.path.isdir(prefix):
        raise Exception("Prefix is not an available directory: {}".format(
                        prefix))
    if args.compiler:
        compiler = repr(args.compiler)
    else:
        compiler = None

    generator = find_generator()

    make_nsis = find_make_nsis(args.make_nsis)

    # write configvars.py with generator, prefix, compiler values
    vcvars_out = repr(vcvars)
    with open('configvars.py', 'w') as configs:
        print('GENERATOR = {}'.format(repr(generator)), file=configs)
        print('PREFIX = {}'.format(repr(prefix)), file=configs)
        print('COMPILER = {}'.format(repr(compiler)), file=configs)
        print('MAKE_NSIS = {}'.format(repr(make_nsis)), file=configs)
        print('VCVARS = {}'.format(vcvars_out), file=configs)
    if v:
        print('Created configvars.py file with values:')
        print('    GENERATOR = {}'.format(repr(generator)))
        print('    PREFIX = {}'.format(repr(prefix)))
        print('    COMPILER = {}'.format(repr(compiler)))
        print('    MAKE_NSIS = {}'.format(repr(make_nsis)))
        print('    VCVARS = {}'.format(vcvars_out))

    # write make.cmd running python make.py %*
    with open('make.cmd', 'w') as makebat:
        print('@{} make.py %*'.format(called_by), file=makebat)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    elif not sys.argv[1].startswith('-'):
        called_by = sys.argv[1]
        replacement = [sys.argv[0]]
        replacement = replacement + sys.argv[2:]
        sys.argv = replacement
    main()
