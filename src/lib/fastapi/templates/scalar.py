"""Scalar documentation template."""

DOCS_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>{{title}}</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body>
    <script
      id="api-reference"
      data-url="/openapi.json"
      data-configuration='{
        "theme": "purple",
        "layout": "modern",
        "showSidebar": true
      }'></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>
"""
