# #########################################################################
#
#  Copyright (c) 2025, Arthur N. Klassen
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#
# #########################################################################
#
#  2025.04.09 - First version
#
#     May you do good and not evil.
#     May you find forgiveness for yourself and forgive others.
#     May you share freely, never taking more than you give.
#
# #########################################################################
#
#  dirs.py - File for MakerDirs class used in make.py
#
# #########################################################################

import os
import os.path
import sys
from pathlib import Path


def mkdir_(dir_value):
    Path(dir_value).mkdir(parents=True, exist_ok=True)
    if not os.path.isdir(dir_value):
        print("FATAL: The directory, %s, could not be created" % (
            dir_value), file=sys.stderr)
        sys.exit(4)


def create_these_(dir_d):
    for dir_key in dir_d:
        mkdir_(dir_d[dir_key])


class MakerDirs:

    def __init__(self, prefix, make_nsis=''):
        self.prefix_ = prefix
        self.has_nsis_ = bool(make_nsis)
        self.build_dirs_ = {}
        self.install_dirs_ = {}
        self.nsis_dests_ = {}
        self.root_ = os.getcwd()

    def build_dirs(self):
        if self.build_dirs_:
            return self.build_dirs_
        proj_build = os.path.join(self.root_, 'build')
        proj_lib = os.path.join(proj_build, 'lib')
        proj_bin = os.path.join(proj_build, 'bin')
        self.build_dirs_ = {'build-root': proj_build,
                            'src-root': os.path.join(proj_build, 'source'),
                            'build': os.path.join(proj_build, 'build'),
                            'include': os.path.join(proj_build, 'include'),

                            'lib_root': proj_lib,
                            'lib_win32': os.path.join(proj_lib, 'Win32'),
                            'lib_x64': os.path.join(proj_lib, 'x64'),
                            'lib_arm64': os.path.join(proj_lib, 'arm64'),

                            'bin_root': proj_bin,
                            'bin_win32': os.path.join(proj_bin, 'Win32'),
                            'bin_x64': os.path.join(proj_bin, 'x64'),
                            'bin_arm64': os.path.join(proj_bin, 'arm64')}
        return self.build_dirs_

    def install_dests(self):
        if self.install_dirs_:
            return self.install_dirs_
        include_root = os.path.join(self.prefix_, 'include')
        lib_root = os.path.join(self.prefix_, 'lib')
        bin_root = os.path.join(self.prefix_, 'bin')
        self.install_dirs_ = {'bin': bin_root, 'include': include_root,
                              'lib_root': lib_root,
                              'lib_win32': os.path.join(lib_root, 'Win32'),
                              'lib_x64': os.path.join(lib_root, 'x64'),
                              'lib_arm64': os.path.join(lib_root, 'arm64'),
                              'bin_win32': os.path.join(bin_root, 'Win32'),
                              'bin_x64': os.path.join(bin_root, 'x64'),
                              'bin_arm64': os.path.join(bin_root, 'arm64')}
        return self.install_dirs_

    def nsis_dests(self):
        if self.has_nsis_:
            if self.nsis_dests_:
                return self.nsis_dests_
            self.nsis_dests_ = {'nsis': os.path.join('build', 'nsis')}

            return self.nsis_dests_
        else:
            return {}

    def create_build_dirs(self):
        create_these_(self.build_dirs())
        create_these_(self.install_dests())

    def create_nsis_dirs(self):
        create_these_(self.nsis_dests())

    def root(self): return self.root_

    def build_root(self): return self.build_dirs()['build-root']

    def build_dir(self): return self.build_dirs()['build']

    def source_dir(self): return self.build_dirs()['src-root']

    def include_dir(self): return self.build_dirs()['include']

    def lib_dir(self, arch=None):
        if arch is None:
            return self.build_dirs()['lib']
        else:
            return self.build_dirs()['lib_{}'.format(arch.lower())]

    def bin_dir(self, arch=None):
        if arch is None:
            return self.build_dirs()['bin']
        else:
            return self.build_dirs()['bin_{}'.format(arch.lower())]

    def patches_dir(self):
        return os.path.join(self.root_, 'patches')
