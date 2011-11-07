#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""
View for return tables, images, anchors etc. through JSON
"""

import re
from ordereddict import OrderedDict

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zopyx.smartprintng.plone.browser.util import _findTextInNode, _findParentDocument
from zopyx.smartprintng.plone import xpath_query

import util

import lxml.html

class MetaInformation(BrowserView):
    """ This view returns informations about tables, images and headings
        for the aggregated HTML of the root content folder as JSON
        data.
    """

    def getMetaInformation(self):

        ref_catalog = getToolByName(self.context, 'reference_catalog')

        # get hold of the root content folder
        try:
            content_folder = self.context.getContentFolder()
        except AttributeError:
            return dict(documents={})

        # and render the aggregated HTML
        html = content_folder.restrictedTraverse('@@asHTML')()
        root = lxml.html.fromstring(html)
    
        documents = OrderedDict()

        for div in root.xpath('//div'):
            if not 'level-0' in div.get('class', ''):
                continue

            uid = div.get('uid')  # of root node
            root_node = ref_catalog.lookupObject(uid)
            documents[uid] = dict(metadata={}, tables=[], images=[], headings=[])
            documents[uid]['metadata']['path'] = div.get('path')
            documents[uid]['metadata']['id'] = div.get('document_id')
            documents[uid]['metadata']['title'] = root_node.Title()
            documents[uid]['metadata']['description'] = root_node.Description()
            documents[uid]['metadata']['url'] = root_node.absolute_url()

            for node in div.xpath(xpath_query(('h1', 'h2', 'h3', 'h4', 'h5'))):
                id = node.get('id')
                level = int(node.tag[1:])
                url = 'resolveuid/%s/#%s' % (uid, id)
                if id:
                    d = dict(id=id,
                             target_url=url,
                             name=node.tag,
                             level=level,
                             text=node.text_content())
                    documents[uid]['headings'].append(d)

            # process images
            for node in div.xpath('//img'):
                id = node.get('id')
                src = node.get('src') 
                if not src:
                    continue
                src_parts = src.split('/')
                if src_parts[-1].startswith('image_'):
                    src = '/'.join(src_parts[:-1])
                elif '@@images' in src:
                    src = '/'.join(src_parts[:src_parts.index('@@images')])
                url = 'resolveuid/%s/#%s' % (uid, id)
                image_url = '%s/%s/image_thumb' % (content_folder.absolute_url(), src)
                if id:
                    d = dict(id=id,
                             target_url=url,
                             image_url=image_url,
                             name=node.tag)
                    documents[uid]['images'].append(d)
                    
                                     
            # process tables
            for node in div.xpath('//table'):
                id = node.get('id')
                if not id:
                    contiue

                # caption + caption
                summary = node.get('summary') or '(table without caption or summary)'
                caption = summary
                if node.xpath('//caption'):
                    caption = node.xpath('//caption')[0].text_content()

                url = 'resolveuid/%s/#%s' % (uid, id)
                d = dict(id=id,
                         target_url=url,
                         name=node.tag,
                         caption=caption)
                documents[uid]['tables'].append(d)

            # process lists
            documents[uid]['lists'] = []
            for list_node in div.xpath(xpath_query(('ol', 'ul', 'dl'))):
                list_items = list()
                for item in list_node.xpath(xpath_query(('li', 'dt'))):
                    item_id = item.get('id')
                    if item_id:
                        url = 'resolveuid/%s/#%s' % (uid, item_id)
                        list_items.append(dict(id=item_id,
                                               target_url=url,
                                               text=item.text_content()))
                documents[uid]['lists'].append(list_items)

        return dict(documents=documents)

