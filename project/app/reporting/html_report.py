from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import List, Dict, Any

def generate_html_report(candidates: List[Dict[str, Any]], output_path: str):
    """Generates an HTML report from a list of candidate results."""
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report.html")
    
    html_content = template.render(candidates=candidates)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path
