import cjson
from django.template import Library, Node, Context, TemplateSyntaxError
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter
def json(value):
    return cjson.decode(value)
json = stringfilter(json)

@register.filter
def item(value, arg):
    return value[unicode(arg)]


class WithJsonNode(Node):
    def __init__(self, var, name, nodelist):
        self.var = var
        self.name = name
        self.nodelist = nodelist

    def __repr__(self):
        return "<WithJsonNode>"

    def render(self, context):
        val = self.var
        context.push()
        context[self.name] = val
        output = self.nodelist.render(context)
        context.pop()
        return output

def do_withjson(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 4 or bits[2] != "as":
        raise TemplateSyntaxError("%r expected format is 'value as name'" %
                                  bits[0])
    obj = cjson.decode(parser.compile_filter(bits[1]).resolve(Context()))
    name = bits[3]
    nodelist = parser.parse(('endwith',))
    parser.delete_first_token()
    return WithJsonNode(obj, name, nodelist)
do_withjson = register.tag('withjson', do_withjson)

