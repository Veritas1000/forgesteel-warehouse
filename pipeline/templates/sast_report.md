{%- if report.vulnerabilities|length > 0 -%}
# ⚠️ SAST Vulnerability Scan Results
    {% set severities = report.vulnerabilities|groupby('severity') %}
    {%- for severity, items in severities %}
## {{severity}}: {{items|length}} found
        {% for vuln_name, individuals in items|groupby('name') %}
### Vulnerability: {{vuln_name}}
            {% for vuln in individuals %}
- {{vuln.location.file}}{% if vuln.location.start_line %}:{{vuln.location.start_line}}{% if vuln.location.end_line and vuln.location.start_line < vuln.location.end_line %}-{{vuln.location.end_line}}{% endif %}{% endif %}
            {%- endfor %}

#### About this vulnerability

{{ (individuals|first).description}}

        {%- endfor -%}
    {%- endfor -%}
{%- else -%}
✅ No vulnerabilities found in SAST scan
{%- endif -%}