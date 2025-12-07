# SAST Vulnerability Scan Results

{% for vuln in report.vulnerabilities|sort(attribute='severity') -%}
## {{vuln.severity}}: {{vuln.name}}
- {{vuln.location.file}}{% if vuln.location.start_line %}:{{vuln.location.start_line}}{% if vuln.location.end_line and vuln.location.start_line < vuln.location.end_line %} - {{vuln.location.end_line}}{% endif %}{% endif %}

{{vuln.description}}
{% endfor -%}