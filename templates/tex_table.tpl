{% for row in data %}
{% with row|length as ncols %}
  {% if forloop.first %}
     \begin{tabular}{*{ {{ncols}} }{l}}\hline
  {% endif %}
  {% for cell in row %}
     {{cell|texescape}} 
     {% if forloop.last %}\\{% else %}&{% endif %}
  {% endfor %}
  {% if forloop.first %}
     \hline\hline
  {% endif %}
{% endwith %}
{% endfor %}
\hline
\end{tabular}
