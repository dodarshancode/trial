import csv
import argparse
from pathlib import Path

def load_templates(template_path):
    """
    Load the template file and split into query_template and code_template.
    The file must have two parts separated by a line with exactly '---'.
    """
    text = template_path.read_text(encoding='utf-8')
    parts = text.splitlines()
    try:
        sep_idx = parts.index('---')
    except ValueError:
        raise ValueError("Template file must contain a line with exactly '---' separating the two sections.")
    query_template = "\n".join(parts[:sep_idx]).strip()
    code_template  = "\n".join(parts[sep_idx+1:]).strip()
    return query_template, code_template

def render_pairs(query_tmpl, code_tmpl, inputs):
    """
    For each dict in inputs, render the query and code templates.
    Returns a list of (query, code) tuples.
    """
    pairs = []
    for params in inputs:
        try:
            q = query_tmpl.format(**params)
            c = code_tmpl.format( **params)
        except KeyError as e:
            raise KeyError(f"Missing placeholder in params: {e}")
        pairs.append((q, c))
    return pairs

def write_csv(pairs, output_path):
    """
    Write the list of (query, code) pairs into a CSV.
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_query', 'code'])
        for q, c in pairs:
            writer.writerow([q, c])

def main():
    parser = argparse.ArgumentParser(
        description="Render a query+code template with multiple input combinations into a CSV."
    )
    parser.add_argument('template', type=Path, help="Path to .txt template file, split by a line '---'")
    parser.add_argument('output',   type=Path, help="Path to output .csv")
    args = parser.parse_args()

    # 1) Load templates
    query_tmpl, code_tmpl = load_templates(args.template)

    # 2) Define your list of input combinations here.
    #    Each dict key must match the placeholders in your templates.
    inputs = [
        {'model': 'gpt-3.5', 'temperature': 0.7},
        {'model': 'gpt-4',   'temperature': 0.1},
        {'model': 'gpt-4-turbo', 'temperature': 0.5},
        # … add as many as you like …
    ]

    # 3) Render
    pairs = render_pairs(query_tmpl, code_tmpl, inputs)

    # 4) Write CSV
    write_csv(pairs, args.output)
    print(f"Wrote {len(pairs)} rows to {args.output}")

if __name__ == '__main__':
    main()


######
'''
# User query:
"Generate a {model} completion with temperature {temperature}"

---
# Code to run:
import openai
openai.api_key = "YOUR_KEY"
openai.ChatCompletion.create(
    model="{model}",
    messages=[{"role":"user","content":"Hello!"}],
    temperature={temperature}
)
'''

python render_templates.py template.txt output.csv
