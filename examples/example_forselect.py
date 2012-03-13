#!/usr/bin/env python

import datatemplate

LANG_NAMES = dict(
        en='English',
        es='Spanish',
        ru='Russian',
        nl='Dutch',
        de='German',
)

TEMPLATE = '''
Results greater than {{threshold}}%:
{% forselect *, `Metric 1 F` AS result FROM data WHERE Test = "test1" AND result > {{threshold}} %}
* {{Model}} in {{lang_names|item:Lang}}: {{result}}
{% empty %}
No results
{% endforselect %}
'''

context = datatemplate.build_context([datatemplate.csvsql('large_table.tsv', table='data', dialect='tab')])
for threshold in [90, 80, 70, 60]:
    print datatemplate.render(TEMPLATE, [context, {'threshold': threshold, 'lang_names': LANG_NAMES}])
