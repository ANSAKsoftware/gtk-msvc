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
#  parts.py - File for parsing/using level-yamls
#
# #########################################################################

import os
import sys
import yaml


class Element:

    def __init__(self, level_x, name, yaml_content):
        self.name_ = name
        self.yaml_content_ = yaml_content
        self.level_ = level_x
        self.files_ = [] if 'files' not in self.yaml_content_ else \
            self.yaml_content_['files']
        self.patches_ = [] if 'patches' not in self.yaml_content_ else \
            self.yaml_content_['patches']
        self.source_ = '' if 'source' not in self.yaml_content_ else \
            self.yaml_content_['source']
        self.targets_ = [] if 'targets' not in self.yaml_content_ else \
            self.yaml_content_['targets']
        self.headers_ = {} if 'headers' not in self.yaml_content_ else \
            self.yaml_content_['headers']
        self.deliverables_ = [] if 'deliverables' not in self.yaml_content_ \
            else self.yaml_content_['deliverables']
        self.builder_name_ = 'cmake' if 'builder' not in self.yaml_content_ \
            else self.yaml_content_['builder']
        self.prebuild_params_ = [] if 'prebuild_params' not in self.yaml_content_ \
            else self.yaml_content_['prebuild_params']
        self.script_path_ = None if 'script_path' not in self.yaml_content_ \
            else self.yaml_content_['script_path']

    def name(self):
        return self.name_

    def base_level(self):
        return self.level_ == 0

    def source(self):
        return self.source_

    def patches(self):
        return self.patches_

    def additional_files(self):
        return self.files_

    def builder_name(self):
        return self.builder_name_

    def prebuild_params(self):
        return self.prebuild_params_

    def targets(self):
        return self.targets_

    def headers(self):
        return self.headers_

    def deliverables(self):
        return self.deliverables_

    def script_path(self):
        return self.script_path_


class Levels:

    def __init__(self):
        self.yamls_ = [y for y in os.listdir('.') if y[-4:] == 'yaml']
        self.yamls_.sort()
        self.levels_ = []
        for one_yaml in self.yamls_:
            yaml_dict = {}
            try:
                with open(one_yaml, 'r') as yaml_source:
                    yaml_dict = yaml.safe_load(yaml_source)
            except yaml.YAMLError as eyaml:
                print("Loading {} failed: {}".format(one_yaml, eyaml))
                sys.exit(eyaml)
            if not yaml_dict:
                print("Loading {} failed: empty file".format(one_yaml))
                sys.exit(116)
            self.levels_.append(yaml_dict)
        self.elements_ = []
        level_x = 0
        for lev in self.levels_:
            for elem in lev:
                self.elements_.append(Element(level_x, elem, lev[elem]))
            level_x = level_x + 1

    def levels(self):
        return self.levels_

    def elements(self):
        return self.elements_
