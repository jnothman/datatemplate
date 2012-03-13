#!/usr/bin/env python
import os.path
import datatemplate

EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(os.path.dirname(EXAMPLE_DIR), 'templates')

contexts = [
    datatemplate.csv('data', os.path.join(EXAMPLE_DIR, 'large_table.tsv'), dialect='tab'),
]
template_path = os.path.join(TEMPLATE_DIR, 'tex_table.tpl')
print datatemplate.render(open(template_path), contexts)
