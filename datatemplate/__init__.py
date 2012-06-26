#!/usr/bin/env python
#coding=utf-8
"""
%prog [context-loaders] < input.tpl
%prog [context-loaders] --render input1.tpl output1 [context-loaders] --render input2.tpl output2 ...

Renders Django templates using a context loaded from files:
    - arbitrary json data
    - comma or tab-delimited data as a sequence of tuples
    - sqlite databases, accessed with the {% select %} and {% forselect %} extension tags
    - comma or tab-delimited data as in-memory sqlite tables

Other variables may be set on the command-line using --var and --json-var.
"""

from django.conf import settings
try:
    settings.configure()
except RuntimeError:
    pass # assume already configured

import types
from django.template import Template, Context, add_to_builtins
from datatemplate.template_libs.sql import CONNECTION_VAR
add_to_builtins('datatemplate.template_libs.withjson')
add_to_builtins('datatemplate.template_libs.sql')
add_to_builtins('datatemplate.template_libs.tex')
add_to_builtins('datatemplate.template_libs.numeric')

import csv as csv_
class tab(csv_.Dialect):
    delimiter = '\t'
    quoting = csv_.QUOTE_NONE
    lineterminator = '\n'
csv_.register_dialect('tab', tab)

def render(template, context={}, out=None):
    if hasattr(template, 'read'):
        template = template.read()
    if not hasattr(template, 'render'):
        template = Template(template)

    if type(context) == list:
        context = build_context(context)

    res = template.render(Context(context, autoescape=False))

    if out:
        print >>out, res
    return res


def build_context(makers):
    context = {}
    for maker in makers:
        if callable(maker):
            context.update(maker(context))
        else:
            context.update(maker)
    return context


def sqlite(connection):
    def context_maker(context):
        if CONNECTION_VAR in context:
            raise ValueError('db_connection already in context')
        import sqlite3
        if connection and isinstance(connection, types.StringTypes):
            conn = sqlite3.connect(connection)
        else:
            conn = connection
        return {CONNECTION_VAR: conn}
    return context_maker


def var(name, value):
    return {name: value}


def csvsql(csvfile, connection=None, table='data', **csv_kwargs):
    if not hasattr(csvfile, 'read'):
        csvfile = open(csvfile)
    def context_maker(context):
        from datatemplate.load_libs.csv2sqlite import convert
        connection = convert(csvfile, context.get(CONNECTION_VAR, ':memory:'), table=table, temporary=True, **csv_kwargs)
        return {CONNECTION_VAR: connection}
    return context_maker

def csv(name, csvfile, **csv_kwargs):
    if not hasattr(csvfile, 'read'):
        csvfile = open(csvfile)
    import csv
    return {name: csv.reader(csvfile, **csv_kwargs)}

# TODO: should have linear CSV access: not sure whether to use DictReader

def _json_loads(s):
    try:
        from cjson import decode as loads
    except ImportError:
        try:
            from json import loads
        except ImportError:
            from simplejson import loads
    return loads(s)

def json(name, jsonfile):
    if not hasattr(jsonfile, 'read'):
        jsonfile = open(jsonfile)
    return {name: _json_loads(jsonfile.read())}

def json_var(name, json):
    return {name: _json_loads(json)}


if __name__ == "__main__":
    import sys, optparse

    parser = optparse.OptionParser(usage=__doc__)
    
    def cl_open(path, mode='r'):
        if path == '-':
            if mode.startswith('r'):
                return sys.stdin
            else:
                return sys.stdout
        return open(path, mode)


    def append_context_maker(option, opt_str, value, parser, fn, **kwargs):
        try:
            dest = parser.values.context_makers
        except AttributeError:
            dest = parser.values.context_makers = []

        with_equals = kwargs.pop('with_equals', None)
        without_equals = kwargs.pop('without_equals', None)
        if with_equals and '=' in value:
            kwargs.update(zip(with_equals, value.split('=', 1)))
        elif without_equals:
            kwargs[without_equals] = value
        else:
            parser.error('Could not parse argument to %s: %s' % (opt_str, value))

        try:
            dest.append(fn(**kwargs))
        except Exception, e:
            parser.error('Error while parsing %s: %s' % (opt_str, e))

    def render_template(option, opt_str, value, parser):
        # Build context so far
        context = build_context(parser.values.context_makers)
        parser.values.context_makers = [context]
        parser.values.rendered = True

        in_path, out_path = value
        render(cl_open(in_path), context, cl_open(out_path, 'w'))

    parser.add_option('--json', metavar='NAME=PATH', help='Load a json file',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': json, 'with_equals': ('name', 'jsonfile')})

    parser.add_option('--csv', metavar='NAME=PATH.csv', help='Load a CSV as a sequence of tuples',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': csv, 'with_equals': ('name', 'csvfile')})

    parser.add_option('--tsv', metavar='NAME=PATH.csv', help='Load a TSV as a sequence of tuples',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': csv, 'with_equals': ('name', 'csvfile'), 'dialect': 'tab'})

    parser.add_option('--sqlite', metavar='PATH', help='Load an sqlite database',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': sqlite, 'without_equals': 'connection'})

    parser.add_option('--csvsql', metavar='[TABLE=]PATH.csv', help='Load a CSV into a table (default: data)',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': csvsql, 'with_equals': ('table', 'csvfile'), 'without_equals': 'csvfile'})

    parser.add_option('--tsvsql', metavar='[TABLE=]PATH.csv', help='Load a TSV into a table (default: data)',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': csvsql, 'with_equals': ('table', 'csvfile'), 'without_equals': 'csvfile', 'dialect': 'tab'})

    parser.add_option('--var', metavar='NAME=VALUE', help='Set a string value',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': var, 'with_equals': ('name', 'value')})

    parser.add_option('--json-var', metavar='NAME=VALUE', help='Set an object value',
            action='callback', callback=append_context_maker, type='string',
            callback_kwargs={'fn': json_var, 'with_equals': ('name', 'json')})

    parser.add_option('--render', metavar='TEMPLATE OUTPATH', help='Render a template with current context (when unused, STDIN is rendered to STDOUT)',
            action='callback', callback=render_template, dest='rendered', default=False,
            type='string', nargs=2)

    parser.add_option('--add-tags', help='Make template tags and filters in the specified module available',
            action='callback', callback=lambda opt, s, val, p, **kwargs: add_to_builtins(val),
            type='string', metavar='path.to.module')

    opts, args = parser.parse_args()

    if args:
        parser.error('No positional arguments permitted')

    if not opts.rendered:
        render(sys.stdin, getattr(opts, 'context_makers', {}), sys.stdout)

