from pathlib import Path
from typing import Dict, Any
from jinja2 import Template

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }}</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3 { color: #222; }
        h1 { border-bottom: 3px solid #0066cc; padding-bottom: 10px; }
        h2 { border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 30px; }
        h3 { margin-top: 20px; }
        .metadata {
            background: #f5f5f5;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .metadata p { margin: 8px 0; }
        ul { list-style: none; padding-left: 0; }
        li { margin: 8px 0; }
        .indent { padding-left: 30px; margin-top: 15px; }
        code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .collection-desc { color: #666; margin: 5px 0 10px 0; }
    </style>
</head>
<body>
    <h1>{{ name }}</h1>

    <div class="metadata">
        <p><strong>Description:</strong> {{ description }}</p>
        <p><strong>Published:</strong> {{ date_published }}</p>
        <p><strong>License:</strong> {{ license }}</p>
    </div>

    <h2>Datasets</h2>

    {% for dataset in datasets %}
    <h3>{{ dataset.name }}</h3>
    {% if dataset.description %}<p>{{ dataset.description }}</p>{% endif %}

    {% for collection in dataset.collections %}
    <div class="indent">
        <strong>{{ collection.name }}</strong>
        {% if collection.description %}
        <p class="collection-desc">{{ collection.description }}</p>
        {% endif %}
        <ul>
        {% for file in collection.files %}
            <li>{{ file.name }} <code>{{ file.path }}</code>
            {% if file.description %}<br><small style="color: #666;">{{ file.description }}</small>{% endif %}
            </li>
        {% endfor %}
        </ul>
    </div>
    {% endfor %}
    {% endfor %}

    <script type="application/ld+json">
{{ json_ld }}
    </script>
</body>
</html>
"""


def convert_jsoncrate_to_html(crate: Dict[str, Any], dir_path:str) -> None:
    """Convert RO-Crate JSON to simple HTML preview.

    Args:
        crate: List of RO-Crate graph items
        dir_path: Directory path where HTML will be saved

    Returns:
        Path to generated HTML file
    """
    # Render template
    template = Template(HTML_TEMPLATE)
    html = template.render(**crate)

    # Write output
    html_path = Path(dir_path) / "ro-crate-preview.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding='utf-8')

    print(f"✓ Generated {html_path}")
