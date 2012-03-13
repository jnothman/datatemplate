#!/usr/bin/env bash

if [ '!' -e "large_table.tsv" ]
then
    echo 'Error: Must be executed from examples directory' >&2
    exit 1
fi

datatemplate --tsvsql data=large_table.tsv --var field='`Metric 1 F`' --var where='Test="test1"' \
    --json-var rows='[["1", "Model=\"model1\""], ["2", "Model=\"model2\""]]' --var corner='Model' \
    --json-var cols='[["English", "Lang=\"en\""], ["Spanish", "Lang=\"es\""], ["Dutch", "Lang=\"nl\""], ["German", "Lang=\"de\""]]' \
    < ../templates/tex_table_from_db_records.tpl
