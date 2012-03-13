<table>
{% for row in data %}
{% with row|length as ncols %}
  {% if forloop.first %}
    <thead><tr>
    {% for cell in row %}
     <th>{{cell|escape}}</th>
    {% endfor %}
    </tr></thead>
    <tbody>
  {% else %}
    <tr>
    {% for cell in row %}
     <td>{{cell|escape}}</td>
    {% endfor %}
    </tr>
  {% endif %}
{% endwith %}
{% endfor %}
</tbody></table>
