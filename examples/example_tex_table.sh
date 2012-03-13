#!/usr/bin/env bash

if [ '!' -e "large_table.tsv" ]
then
    echo 'Error: Must be executed from examples directory' >&2
    exit 1
fi

datatemplate --tsv data=large_table.tsv < ../templates/tex_table.tpl
