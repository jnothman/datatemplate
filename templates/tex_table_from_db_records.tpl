{% comment %}
Constructs a TeX table where each cell is a record from a database relation.

Each table row and column specifies a WHERE clause, whose conjunction singles out a particular record.

Arguments:
* rows: a list of (label, where-clause) tuples
* cols: a list of (label, where-clause) tuples
* from: the table (or other relation) from which to retrieve the data
* field: an SQL expression referring to the value to extract
* corner: a label for the top-left corner cell
* where: a global WHERE condition
{% endcomment %}
\begin{tabular}{l|*{ {{cols|length}} }{l} }
\hline
{{corner|texescape}}{% for clabel, cwhere in cols %} & {{clabel|texescape}}{% endfor %} \\
\hline
\hline
{% for rlabel, rwhere in rows %}
{{rlabel|texescape}}{% for clabel, cwhere in cols %} & {% select {{field|default:"no_field_given"}} AS value FROM {{from|default:"data"}} WHERE ({{where|default:1}}) AND ({{rwhere}}) AND ({{cwhere}}) %}{{value|texescape}}{% endselect %}{% endfor %} \\
{% endfor %}
\hline
\end{tabular}
