################################################################
# zopyx.smartprintng.plone
# (C) 2011,  ZOPYX Limited & Co. KG, D-72070 Tuebingen, Germany
################################################################

""" HTML transformation classes (based on lxml.html) """

import os
import re
import urllib2
import cgi
import tempfile
import inspect
import uuid
import time
import lxml.html


_marker = object()
TRANSFORMATIONS = dict()

def registerTransformation(method):
    """ Decorator to register a method as a transformation"""
    name = method.__name__
    TRANSFORMATIONS[name] = method

def availableTransformations():
    return TRANSFORMATION.keys()

def hasTransformations(transformations):
    available_transformations = availableTransformations()
    for t in transformations:
        if not t in available_transformations:
            return False
    return True

class Transformer(object):

    def __init__(self, transformation_names, context=None, destdir=None):
        self.transformation_names = transformation_names
        self.context = context
        self.destdir = destdir

    def __call__(self, html, input_encoding=None, output_encoding=unicode, return_body=False):

        if not isinstance(html, unicode):
            if not input_encoding:
                raise TypeError('Input data must be unicode')
            html = unicode(html, input_encoding)

        root = lxml.html.fromstring(html)

        for name in self.transformation_names:
            method = TRANSFORMATIONS.get(name)
            params = dict(context=self.context,
                          request=getattr(self.context, 'REQUEST', None),
                          destdir=self.destdir,
                          )
            if method is None:
                raise ValueError('No transformation "%s" registered' % name)

            ts = time.time()
            argspec = inspect.getargspec(method)
            if isinstance(argspec, tuple):
                args = argspec[0] # Python 2.4
            else:
                args = argspec.args
            if 'params' in args:
                method(root, params)
            else:
                method(root)
            LOG.info('Transformation %-30s: %3.6f seconds' % (name, time.time()-ts))

        if return_body:
            body = root.xpath('//body')[0]
            html_new = body.text + u''.join([lxml.html.tostring(b, encoding=output_encoding) for b in body])

        else:
            html_new = lxml.html.tostring(root, encoding=output_encoding)
            if html_new.startswith('<div>') and html_new.endswith('</div>'):
                html_new = html_new[5:-6].strip()

        return html_new.strip()

def xpath_query(node_names):
    if not isinstance(node_names, (list, tuple)):
        raise TypeError('"node_names" must be a list or tuple (not %s)' % type(node_names))
    return './/*[%s]' % ' or '.join(['name()="%s"' % name for name in node_names])


UUID4TAGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'img', 'table', 'li', 'dt', 'ul', 'ol', 'dl')
@registerTransformation
def addUUIDs(root, tags=UUID4TAGS):
    """ Add a unique/random UUID to all (specified) tags """
    for node in root.xpath(xpath_query(tags)):
        node_id = node.get('id', _marker)
        if node_id is _marker:
            node.attrib['id'] = str(uuid.uuid4())

