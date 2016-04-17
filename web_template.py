"""
Benchmark for twisted.web.template rendering.
"""
from StringIO import StringIO
from time import time

from twisted.internet.defer import succeed
from twisted.web.template import (
    Element, flatten, renderer, TagLoader, tags, XMLString)

from benchlib import driver



class Elem(Element):
    loader = XMLString(
        """
        <div xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1">
        """ + "A" * 1000 + """
        <div t:render="r" />
        <div t:render="r2" />
        <div t:render="r3">
        <t:slot name="meep" />
        </div>
        </div>
        """)


    def __init__(self, children=[]):
        super(Elem, self).__init__()
        self.children = children

    @renderer
    def r(self, req, tag):
        return tag(
            [self.children,
             u'hi mom!'],
            attr=u'value')


    @renderer
    def r2(self, req, tag):
        return tags.div(u'foo', attr=u'value')


    @renderer
    def r3(self, req, tag):
        return tag.fillSlots(
            meep=(u'slotvalue',
                  u'42',
                  'bar',
                  tags.div(u'meep', attr=u'value')))



def render():
    child = Elem()
    for _ in xrange(20):
        child = Elem([child])
    root = TagLoader([child] * 10).load()
    out = StringIO()
    flatten(None, root, out.write)



def main(reactor, duration):
    start = time()
    count = 0
    while time() - start < duration:
        render()
        count += 1
    return succeed(count)



if __name__ == '__main__':
    import sys
    import web_template
    driver(web_template.main, sys.argv)
