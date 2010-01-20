"""saxns -- a namespace-aware SAX ContentHandler"""

import re, collections
from xml import sax

__all__ = ('XMLError', 'ContentHandler', 'parser')

class XMLError(Exception): pass

def parser(handler=None):
    """A shortcut for sax.make_parser() followed by a
    setContentHandler()."""
    parse = sax.make_parser()
    if handler:
        parse.setContentHandler(handler)
    return parse


### ContentHandler

class ContentHandler(object):
    """This ContentHandler provided generates *PrefixMapping and
    *ElementNS events from *Element events.  This can be used to act
    on namespace events when the underlying XMLReader is not namespace
    aware.

    A subclass of this ContentHandler can implement the *PrefixMapping
    and *ElementNS event handlers and behave as if the underlying
    reader supports namepsaces.  One caveat is that the qualified
    names of opening and closing tags must match since the reader is
    not namespace aware.

    >>> class EchoHandler(ContentHandler):
    ...     def startPrefixMapping(self, prefix, uri):
    ...         print 'start-ns', prefix, uri
    ...
    ...     def endPrefixMapping(self, prefix):
    ...         print 'end-ns', prefix
    ...
    ...     def startElementNS(self, name, qname, attrs):
    ...         print 'start-el', name, attrs
    ...
    ...     def endElementNS(self, name, qname):
    ...         print 'end-el', name
    ...
    ...     def characters(self, data):
    ...         print 'data', data
    ...

    >>> reader = parser(EchoHandler())
    >>> reader.feed('<foo:bar xmlns="urn:DEFAULT" xmlns:foo="urn:FOO">quux</foo:bar>')
    start-ns foo urn:FOO
    start-ns None urn:DEFAULT
    start-el (u'urn:FOO', u'bar') <AttributeNS []>
    data quux
    end-el (u'urn:FOO', u'bar')
    end-ns None
    end-ns foo
    >>> reader.close()
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.nsmap = NSMap({ None: None })
        self._prefix_stack = []
        self._delay_attrs = []
        self._attrs = AttributeNS(self.nsmap)

    ## Implement these in a subclass

    def setDocumentLocator(self, locator):
        pass

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startPrefixMapping(self, prefix, uri):
        pass

    def endPrefixMapping(self, prefix):
        pass

    def startElementNS(self, name, qname, attrs):
        pass

    def endElementNS(self, name, qname):
        pass

    def characters(self, data):
        pass

    def ignorableWhitespace(self, data):
        pass

    def processingInstruction(self, target, data):
        pass

    def skippedEntity(self, name):
        pass

    ## Do not override these

    def startElement(self, qname, attrs):
        nsmap = self.nsmap

        ## First, process the attributes to find any xmlns
        ## declarations.
        frame = []
        delay = self._delay_attrs; del delay[:]
        for (attr_qname, value) in attrs.items():
            (prefix, lname) = prefix_name(attr_qname)

            ## An xmlns="..." attribute is equivalent to
            ## xmlns:None="..."
            if prefix is None and lname == 'xmlns':
                prefix = lname; lname = None

            if prefix == 'xmlns':
                if nsmap.get(lname) != value:
                    frame.append(lname)
                    nsmap[lname] = value
                    self.startPrefixMapping(lname, value)
            else:
                delay.append((prefix, lname, value))

        ## Postprocess non-xmlns attributes.
        _attrs = self._attrs._clear()
        for (prefix, lname, value) in delay:
            _attrs._set(map_xml_name(nsmap, prefix, lname), value)

        ## Process the tag name
        name = map_qname(nsmap, qname)
        self._prefix_stack.append((name, frame))

        ## Dispatch
        self.startElementNS(name, qname, _attrs)

    def endElement(self, qname):
        if not self._prefix_stack:
            raise XMLError('Unexpected closing tag: %r.' % qname)

        nsmap = self.nsmap
        name = map_qname(nsmap, qname)
        (start_name, frame) = self._prefix_stack.pop()

        if name != start_name:
            raise XMLError('Expected closing %r, not %r.' % (
                make_clark_name(start_name),
                make_clark_name(name)
            ))

        self.endElementNS(name, qname)

        for prefix in reversed(frame):
            self.endPrefixMapping(prefix)
            del nsmap[prefix]


### Aux

class NSMap(object):
    """An NSMap maps prefixes to namespace URIs.  It is essentially a
    dictionary, but each prefix is associated with a stack rather than
    a direct mapping.  A reverse mapping of (uri, prefix) items is
    also maintained; use the prefix() method to access it."""

    def __init__(self, data=None):
        self.data = {}
        self.rmap = {}
        if data:
            self.update(data)

    def __repr__(self):
        return '<%s [%s]>' % (
            type(self).__name__,
            ', '.join(repr(i) for i in self.iteritems())
        )

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        uris = self.data.get(key)
        if not uris:
            raise KeyError(key)
        return uris[-1]

    def get(self, key, default=None):
        uris = self.data.get(key)
        return uris[-1] if uris else default

    def prefix(self, uri, default=None):
        prefix = self.rmap.get(uri)
        return prefix[-1] if prefix else default

    def __setitem__(self, key, value):
        self.__set(self.data, key, value)
        self.__set(self.rmap, value, key)

    def __set(self, data, key, value):
        values = data.get(key)
        if not values:
            data[key] = [value]
        elif values[-1] != value:
            values.append(value)

    def __delitem__(self, key):
        uris = self.data.get(key)
        if not uris:
            raise KeyError(key)
        self.__del(self.rmap, uris[-1])
        self.__del(self.data, key)

    def __del(self, data, key):
        values = data.get(key)
        if not values:
            return False

        if len(values) == 1:
            del data[key]
        else:
            values.pop()

        return True

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        return ((k, v[-1]) for (k, v) in self.data.iteritems())

    def update(self, data):
        if isinstance(data, collections.Mapping):
            data = data.iteritems()
        for (key, value) in data:
            self[key] = value

class AttributeNS(object):
    """An implementation of the SAX AttributeNS interface."""

    def __init__(self, nsmap):
        self.nsmap = nsmap
        self.data = {}

    def __repr__(self):
        return '<%s [%s]>' % (
            type(self).__name__,
            ', '.join(repr(i) for i in self.iteritems())
        )

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def copy(self):
        result = AttributeNS(dict(self.nsmap.iteritems()))
        result.data = NSMap(self.data)
        return result

    def get(self, key, default=None):
        self.data.get(key, default)

    def has_key(self, key):
        return key in self.data

    def iterkeys(self):
        return self.data.iterkeys()

    def keys(self):
        return self.data.keys()

    def itervalues(self):
        return self.data.itervalues()

    def values(self):
        return self.data.values()

    def iteritems(self):
        return self.data.iteritems()

    def items(self):
        return self.data.items()

    def _clear(self):
        self.data.clear()
        return self

    def _set(self, key, value):
        self.data[key] = value

    ## AttributeNS Interface

    def getLength(self):
        return len(self)

    def getNames(self):
        return self.keys()

    def getType(self, name):
        return 'CDATA'

    def getValue(self, name):
        return self[name]

    def getValueByQName(self, qname):
        return self.getValue(self.getNameByQName(qname))

    def getNameByQName(self, qname):
        return map_xml_name(self.nsmap(qname))

    def getQNameByName(self, name):
        return map_name(self.nsmap, name)

    def getQNames(self):
        return [map_name(self.nsmap, n) for n in self.iterkeys()]


### Utilities

def close_tag(nsmap, name):
    return '</%s>' % map_name(nsmap, name)

def map_qname(nsmap, qname):
    return map_xml_name(nsmap, *prefix_name(qname))

def map_name(nsmap, name):
    (uri, lname) = name
    return make_prefix_name(nsmap.prefix(uri), lname)

def map_xml_name(nsmap, prefix, lname):
    uri = nsmap.get(prefix)
    if prefix and not uri:
        raise XMLError('Unrecognized prefix: %r.' % make_prefix_name(prefix, lname))
    return (uri, lname)

PREFIX_NAME = re.compile(r'^(?:([^:]+):)?(.+)$')

def prefix_name(name):
    """Parse a name in XML prefix notation to produce a (uri, prefix,
    local-name) item.

    >>> prefix_name('foo')
    (None, 'foo')
    >>> prefix_name('foo:bar')
    ('foo', 'bar')
    """
    probe = PREFIX_NAME.match(name)
    if not probe:
        raise XMLError('Badly formatted XML name: %r.' % name)
    return probe.groups() if probe else (None, name)

def make_prefix_name(uri, lname):
    return '%s:%s' % (uri, lname) if uri else lname

CLARK_NAME = re.compile(r'^{([^}]+)}(.+)$')

def clark_name(name, default=None):
    """Parse a name in Clark notation to produce a (uri, local-name)
    item.

    >>> clark_name('{urn:FOO}bar')
    ('urn:FOO', 'bar')
    >>> clark_name('baz')
    (None, 'baz')
    """
    if isinstance(name, basestring):
        probe = CLARK_NAME.match(name)
        if not probe:
            return (default, name)
        name = probe.groups()
    return name if name[0] else (default, name)

def make_clark_name(name):
    if isinstance(name, basestring):
        return name
    return u'{%s}%s' % name if name[0] else name[1]
