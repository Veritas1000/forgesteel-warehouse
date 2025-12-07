import jinja2
import json

## Assumes run from top level

## Load JSON data
with open('gl-sast-report.json') as json_file:
    sast_json = json.load(json_file)

## Set up Jinja environment
env = jinja2.Environment(autoescape=jinja2.select_autoescape(['html', 'htm', 'xml']), loader=jinja2.FileSystemLoader('.'))
template = env.get_template('pipeline/templates/sast_report.md')

# Render the template with sast report json data
output = template.render(report=sast_json)

comment_obj = { "body": output }

print(json.dumps(comment_obj))
