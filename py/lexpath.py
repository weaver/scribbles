#!/usr/bin/env python

"""lexpath -- lexical analysis of an XPath expression

This depends on PLY <http://www.dabeaz.com/ply/>:

    easy_install ply

Example:

    > lexpath.py 'child::*[self::chapter or self::appendix][position()=last()]'
    LexToken(AXIS,'child',1,0)
    ...
"""

import sys, re
from ply import lex
from pykk.lib import profile

def usage():
    print __doc__
    print 'usage: %s expression' % sys.argv[0]
    sys.exit(1)

def expression(xml):
    """ExprToken: <http://www.w3.org/TR/xpath/#exprlex>"""

    tokens = [
        'BRACKET',
        'ABBREV',
        'NUMBER',
        'LITERAL',
        'VARIABLE',
        'NAME',
        'FUNCTION'
    ]

    reserved = {
        ## [6] AxisName
        'ancestor': 'AXIS',
        'ancestor-or-self': 'AXIS',
        'attribute': 'AXIS',
        'child': 'AXIS',
        'descendant': 'AXIS',
        'descendant-or-self': 'AXIS',
        'following': 'AXIS',
        'following-sibling': 'AXIS',
        'namespace': 'AXIS',
        'parent': 'AXIS',
        'preceeding': 'AXIS',
        'preceeding-sibling': 'AXIS',
        'self': 'AXIS',

        ## [33] OperatorName
        'and': 'OPERATOR',
        'or': 'OPERATOR',
        'mod': 'OPERATOR',
        'div': 'OPERATOR',

        ## [38] NodeType
        'comment': 'NTYPE',
        'text': 'NTYPE',
        'processing-instruction': 'NTYPE',
        'node': 'NTYPE'
    }

    tokens.extend(set(reserved.itervalues()))

    ## [28] ExprToken
    t_BRACKET = r'\(|\)|\[|\]'
    t_ABBREV = r'\.{1,2}|@|,|::'

    ## [30] Number / [31] Digits
    def t_NUMBER(t):
        r'\d+(?:\.\d*)?|\.\d+'
        t.value = (float if '.' in t.value else int)(t.value)
        return t

    ## [29] Literal
    t_LITERAL = r'"([^"]*)"|\'([^\']*)\''

    ## [32] Operator  / [34] MultiplyOperator
    t_OPERATOR = r'\*|/|//|\||\+|\-|=|!=|<|<=|>|>='

    ## [36] VariableReference
    t_VARIABLE = r'\$(%(qname)s)' % xml

    ## [37] NameTest / [35] FunctionName (FIXME: not actual NCName or QName)
    @lex.TOKEN(ur'\*|%(ncname)s:\*|%(qname)s' % xml)
    def t_NAME(t):
        t.type = reserved.get(t.value, 'NAME')
        return t

    ## [39] ExprWhitespace
    t_ignore = ' \t\n\r'

    def t_error(t):
        print 'Illegal character %r at %r' % (t.value[0], t.value[0:15])

    return lex.lex(reflags=re.UNICODE)

def xml(extended=False):
    """XML tokens

    <http://www.w3.org/TR/REC-xml/#NT-NameStartChar>
    <http://www.w3.org/TR/REC-xml-names/#NT-QName>

    With extended=True, the full range of unicode name characters are
    used for identifiers.  This seems to affect the load-time of a
    script by a few tenths of a second (maybe due to compilation?).
    The execution time of the lexer seems unaffected.
    """

    xml = {}

    ## [4] NameStartChar
    xml['start'] = ur'[A-Za-z_%s]'
    if extended:
        xml['start'] %= (
            ur'\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D'
            ur'\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF'
            ur'\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD'
         )
    else:
        xml['start'] %= u''

    ## [4a] NameChar
    xml['name'] = ur'%(start)s|[\-\.0-9%%s]' % xml
    if extended:
        xml['name'] %= ur'\u00B7\u0300-\u036F\u203F-\u2040'
    else:
        xml['name'] %= u''

    ## [4] NCName
    xml['ncname'] = ur'%(start)s(?:%(name)s)*' % xml

    ## [7] QName
    xml['qname'] = ur'%(ncname)s(?::%(ncname)s)?' % xml

    return xml

def main(path):
    expr = expression(xml())
    expr.input(path)
    while True:
        tok = expr.token()
        if not tok:
            break
        print tok


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    main(sys.argv[1])

