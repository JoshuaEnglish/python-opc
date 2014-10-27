# -*- coding: utf-8 -*-
#
# phys_pkg.py
#
# Copyright (C) 2013 Steve Canny scanny@cisco.com
#
# This module is part of python-opc and is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

"""
Provides a general interface to a *physical* OPC package, such as a zip file.
"""

from zipfile import ZIP_DEFLATED, ZipFile
import re

class PhysPkgReader(object):
    """
    Factory for physical package reader objects.
    """
    def __new__(cls, pkg_file):
        return ZipPkgReader(pkg_file)


class PhysPkgWriter(object):
    """
    Factory for physical package writer objects.
    """
    def __new__(cls, pkg_file):
        return ZipPkgWriter(pkg_file)


class ZipPkgReader(object):
    """
    Implements |PhysPkgReader| interface for a zip file OPC package.
    """
    _CONTENT_TYPES_MEMBERNAME = '[Content_Types].xml'

    def __init__(self, pkg_file):
        super(ZipPkgReader, self).__init__()
        self._zipf = ZipFile(pkg_file, 'r')

    def blob_for(self, pack_uri):
        """
        Return blob corresponding to *pack_uri*. Raises |ValueError| if no
        matching member is present in zip archive.
        """
        result = None
        try:
            result = self._zipf.read(pack_uri.membername)
        except KeyError:
            bTypes = [c for c in self._zipf.namelist() if pack_uri.membername in c]
            result = []
            for b in bTypes:
                m = re.search('\[(\d+)\]',b)
                if m is None or len(m.groups()) == 0:
                    continue
                data = self._zipf.read(b)
                if data is None or len(data) == 0:
                    pass #print "Didn't read anything from:", b
                else:
                    result.append((int(m.group(1)),data))
            result = [x[1] for x in sorted(result, key=lambda x: x[0])]
            result =  "\n".join(result)

        return result

    def close(self):
        """
        Close the zip archive, releasing any resources it is using.
        """
        self._zipf.close()

    def content_types_is_dir(self):
        name = self._CONTENT_TYPES_MEMBERNAME+'/'
        for x in self._zipf.namelist():
            if name in x:
                return True
        return False

    @property
    def content_types_xml(self):
        """
        Return the `[Content_Types].xml` blob from the zip package.
        """
        return self._zipf.read(self._CONTENT_TYPES_MEMBERNAME)

    @property
    def content_types_xml_list(self):
        """
        Return the list of content type .pieces from [Content_Types].xml/ dir
        in zip package.
        """
        cTypes = [c for c in self._zipf.namelist() if self._CONTENT_TYPES_MEMBERNAME in c]
        result = []
        for c in cTypes:
            m = re.search('\[Content_Types\].xml/\[(\d+)\]',c)
            if m is None or len(m.groups()) == 0:
                continue
            data = self._zipf.read(c)
            if data is None or len(data) == 0:
                pass #print "Didn't read anything from:", c
            else:
                result.append((int(m.group(1)),data))
        result = [x[1] for x in sorted(result, key=lambda x: x[0])]
        return "\n".join(result)

    def rels_xml_for(self, source_uri):
        """
        Return rels item XML for source with *source_uri* or None if no rels
        item is present.
        """
        readUri = source_uri
        #if readUri == '/':
        readUri = source_uri.rels_uri.membername
        #elif readUri[0] == '/':
        #    readUri = readUri[1:]

        try:
            rels_xml = self._zipf.read(readUri)
        except KeyError:
            rels_xml = None
            try:
                rels = [c for c in self._zipf.namelist() if c.startswith(readUri)]
                result = []
                for r in rels:
                    m = re.search('\[(\d+)\]',r)
                    if m is None or len(m.groups()) == 0:
                        pass
                    data = self._zipf.read(r)
                    if data is None or len(data) == 0:
                        pass
                    else:
                        result.append((int(m.group(1)), data))
                result = [x[1] for x in sorted(result,key=lambda x: x[0])]
                rels_xml = "\n".join(result)
            except Exception, e:
                print e
                rels_xml = None
        return rels_xml


class ZipPkgWriter(object):
    """
    Implements |PhysPkgWriter| interface for a zip file OPC package.
    """
    def __init__(self, pkg_file):
        super(ZipPkgWriter, self).__init__()
        self._zipf = ZipFile(pkg_file, 'w', compression=ZIP_DEFLATED)

    def close(self):
        """
        Close the zip archive, flushing any pending physical writes and
        releasing any resources it's using.
        """
        self._zipf.close()

    def write(self, pack_uri, blob):
        """
        Write *blob* to this zip package with the membername corresponding to
        *pack_uri*.
        """
        self._zipf.writestr(pack_uri.membername, blob)
