{% comment %}
Constructs a HTML table where each cell is a record from a database relation.

Each table row and column specifies a WHERE clause, whose conjunction singles out a particular record.

Arguments:
* rows: a list of (label, where-clause) tuples
* cols: a list of (label, where-clause) tuples
* from: the table (or other relation) from which to retrieve the data
* field: an SQL expression referring to the value to extract
* corner: a label for the top-left corner cell
* where: a global WHERE condition
{% endcomment %}
<table>
<thead>
<tr><th>{{corner|escape}}</th>{% for clabel, cwhere in cols %}<td>{{clabel|escape}}</td>{% endfor %}</tr>
</thead>
<tbody>
{% for rlabel, rwhere in rows %}
<tr><td>{{rlabel|escape}}</td>{% for clabel, cwhere in cols %}<td>{% select {{field|default:"no_field_given"}} AS value FROM {{from|default:"data"}} WHERE ({{where|default:1}}) AND ({{rwhere}}) AND ({{cwhere}}) %}{{value|escape}}{% endselect %}</td>{% endfor %}</tr>
{% endfor %}
</tbody>
</table>
