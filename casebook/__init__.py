#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

CP = 'utf-8'

class LogOnError(Exception):
    '''raise this exception when LogOn request to casebook.ru failed
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return u"%s" % (self.value, )
