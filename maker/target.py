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
#  target.py - File for building a target
#
# #########################################################################

import os
import os.path
import shutil
import sys
from . import dirs
from . import parts
from . import proc

Element = parts.Element
Proc = proc.Proc
mkdir = dirs.mkdir_

ARCH_Win32 = "Win32"
ARCH_X64 = "x64"

ARCHS = [ARCH_Win32, ARCH_X64]

BUILD_RELEASE = "Release"


class Builder:

    def __init__(self, builder_name):
        self.builder_name_ = builder_name
        self.bob_ = None
        self.last_rc_ = 0
        self.dirs_ = {}

    def pre_build(self, target):
        for A in ARCHS:
            self.dirs_[A] = os.path.join(target.build_dir(), A)
            mkdir(self.dirs_[A])
            p = proc.proc('cmake', target.script_path(), '-A', A,
                          cwd=self.dirs_[A], consume=True)
            if not p.ok():
                print("ERROR: CMake parsing failed for {}".format(
                      target.name()), file=sys.stderr)
                sys.exit(p.rc())

    def build(self, build_target):
        for A in self.dirs_:
            p = proc.proc('cmake', '--build', '.', '--config', BUILD_RELEASE,
                          '-t', build_target, cwd=self.dirs_[A], consume=True)
            p.ok()

    def post_build(self):
        pass


class Target:

    def __init__(self, element, maker_dirs, archs=None):
        global ARCHS
        self.dirs_ = maker_dirs
        if archs:
            ARCHS = archs

        self.element_ = element
        self.source_sub_dir_ = os.path.join(self.dirs_.source_dir(),
                                            self.element_.name())
        self.build_sub_dir_ = os.path.join(self.dirs_.build_dir(),
                                           self.element_.name())
        self.script_path_ = self.source_sub_dir_ if \
            self.element_.script_path() is None else os.path.join(
                    self.source_sub_dir_, self.element_.script_path())

        self.builder_ = Builder(self.element_.builder_name())

    def name(self):
        return self.element_.name_

    def build_dir(self):
        return self.build_sub_dir_

    def script_path(self):
        return self.script_path_

    def git(self, *args):
        return proc.git(*args, consume=True, cwd=self.source_sub_dir_)

    def apply_patches(self, reverse=False):
        patches = [p for p in self.element_.patches()]
        if patches:
            if reverse:
                patches.reverse()
                for p in patches:
                    patch_file = os.path.join(self.dirs_.patches_dir(), p)
                    self.git("apply", "-R", patch_file).ok()
            else:
                for p in patches:
                    patch_file = os.path.join(self.dirs_.patches_dir(), p)
                    self.git("apply", patch_file).ok()

    def sync(self):
        p = None
        if os.path.isdir(self.source_sub_dir_):
            self.apply_patches(reverse=True)
            cmd = "pull"
            p = self.git("pull")
        else:
            cmd = "clone"
            p = proc.git("clone", self.element_.source(), self.source_sub_dir_,
                         consume=True, cwd=self.dirs_.source_dir())
        if not p.ok():
            print("FATAL: git {} command failed for {}".format(
                cmd, self.element_.name()), file=sys.stderr)
            sys.exit(p.rc())

        if not os.path.isdir(self.source_sub_dir_) and not \
                os.path.isdir(os.path.join(self.source_sub_dir_, ".git")):
            print("FATAL: The project source for %s could not be cloned" %
                  (self.element_.name()), file=sys.stderr)
            sys.exit(p.rc())

        cmd = "submodule"
        p = self.git("submodule", "update", "--init")
        if p.ok():
            cmd = "status"
            p = self.git("status")
        if not p.ok():
            print("FATAL: git {} command failed for {}".format(
                    cmd, self.element_.name()), file=sys.stderr)
            sys.exit(p.rc())

        self.apply_patches()

    def build(self):
        mkdir(self.build_sub_dir_)
        if self.builder_ is not None:
            self.builder_.pre_build(self)
            for t in self.element_.targets():
                self.builder_.build(t)
            self.builder_.post_build()

    def gather(self):
        # copy headers from the source to the destination
        header_dict = self.element_.headers()
        for h in header_dict:
            # source is the key, dest sub-dir off include is the value;
            # '.' for none
            source = os.path.join(self.source_sub_dir_, h)
            if header_dict[h] == '.':
                dest = self.dirs_.include_dir()
            else:
                dest = os.path.join(self.dirs_.include_dir(), header_dict['h'])
                mkdir(dest)
            shutil.copy2(source, dest)
        # copy .lib's / .dll's from build to the destination
        for deliv in self.element_.deliverables():
            if deliv[-3:].lower() == 'lib':
                for A in ARCHS:
                    shutil.copy2(os.path.join(self.build_sub_dir_, A, deliv),
                                 self.dirs_.lib_dir(A))
            else:
                assert deliv[-3:].lower() == 'dll'
                for A in ARCHS:
                    shutil.copy2(os.path.join(self.build_sub_dir_, A, deliv),
                                 self.dirs_.bin_dir(A))
