#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook http lib module

http://docs.python-requests.org/en/latest/community/faq/
http://stackoverflow.com/questions/13030095/how-to-save-requests-python-cookies-to-a-file
'''

import requests
import requests.utils
import pickle
import os

import casebook
import casebook.const as const
import casebook.utils as utils

CP = casebook.CP

class HttpSession(object):
    """ requests session wrapper
    """

    def __init__(self):
        '''HttpSession constructor'''
        self.session = requests.Session()


    def restoreCookies(self, fname):
        '''Load http cookies from file'''
        self.cookiesFileName = fname
        if os.path.isfile(fname):
            with open(fname) as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
                self.session.cookies = cookies

    def saveCookies(self, fname=''):
        '''Save http cookies to file'''
        if fname == '':
            fname = self.cookiesFileName
        with open(fname, 'w') as f:
            pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

    def deleteCookies(self):
        '''delete all cookies'''
        cookies = requests.utils.cookiejar_from_dict({})
        self.session.cookies = cookies

    def setHeaders(self, dictHeaders):
        '''Set http requests headers from dict.

        dictHeaders example:
            {"Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"}
        '''
        self.session.headers.update(dictHeaders)


    def get(self, url, **kwargs):
        '''Send HTTP GET requests and return Response object.
        http://docs.python-requests.org/en/latest/api/#requests.Response

        http://requests.readthedocs.org/en/latest/user/quickstart/#timeouts
        http://docs.python-requests.org/en/latest/api/#requests.request
        http://stackoverflow.com/questions/21965484/timeout-for-python-requests-get-entire-response
        '''
        if not kwargs.get('timeout', ''):
            kwargs['timeout'] = const.REQUESTS_TIMEOUT

        print u"HttpSession.get from '%s' with params '%s'" % (url, utils.toJsonCompact(kwargs))
        res = self.session.get(url, **kwargs)
        # print u"%s" % res.text

        return res


    def post(self, url, data=None, **kwargs):
        '''Send HTTP POST requests and return Response object.
        data parameter may be dict or JSON string, representing POST data.

        http://docs.python-requests.org/en/latest/user/quickstart/#more-complicated-post-requests
        http://docs.python-requests.org/en/latest/api/#requests.Response
        '''
        if not kwargs.get('timeout', ''):
            kwargs['timeout'] = const.REQUESTS_TIMEOUT


        td = utils.fromJson(data) if isinstance(data, str) else data
        td = utils.toJsonCompact(td)
        print u"HttpSession.post from '%s', data '%s', with params '%s'" % (url, td,
            utils.toJsonCompact(kwargs))

        res = self.session.post(url, data=data, **kwargs)
        # print u"%s" % res.text

        return res
# class httpSession(object):
