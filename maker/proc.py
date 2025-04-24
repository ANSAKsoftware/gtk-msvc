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
#  proc.py - Wrapper for executing command line tools
#
# #########################################################################

import os
import subprocess

CMD = 'c:\\windows\\system32\\cmd.exe'
C = '/c'

GIT = 'git'


class Proc:

    def __init__(self, *args, consume=False, env=None, cwd=None):
        try:
            self.lines_ = []
            self.rc_ = None
            self.consume_ = consume
            extras = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE,
                      'stderr': subprocess.STDOUT} if consume else {}
            if cwd:
                extras['cwd'] = cwd
            if env:
                env.update(os.environ)
                extras['env'] = env
            self.p_ = subprocess.Popen(args, **extras)
        except FileNotFoundError:
            self.p_ = None
            self.rc_ = 9009

    def rc(self):
        if self.rc_ is not None:
            return self.rc_
        if self.consume_:
            self.lines_ += self.p_.stdout.readlines()
        self.rc_ = self.p_.wait()
        return self.rc_

    def lines(self):
        if self.rc_ is None and self.consume_:
            self.lines_ += self.p_.stdout.readlines()
        return self.lines_

    def ok(self):
        return self.rc() == 0


def cmd(*args, **kwargs):
    return Proc(CMD, C, *args, **kwargs)


def proc(*args, **kwargs):
    return Proc(CMD, C, *args, **kwargs)


def git(*args, **kwargs):
    return Proc(CMD, C, GIT, *args, **kwargs)
