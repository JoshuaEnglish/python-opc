# -*- coding: utf-8 -*-
#
# test_packuri.py
#
# Copyright (C) 2013 Steve Canny scanny@cisco.com
#
# This module is part of python-pptx and is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

"""Test suite for opc.packuri module."""

import pytest

from opc.packuri import PackURI


class DescribePackURI(object):

    def cases(self, expected_values):
        """
        Return list of tuples zipped from uri_str cases and
        *expected_values*. Raise if lengths don't match.
        """
        uri_str_cases = [
            '/',
            '/ppt/presentation.xml',
            '/ppt/slides/slide1.xml',
        ]
        if len(expected_values) != len(uri_str_cases):
            msg = "len(expected_values) differs from len(uri_str_cases)"
            raise AssertionError(msg)
        pack_uris = [PackURI(uri_str) for uri_str in uri_str_cases]
        return zip(pack_uris, expected_values)

    def it_should_raise_on_construct_with_bad_pack_uri_str(self):
        with pytest.raises(ValueError):
            PackURI('foobar')

    def it_can_calculate_baseURI(self):
        expected_values = ('/', '/ppt', '/ppt/slides')
        for pack_uri, expected_baseURI in self.cases(expected_values):
            assert pack_uri.baseURI == expected_baseURI

    def it_can_calculate_filename(self):
        expected_values = ('', 'presentation.xml', 'slide1.xml')
        for pack_uri, expected_filename in self.cases(expected_values):
            assert pack_uri.filename == expected_filename

    def it_can_calculate_membername(self):
        expected_values = (
            '',
            'ppt/presentation.xml',
            'ppt/slides/slide1.xml',
        )
        for pack_uri, expected_membername in self.cases(expected_values):
            assert pack_uri.membername == expected_membername

    def it_can_calculate_rels_uri(self):
        expected_values = (
            '/_rels/.rels',
            '/ppt/_rels/presentation.xml.rels',
            '/ppt/slides/_rels/slide1.xml.rels',
        )
        for pack_uri, expected_rels_uri in self.cases(expected_values):
            assert pack_uri.rels_uri == expected_rels_uri