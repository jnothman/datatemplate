#!/usr/bin/env python
# A simple Python script to convert csv files to sqlite (with type guessing)
#
# @author: Rufus Pollock
# Placed in the Public Domain
import csv
import sqlite3

def convert(filepath_or_fileobj, conn, table='data', temporary=False, **csv_kwargs):
    if isinstance(filepath_or_fileobj, basestring):
        fo = open(filepath_or_fileobj)
    else:
        fo = filepath_or_fileobj
    reader = csv.reader(fo, **csv_kwargs)

    types = _guess_types(fo, csv_kwargs=csv_kwargs)
    fo.seek(0)
    headers = reader.next()

    _columns = ','.join(
        '`%s` %s' % (header, _type) for (header,_type) in zip(headers, types)
        )

    if not hasattr(conn, 'cursor'):
        conn = sqlite3.connect(conn)
    c = conn.cursor()
    c.execute('CREATE %s table %s (%s)' % ('temporary' if temporary else '', table, _columns))

    _insert_tmpl = 'insert into %s values (%s)' % (table,
        ','.join(['?']*len(headers)))
    for row in reader:
        c.execute(_insert_tmpl, [v or None for v in row])

    conn.commit()
    c.close()
    return conn

def _guess_types(fileobj, max_sample_size=100, csv_kwargs={}):
    '''Guess column types (as for SQLite) of CSV.

    :param fileobj: read-only file object for a CSV file.
    '''
    reader = csv.reader(fileobj, **csv_kwargs)
    # skip header
    _headers = reader.next()
    # order matters
    # (order in form of type you want used in case of tie to be last)
    options = [
        ('integer', int),
        ('real', float),
        ('text', unicode),
        # 'date',
    ]
    casts = dict(options)
    opt_list = [type_ for type_, cast in options]

    # the remaining types compatible with each column
    compatible = [opt_list[:] for x in range(len(_headers))]

    for count, row in enumerate(reader):
        for cell, col_compat in zip(row, compatible):
            cell = cell.strip()
            if not cell:
                continue

            failed = []
            for opt in col_compat:
                try:
                    casts[opt](cell)
                except ValueError:
                    failed.append(opt)
            for failure in failed:
                col_compat.remove(failure)

        if count == max_sample_size:
            break
    return [col_compat[0] for col_compat in compatible]


def test():
    '''Simple test case'''
    import StringIO
    import os
    fileobj = StringIO.StringIO(
'''heading_1,heading_2,heading_3
abc,1,1.0
xyz,2,2.0
efg,3,3.0'''
    )
    dbpath = '/tmp/csv2sqlite-test-data.db'
    if os.path.exists(dbpath):
        os.remove(dbpath)
    table = 'data'
    convert(fileobj, dbpath, table)
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('select count(*) from %s' % table);
    row = c.next()
    assert row[0] == 3, row

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('''csv2sqlite.py {csv-file-path} {sqlite-db-path} [{table-name}]

Convert a csv file to a table in an sqlite database (which need not yet exist).

* table-name is optional and defaults to 'data'
''')
        sys.exit(1)
    convert(*sys.argv[1:])
