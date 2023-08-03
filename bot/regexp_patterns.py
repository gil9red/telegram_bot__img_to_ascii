#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import re

from third_party.regexp import fill_string_pattern


COMMAND_START = "start"
COMMAND_HELP = "help"

PATTERN_CHANGE_SIZE = re.compile("^size=(.+)$")


if __name__ == "__main__":
    assert fill_string_pattern(PATTERN_CHANGE_SIZE, 120) == "size=120"
