import re
from django.template import Library, Node, Context, TemplateSyntaxError
from django.template.defaulttags import ForNode

CONNECTION_VAR = '_db_connection'

register = Library()

class NoRowsReturned(ValueError):
    pass

class ManyRowsReturned(ValueError):
    pass


def _parse_expr(parser, token):
    bits = list(token.split_contents())
    expr = ' '.join(bits[1:])

    res = []
    upto = 0
    for match in re.finditer(r'\{\{(.*?)\}\}', expr):
        if upto < match.start():
            res.append(expr[upto:match.start()])
        res.append(parser.compile_filter(match.group(1)))
        upto = match.end()
    if upto < len(expr):
        res.append(expr[upto:])

    # TODO allow ?-bindings
###    if len(bits) != 2:
###        raise TemplateSyntaxError("%r expected format is 'field1, field2, ... FROM ...'" %
###                                  bits[0])
    return res


class SelectNode(Node):
    child_nodelists = ('nodelist',)

    def __init__(self, expr, nodelist, connection_var=CONNECTION_VAR):
        self.expr = expr
        self.nodelist = nodelist
        self.connection_var = connection_var

    def __repr__(self):
        return "<SelectNode %s>" % self.expr
    
    def execute_query(self, context):
        expr = ''.join(unicode(v.resolve(context, True)) if hasattr(v, 'resolve') else v for v in self.expr)
        cursor = context[self.connection_var].cursor()
        try:
            cursor.execute('SELECT %s' % expr)
        except Exception:
            import sys
            print >>sys.stderr, 'Error executing SELECT %s' % expr
            raise

        return cursor

    def render_row(self, context, data, cursor):
        context.push()
        assert len(data) == len(cursor.description)
        for desc, value in zip(cursor.description, data):
            context[desc[0]] = value
        output = self.nodelist.render(context)
        context.pop()
        return output

    def render(self, context):
        cursor = self.execute_query(context)
        data = cursor.fetchone()
        if data is None:
            raise NoRowsReturned()
        if cursor.fetchone() is not None:
            raise ManyRowsReturned()
        return self.render_row(context, data, cursor)

def do_select(parser, token):
    expr = _parse_expr(parser, token)
    nodelist = parser.parse(('endselect',))
    parser.delete_first_token()
    return SelectNode(expr, nodelist)
do_select = register.tag('select', do_select)


class _SequenceResolver(object):
    def __init__(self, parent):
        self.parent = parent

    def resolve(self, context, junk):
        cursor = self.parent.execute_query(context)
        res = cursor.fetchall()
        self.parent.loopvars = [desc[0] for desc in cursor.description]
        if len(cursor.description) == 1:
            return (x for (x,) in res)
        else:
            return res

class ForSelectNode(ForNode, SelectNode):

    def __init__(self, expr, nodelist_loop, nodelist_empty=None, connection_var=CONNECTION_VAR):
        SelectNode.__init__(self, expr, connection_var)
        ForNode.__init__(self, '?', _SequenceResolver(self), False, nodelist_loop, nodelist_empty)

def do_forselect(parser, token):
    expr = _parse_expr(parser, token)
    nodelist_loop = parser.parse(('empty', 'endforselect',))
    token = parser.next_token()
    if token.contents == 'empty':
        nodelist_empty = parser.parse(('endforselect',))
        parser.delete_first_token()
    else:
        nodelist_empty = None
    return ForSelectNode(expr, nodelist_loop, nodelist_empty)
do_forselect = register.tag("forselect", do_forselect)

