#!/usr/bin/env python
import os.path
import datatemplate

EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(os.path.dirname(EXAMPLE_DIR), 'templates')

contexts = [
    datatemplate.csvsql(os.path.join(EXAMPLE_DIR, 'large_table.tsv'), dialect='tab'),
    {
        'field': '`Metric 1 F`',
        'where': 'Test="test1"',
        'corner': 'Model',
        'rows': [
            ('1', 'Model="model1"'),
            ('2', 'Model="model2"'),
            ('3', 'Model="model3"'),
        ],
        'cols': [
            ('English', 'Lang="en"'),
            ('Spanish', 'Lang="es"'),
            ('Dutch', 'Lang="nl"'),
            ('German', 'Lang="de"')
        ],
    },
]
template_path = os.path.join(TEMPLATE_DIR, 'tex_table_from_db_records.tpl')
print datatemplate.render(open(template_path), contexts)
