# Copyright (C) 2018 Tetsuya Miura <miute.dev@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from abc import ABC, abstractmethod
from fractions import Fraction
from io import StringIO
from logging import getLogger

from . import mediaquery as mq
from .core import SVGLength
from .dom import Element, Node
from .element import SVGParser
from .screen import Screen
from .url import Location
from .utils import get_content_type, load, normalize_url


class BrowsingContext(object):
    """A browsing context object that is associated with the document."""

    def __init__(self, document, window_=None):
        """Constructs a browsing context object.

        Arguments:
            document (Document, None): The current document associated with
                the active window.
            window_ (Window, optional): The active window that is associated
                with the current document.
        """
        self._document = document
        if window_ is None:
            global window
            window_ = window
        self._window = window_

    @property
    def document(self):
        """Document: The current document associated with the active window.
        """
        return (self._document if self._document is not None
                else self._window.document)

    @property
    def window(self):
        """Window: The active window that is associated with the current
        document.
        """
        return self._window


class Document(Node):
    """Represents the DOM Document."""

    def __init__(self,
                 content_type=None, default_view=None, document_element=None,
                 implementation=None):
        """Constructs a Document object.

        Arguments:
            content_type (str, optional): The MIME type of the document.
            default_view (Window, optional): The active window that is
                associated with the document.
            document_element (Element, optional): A root element of the
                document.
            implementation (SVGDOMImplementation, optional):
                A DOM implementation object that is associated with the
                document.
        """
        super().__init__()
        self._browsing_context = BrowsingContext(self, default_view)
        self._content_type = (content_type if content_type is not None
                              else 'application/xml')
        if document_element is not None:
            for it in document_element.iter():
                it._owner_document = self
        self._document_element = document_element
        self._implementation = implementation
        if default_view is not None:
            self._location = default_view.location
        else:
            self._location = Location(self._browsing_context)

    @property
    def content_type(self):
        """str: The MIME type of the current document."""
        return self._content_type

    @property
    def default_view(self):
        """Window: The active window that is associated with the current
        document."""
        return self._browsing_context.window

    @property
    def document_element(self):
        """Element: A root element of the current document."""
        return self._document_element

    @property
    def document_uri(self):
        """str: The entire URL of the current document."""
        return self._location.href

    @property
    def implementation(self):
        """DOMImplementation: The DOM implementation object that is associated
        with the current document.
        """
        return self._implementation

    @property
    def location(self):
        """Location: The Location object that is associated with the current
        document.
        If changed, the associated document navigates to the new page.
        """
        return self._location

    @location.setter
    def location(self, src):
        url = normalize_url(src, self._location.href)
        self._location.href = url.tostring()

    @property
    def node_name(self):
        return '#document'

    @property
    def node_type(self):
        return Node.DOCUMENT_NODE

    @property
    def node_value(self):
        return None

    @node_value.setter
    def node_value(self, value):
        pass  # do nothing

    @property
    def origin(self):
        """str: The URL's origin of the current document."""
        return self._location.origin

    @property
    def parent_node(self):
        """Node: A parent node."""
        if self._document_element is None:
            return None
        return self._document_element.getparent()

    @property
    def text_content(self):
        return None

    @text_content.setter
    def text_content(self, text):
        pass  # do nothing

    @property
    def url(self):
        """str: The entire URL of the current document."""
        return self._location.href

    def append_child(self, node):
        """Adds a node to the end of this node.

        Arguments:
            node (Node): A node to be added.
        Returns:
            Node: An appended node.
        """
        if self._document_element is None:
            for it in node.iter():
                if not isinstance(it, Node):
                    raise TypeError('Expected Node, got {} {}'.format(
                        repr(type(it)), hex(id(it))))
                it._owner_document = self
            self._document_element = node
        else:
            self._document_element.append(node)
        return node

    def create_comment(self, data):
        """Creates a new comment instance, and returns it.
        See also SVGParser.create_comment().

        Arguments:
            data (str): A string of the comment.
        Returns:
            Comment: A new comment.
        """
        if self._implementation is None:
            raise ValueError('The object is in the wrong document.')
        comment = self._implementation.create_comment(data)
        return comment

    def create_element(self, local_name, attrib=None, nsmap=None, **_extra):
        """Creates a new element instance, and returns it.
        See also SVGParser.create_element().

        Arguments:
            local_name (str): A local name of an element to be created.
            attrib (dict, optional): A dictionary of an element's attributes.
            nsmap (dict, optional): A map of a namespace prefix to the URI.
            **_extra: See lxml.etree._Element.makeelement() and
                lxml.etree._BaseParser.makeelement().
        Returns:
            Element: A new element.
        """
        if self._implementation is None:
            raise ValueError('The object is in the wrong document.')
        element = self._implementation.create_element_ns(
            None,
            local_name,
            attrib=attrib,
            nsmap=nsmap,
            **_extra)
        return element

    def create_element_ns(self,
                          namespace, qualified_name, attrib=None, nsmap=None,
                          **_extra):
        """Creates a new element instance with the specified namespace URI,
        and returns it.
        See also SVGParser.create_element_ns().

        Arguments:
            namespace (str, None): The namespace URI to associated with
                the element.
            qualified_name (str): A qualified name of an element to be created.
            attrib (dict, optional): A dictionary of an element's attributes.
            nsmap (dict, optional): A map of a namespace prefix to the URI.
            **_extra: See lxml.etree._Element.makeelement() and
                lxml.etree._BaseParser.makeelement().
        Returns:
            Element: A new element.
        """
        if self._implementation is None:
            raise ValueError('The object is in the wrong document.')
        element = self._implementation.create_element_ns(
            namespace,
            qualified_name,
            attrib=attrib,
            nsmap=nsmap,
            **_extra)
        return element

    def get_elements_by_class_name(self, class_names, namespaces=None):
        """Finds all matching sub-elements, by class names.

        Arguments:
            class_names (str): A list of class names that are separated by
                whitespace.
            namespaces (dict, optional): The XPath prefixes in the path
                expression.
        Returns:
            list[Element]: A list of elements.
        """
        root = self._document_element
        if root is None or root.node_type != Node.ELEMENT_NODE:
            raise ValueError('The object is in the wrong document.')
        elements = root.get_elements_by_class_name(
            class_names,
            namespaces=namespaces)
        return elements

    def get_elements_by_tag_name(self, qualified_name, namespaces=None):
        """Finds all matching sub-elements, by the qualified name.

        Arguments:
            qualified_name (str): The qualified name or '*'.
            namespaces (dict, optional): The XPath prefixes in the path
                expression.
        Returns:
            list[Element]: A list of elements.
        """
        root = self._document_element
        if root is None or root.node_type != Node.ELEMENT_NODE:
            raise ValueError('The object is in the wrong document.')
        elements = root.get_elements_by_tag_name(
            qualified_name,
            namespaces=namespaces)
        return elements

    def get_elements_by_tag_name_ns(self,
                                    namespace, local_name, namespaces=None):
        """Finds all matching sub-elements, by the namespace URI and the local
        name.

        Arguments:
            namespace (str, None): The namespace URI, '*' or None.
            local_name (str): The local name or '*'.
            namespaces (dict, optional): The XPath prefixes in the path
                expression.
        Returns:
            list[Element]: A list of elements.
        """
        root = self._document_element
        if root is None or root.node_type != Node.ELEMENT_NODE:
            raise ValueError('The object is in the wrong document.')
        elements = root.get_elements_by_tag_name_ns(
            namespace,
            local_name,
            namespaces=namespaces)
        return elements

    def get_root_node(self):
        """Returns a root node of the current document that contains this node.

        Returns:
            Node: A root node.
        """
        if self._document_element is None:
            return None
        return self._document_element.getroottree().getroot()

    def insert_before(self, node, child):
        """Inserts a node into a parent before a child.

        Arguments:
            node (Node): A node to be inserted.
            child (Node, None): A reference child node.
        Returns:
            Node: A inserted node.
        """
        if child is None:
            return self.append_child(node)
        elif self._document_element is None:
            raise ValueError('The object is in the wrong document.')
        elif child not in self._document_element:
            raise ValueError('The object can not be found here.')
        else:
            child.addprevious(node)
        return node

    def open(self, replace=''):
        """Replaces the current document in-place.
        See also Document.location.

        Arguments:
            replace (str): Reserved.
        Returns:
            Document: Returns itself.
        """
        _ = replace
        url = self._location.href
        logger = getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        logger.debug('navigate to \'{}\''.format(url))
        if self._document_element is not None:
            del self._document_element
            self._document_element = None
        if not url.startswith('about:'):
            root = self._implementation.parse(url)
            self.append_child(root)
        return self

    def remove_child(self, child):
        """Removes a child node from this node.

        Arguments:
            child (Node): A node to be removed.
        Returns:
            Node: A removed node.
        """
        if self._document_element is None:
            raise ValueError('The object is in the wrong document.')
        else:
            self._document_element.remove(child)
        return child

    def replace_child(self, node, child):
        """Replaces a child with node.

        Arguments:
            node (Node): A node to be replaced.
            child (Node, None): A reference child node.
        Returns:
            Node: A replaced node.
        """
        if self._document_element is None:
            raise ValueError('The object is in the wrong document.')
        elif child not in self._document_element:
            raise ValueError('The object can not be found here.')
        else:
            self._document_element.replace(child, node)
        return node

    def write(self, text):
        """Parses an SVG document or fragment from a string, and adds to the
        current document.

        Arguments:
            text (str): An SVG document or fragment.
        """
        root = self._implementation.parse(StringIO(text))
        for it in root.iter():
            if not isinstance(it, Node):
                raise TypeError('Expected Node, got {} {}'.format(
                    repr(type(it)), hex(id(it))))
            it._owner_document = self
        self.append_child(root)

    def writeln(self, text):
        """Same as Document.write().

        Arguments:
            text (str): An SVG document or fragment.
        """
        self.write(text)


class DOMImplementation(ABC):
    """Represents the DOM DOMImplementation."""

    @abstractmethod
    def create_document(self,
                        namespace, qualified_name=None, doctype=None,
                        nsmap=None, **extra):
        """Creates a new XML document instance, and returns it.

        Arguments:
            namespace (str, None): The namespace URI to associated with the
                element.
            qualified_name (str, optional): A qualified name of an element to
                be created.
            doctype (DocumentType, optional): A Document Type of the document.
            nsmap (dict, optional): A map of a namespace prefix to the URI.
            **extra: Reserved.
        Returns:
            XMLDocument: A new XML document.
        """
        raise NotImplementedError


class GenericDOMImplementation(DOMImplementation):
    @abstractmethod
    def create_comment(self, data):
        """Creates a new comment instance, and returns it.

        Arguments:
            data (str): A string of the comment.
        Returns:
            Comment: A new comment.
        """
        raise NotImplementedError

    def create_document(self,
                        namespace, qualified_name=None, doctype=None,
                        nsmap=None, **extra):
        """Creates a new XML document instance, and returns it.

        Arguments:
            namespace (str, None): The namespace URI to associated with the
                element.
            qualified_name (str, optional): A qualified name of an element to
                be created.
            doctype (DocumentType, optional): A Document Type of the document.
                Sets to None.
            nsmap (dict, optional): A map of a namespace prefix to the URI.
            **extra: See Document.__init__().
        Returns:
            XMLDocument: A new XML document.
        """
        _ = doctype
        if namespace == Element.SVG_NAMESPACE_URI:
            content_type = 'image/svg+xml'
        elif namespace == Element.XHTML_NAMESPACE_URI:
            content_type = 'application/xhtml+xml'
        else:
            content_type = 'application/xml'
        if qualified_name is None or len(qualified_name) == 0:
            root = None
        else:
            root = self.create_element_ns(
                namespace,
                qualified_name,
                nsmap=nsmap)
        doc = XMLDocument(content_type=content_type,
                          document_element=root,
                          implementation=self,
                          **extra)
        return doc

    @abstractmethod
    def create_element_ns(self,
                          namespace, qualified_name, attrib=None, nsmap=None,
                          **_extra):
        """Creates a new element instance with the specified namespace URI,
        and returns it.

        Arguments:
            namespace (str, None): The namespace URI to associated with
                the element.
            qualified_name (str): A qualified name of an element to be created.
            attrib (dict, optional): A dictionary of an element's attributes.
            nsmap (dict, optional): A map of a namespace prefix to the URI.
            **_extra: Reserved.
        Returns:
            Element: A new element.
        """
        raise NotImplementedError

    @abstractmethod
    def parse(self, source):
        """Parses an XML document, and returns the root element of it.

        Arguments:
            source (str, file): An URL or a file-like object of an SVG
                document.
        Returns:
            Element: A root element of the document.
        """
        raise NotImplementedError


def _mql_compare(left, right, user_data):
    left_value = SVGLength(left, context=user_data)
    right_value = SVGLength(right, context=user_data)
    if left_value == right_value:
        return 0
    cmp = 1 if left_value > right_value else -1
    return cmp


class MediaQueryList(object):
    """Represents the CSSOM-VIEW MediaQueryList."""

    def __init__(self, browsing_context, query):
        """Constructs a MediaQueryList object.

        Arguments:
            browsing_context (BrowsingContext): A browsing context object that
                is associated with the document.
            query (str): The media query list to be parsed.
        """
        self._browsing_context = browsing_context
        self._query = query
        self._tree = mq.parse(self._query)

    @property
    def matches(self):
        """bool: The matches state of the associated media query list."""
        doc = self._browsing_context.document
        win = self._browsing_context.window
        context = doc.document_element
        if context is not None:
            _, _, vpw, vph = context.get_viewport_size()
            width = vpw.value()
            height = vph.value()
        else:
            width = win.inner_width
            height = win.inner_height
        aspect_ratio = Fraction(int(width), int(height))
        screen = win.screen
        device_aspect_ratio = Fraction(int(screen.width), int(screen.height))
        conditions = {
            'media': screen.media,
            'width': '{}px'.format(width),
            'height': '{}px'.format(height),
            'aspect-ratio': '{}'.format(aspect_ratio),
            'orientation': screen.orientation,
            'resolution': '{}dppx'.format(win.device_pixel_ratio),
            'scan': screen.scan,
            'grid': 0,
            'update': screen.update,
            'overflow-block': 'none',
            'overflow-inline': 'none',
            'color': screen.color_depth,
            'color-index': 1 << screen.color_depth,
            'monochrome': screen.monochrome,
            'color-gamut': screen.color_gamut,
            # deprecated media features
            'device-width': '{}px'.format(screen.width),
            'device-height': '{}px'.format(screen.height),
            'device-aspect-ratio': '{}'.format(device_aspect_ratio),
        }
        matches, _ = mq.match(self._tree, conditions, _mql_compare,
                              user_data=context)
        return matches

    @property
    def media(self):
        """str: The serialized form of the associated media query list."""
        # TODO: serialize a media query list.
        return self._query


class SVGDOMImplementation(GenericDOMImplementation):
    def __init__(self, **kwargs):
        """Constructs an SVGDOMImplementation object.

        Arguments:
            **kwargs: See SVGParser.__init__().
        """
        self._parser = SVGParser(**kwargs)

    @property
    def parser(self):
        """SVGParser: An SVG parser object."""
        return self._parser

    def create_comment(self, data):
        """Creates a new comment instance, and returns it.
        See also SVGParser.create_comment().

        Arguments:
            data (str): A string of the comment.
        Returns:
            Comment: A new comment.
        """
        comment = self._parser.create_comment(data)
        return comment

    def create_element_ns(self,
                          namespace, qualified_name, attrib=None, nsmap=None,
                          **_extra):
        """Creates a new element instance with the specified namespace URI,
        and returns it.
        See also SVGParser.create_element_ns().

        Arguments:
            namespace (str, None): The namespace URI to associated with
                the element.
            qualified_name (str): A qualified name of an element to be created.
            attrib (dict, optional): A dictionary of an element's attributes.
            nsmap (dict, optional): A map of a namespace prefix to the URI.
            **_extra: See lxml.etree._Element.makeelement() and
                lxml.etree._BaseParser.makeelement().
        Returns:
            Element: A new element.
        """
        element = self._parser.create_element_ns(namespace,
                                                 qualified_name,
                                                 attrib=attrib,
                                                 nsmap=nsmap,
                                                 **_extra)
        return element

    def create_svg_document(self, nsmap=None):
        """Creates a new SVG document instance, and returns it.

        Arguments:
            nsmap (dict, optional): A map of a namespace prefix to the URI.
        Returns:
            XMLDocument: A new SVG document.
        """
        doc = self.create_document(Element.SVG_NAMESPACE_URI,
                                   'svg',
                                   nsmap=nsmap)
        return doc

    def parse(self, source):
        """Parses an SVG document, and returns the root element of it.

        Arguments:
            source (str, file): An URL or a file-like object of an SVG
                document.
        Returns:
            Element: A root element of the document.
        """
        if isinstance(source, str):
            data, headers = load(source)
            content_type = get_content_type(headers)
            if content_type is None:
                charset = 'utf-8'
            else:
                charset = content_type.get('charset', 'utf-8')
            data = StringIO(data.decode(charset))
        else:
            data = source
        tree = self._parser.parse(data)
        return tree.getroot()


class Window(object):
    """Represents the Window."""

    def __init__(self, implementation):
        """Constructs a Window object.

        Arguments:
            implementation (DOMImplementation): A DOMImplementation object.
        """
        self._browsing_context = BrowsingContext(None, self)
        self._location = Location(self._browsing_context)
        self._implementation = implementation
        self._document = self._implementation.create_document(
            Element.SVG_NAMESPACE_URI,
            default_view=self)
        self._screen = Screen()
        self._inner_width = self._screen.width
        self._inner_height = self._screen.height
        self._page_zoom_scale = 1.

    @property
    def device_pixel_ratio(self):
        """float: The result of dividing CSS pixel size by device pixel size
        of the output device.
        """
        return self._screen.device_pixel_ratio * self.page_zoom_scale

    @property
    def document(self):
        """Document: The current document associated with the current window.
        """
        return self._document

    @property
    def inner_height(self):
        """int: The viewport height."""
        return self._inner_height

    @inner_height.setter
    def inner_height(self, height):
        self._inner_height = int(height)

    @property
    def inner_width(self):
        """int: The viewport width."""
        return self._inner_width

    @inner_width.setter
    def inner_width(self, width):
        self._inner_width = int(width)

    @property
    def location(self):
        """Location: The location object that is associated with the current
        document.
        If changed, the associated document navigates to the new page.
        """
        return self._location

    @location.setter
    def location(self, src):
        url = normalize_url(src, self._document.document_uri)
        self._location.href = url.tostring()

    @property
    def page_zoom_scale(self):
        """float: The current zoom scale of the current window."""
        return self._page_zoom_scale

    @page_zoom_scale.setter
    def page_zoom_scale(self, scale):
        self._page_zoom_scale = float(scale)

    @property
    def screen(self):
        """Screen: The Screen object that is associated with the current
        window.
        """
        return self._screen

    def match_media(self, query):
        """Returns a new MediaQueryList object, with the context object’s
        associated Document, with parsed media query list as its associated
        media query list.

        Arguments:
            query (str): The media query list to be parsed.
        Returns:
            MediaQueryList: A new MediaQueryList object.
        """
        mql = MediaQueryList(self._browsing_context, query)
        return mql


class XMLDocument(Document):
    """Represents the DOM XMLDocument."""
    pass


window = Window(SVGDOMImplementation())
