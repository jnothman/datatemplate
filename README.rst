datatemplate
============

is a tool to render Django templates using a context (i.e. variables loaded from files):

* arbitrary JSON data
* comma or tab-delimited data as a sequence of tuples
* sqlite databases
* comma or tab-delimited data as in-memory sqlite tables

Other variables may be set on the command-line using ``--var`` and ``--json-var``.

For example, ``templates/html_table.tpl`` and ``templates/tex_table.tpl`` can be used to render sequences of tuples (where the first is a header) loaded from CSV, TSV (tab-delimited) or JSON, as tables in HTML and TeX respectively.

``datatemplate`` also introduces some template tags to perform SQL SELECT queries over sqlite databases (or CSVs read into sqlite in-memory tables):

* ``{% select field1, field2 from blah %}`` performs a query with exactly one row in its result, allowing ``{{field1}}`` and ``{{field2}}`` to be used until ``{% endselect %}``
* ``{% forselect field1, field2 from blah %}`` iterates through rows of the query, providing the forloop variable for additional control.
* Context variables in queries are resolved: ``{% select field1, field2 from {{table_var}} %}``

As such, ``datatemplate`` allows the generic formatting of SQL results over CSV data!

Installation
------------

Simply execute:

::

    python setup.py install

to provide command-line:

::

    datatemplate --help
    datatemplate --csv data=/path/to/data.csv < templates/html_table.tpl > out.html

and Python interfaces:

::

    import datatemplate
    template = open('templates/html_table.tpl')
    context_makers = [datatemplate.csv('data', '/path/to/data.csv')]
    print datatemplate.render(template, context_makers)
