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
#  which.py -- Implement in Python3 what is unavailable on Windows as a
#              which command. Not set up to be a commandline utility but
#              easily re-purposed. Help yourself!
#
# #########################################################################
import os
import os.path
import sys

PATH_DIRS = os.environ['PATH'].split(';')
PATH_DIRS = ['.'] + PATH_DIRS
EXTENSIONS = set(('com', 'bat', 'exe', 'dll', 'cmd', 'ps1'))


def which(prog):
    dot_split_prog = prog.split('.')
    dont_add_extensions = False
    dotless_prog = prog
    while len(dot_split_prog) > 1 and dot_split_prog[-1] == '':
        dot_split_prog = dot_split_prog[:-1]
        dotless_prog = dotless_prog[:-1]
    if len(dot_split_prog) < 1:
        raise ValueError('"." is not a valid command to look for')
    if len(dot_split_prog) > 1 and dot_split_prog[-1].lower() in EXTENSIONS:
        dont_add_extensions = True
    prog_to_check = '.'.join(dot_split_prog)

    for d in PATH_DIRS:
        if not d:
            continue
        path_d = os.path.join(d, prog_to_check)
        if dont_add_extensions:
            if os.path.isfile(path_d):
                return os.path.join(d, prog)
        else:
            for e in EXTENSIONS:
                path_d_e = '.'.join([path_d, e])
                if os.path.isfile(path_d_e):
                    return os.path.join(d, '.'.join([dotless_prog, e]))
    raise FileNotFoundError


if __name__ == '__main__':
    printed = False
    for a in sys.argv[1:]:
        try:
            print(which(a))
            printed = True
        except FileNotFoundError:
            if len(sys.argv) > 2:
                print('No command for {} found in PATH'.format(a))
    if not printed:
        if len(sys.argv) < 3:
            print('Command not found in PATH')
        print('Directories in PATH (look for .cmd, .bat, .ps1, .exe, .com and '
              '.dll here):')
        for d in PATH_DIRS:
            if not d:
                continue
            print('    {}'.format(d))
