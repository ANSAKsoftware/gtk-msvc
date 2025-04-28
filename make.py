#!/usr/bin/env python3

# #########################################################################
#
#  Copyright (c) 2022, Arthur N. Klassen
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
#  2022.02.20 - First version
#
#     May you do good and not evil.
#     May you find forgiveness for yourself and forgive others.
#     May you share freely, never taking more than you give.
#
# #########################################################################
#
#  make.py -- Implement in Python3 what is unavailable on Windows (outside of
#             MinGW / Cygwin), the minimal Makefile-like behaviour of all
#             install, uninstall and a few other things. For more, see
#
#             python3 make.py help
#
# #########################################################################

import argparse

from maker.dirs import MakerDirs
from maker.parts import Levels
from maker.proc import Proc
from maker.target import Target
# from configvars import GENERATOR, PREFIX, COMPILER, MAKE_NSIS, VCVARS
from configvars import PREFIX, MAKE_NSIS


class Maker:

    def __init__(self):
        self.build_dir_ = 'build'
        self.done_ = set()
        self.step_performed_ = False
        self.v_ = False
        self.env_win32_ = ''
        self.env_x64_ = ''
        self.maker_dirs_ = MakerDirs(PREFIX, MAKE_NSIS)

    def valid_order(self, raw_targets):
        valid = []
        if any(t == 'help' for t in raw_targets):
            return ['help']
        if any(t == 'clean' for t in raw_targets):
            valid.append('clean')
        for t in raw_targets:
            if t != 'clean':
                valid.append(t)
        if not valid:
            return ['all']
        return valid

    def read_elements_(self):
        if not hasattr(self, 'levels_'):
            self.levels_ = Levels()
            self.elements_ = self.levels_.elements()

    def prep_elements_(self):
        if hasattr(self, 'targets_'):
            return
        self.targets_ = []
        for element in self.elements_:
            self.targets_.append(Target(element, self.build_dir_))

    def sync_targets_(self):
        for target in self.targets_:
            target.sync()

    def make_all(self):
        self.prep_elements_()
        self.sync_targets_()
        self.maker_dirs_.create_build_dirs()
        for target in self.targets_:
            target.sync()
            target.build()
        self.step_performed_ = True

    def make_install(self):
        self.read_elements_()
        for target in self.targets_:
            target.gather()
        # make sure c:\ProgramData\include exists
        # make sure c:\ProgramData\lib exists
        # make sure c:\ProgramData\bin exists
        self.step_performed_ = True

    def make_uninstall(self):
        self.read_elements_()
        # if any of c:\ProgramData\include, c:\ProgramData\lib or
        # C:\ProgramData\bin do not exist, leave
        for target in self.targets_:
            target.uninstall()
        self.step_performed_ = True

    def make_package(self):
        self.read_elements_()
        self.maker_dirs_.create_nsis_dirs()
        for target in self.targets_:
            target.gather()
        # generate NSIS script
        # run makensis
        self.step_performed_ = True

    def make_clean(self):
        def deleteThese(paths):
            for path in paths:
                if os.path.isdir(path):
                    Proc(CMD, C, 'rmdir', '/s', '/q', path).run()
                elif os.path.isfile(path):
                    Proc(CMD, C, 'del', path).run()

        for d in self.maker_dirs_.build_dirs():
            deleteThese(d)
        self.step_performed_ = True

    def make_scrub(self):
        if os.path.isdir('build'):
            Proc(CMD, C, 'rmdir', '/s', '/q', 'build').run()
        rm_f('configvars.py')
        if os.path.isdir('__pycache__'):
            Proc(CMD, C, 'rmdir', '/s', '/q', '__pycache__').run()
        self.step_performed_ = True
        pass

    def make_help(self):
        print("Makefile simluator for ease-of-deployment on Windows in Win32")
        print("  * help: this message")
        print("  * all: (default target) compile of the libraries (Release)")
        print("  * install: deploy headers and libraries to prefix")
        print("  * uninstall: remove the headers and libraries at prefix")
        print("  * package: build an installer for this source code, place " +
              "it in .\\build (unaffected by prefix setting)")
        print("If you haven't already done so, run .\\configure.cmd before "
              "running .\\make.")
        print("There are some important settings to be determined there.")
        self.step_performed_ = True

    targets = {"all": make_all, "install": make_install,
               "uninstall": make_uninstall, "package": make_package,
               "clean": make_clean, "scrub": make_scrub, "help": make_help}

    def process(self, args):
        self.v_ = bool(args.verbose)
        for target in self.valid_order(args.targets):
            assert target in Maker.targets
            Maker.targets[target](self)
        if not self.step_performed_:
            print('Nothing to do for targets, {}'.format(repr(args.targets)))


def main():
    parser = argparse.ArgumentParser(
                 description="Make script for ansak-string on Windows")
    parser.add_argument('-v', '--verbose',
                        help='more detailed progress messages',
                        action='store_true')
    targets_prompt = 'Things to build. If nothing specified, "all" '
    targets_prompt += 'is assumed. Possible values are: {}'.format(
                      str(Maker.targets.keys()))
    parser.add_argument('targets', help=targets_prompt, type=str, nargs='*')

    Maker().process(parser.parse_args())


if __name__ == '__main__':
    main()
    return 0
