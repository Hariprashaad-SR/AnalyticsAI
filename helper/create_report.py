import markdown
import asyncio
import pathlib
from playwright.async_api import async_playwright

async def md_to_pdf(summary_md):
    input_md = "sales_report.md"
    summary_md.replace('/saved_graphs', 'saved_graphs')

    with open(input_md, "w", encoding="utf-8") as f:
        f.write(summary_md)

    md_content = open("sales_report.md", encoding="utf-8").read()

    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"]
    )

    html_page = f"""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                    <title>Sales Report</title>
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

                    <style>
                        :root {{
                        --primary: #2563eb;
                        --primary-dark: #1d4ed8;
                        --gray-1: #f9fafb;
                        --gray-2: #f3f4f6;
                        --gray-3: #e5e7eb;
                        --gray-6: #4b5563;
                        --gray-8: #1f2937;
                        --text: #111827;
                        }}

                        * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        }}

                        img {{
                        max-width: 100%;
                        height: auto;           /* ← add this */
                        display: block;         /* ← helps centering & removes bottom gap */
                        margin: 1.5rem auto;    /* ← nice spacing + centered */
                    }}

                        body {{
                        font-family: 'Inter', system-ui, -apple-system, sans-serif;
                        background: var(--gray-1);
                        color: var(--text);
                        line-height: 1.6;
                        font-size: 15px;
                        }}

                        .container {{
                        max-width: 980px;
                        margin: 0 auto;
                        background: white;
                        padding: 5.5cm 2cm 4cm 2cm;
                        min-height: 100vh;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
                        }}

                        header {{
                        margin-bottom: 3.2rem;
                        padding-bottom: 2rem;
                        border-bottom: 3px solid var(--primary);
                        position: relative;
                        }}

                        header::after {{
                        content: "";
                        position: absolute;
                        bottom: -3px;
                        left: 0;
                        width: 140px;
                        height: 3px;
                        background: linear-gradient(to right, var(--primary), #60a5fa);
                        }}

                        h1 {{
                        font-size: 2.4rem;
                        font-weight: 700;
                        color: var(--gray-8);
                        margin-bottom: 0.6rem;
                        }}

                        .subtitle {{
                        color: var(--gray-6);
                        font-size: 1.1rem;
                        font-weight: 400;
                        }}

                        h2 {{
                        color: var(--gray-8);
                        font-size: 1.85rem;
                        font-weight: 600;
                        margin: 2.6rem 0 1.3rem;
                        border-left: 5px solid var(--primary);
                        padding-left: 1rem;
                        }}

                        h3 {{
                        color: #374151;
                        font-size: 1.42rem;
                        font-weight: 600;
                        margin: 2.2rem 0 1rem;
                        }}

                        p {{
                        margin-bottom: 1.3rem;
                        }}

                        table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 1.8rem 0;
                        font-size: 0.96rem;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                        border-radius: 8px;
                        overflow: hidden;
                        }}

                        th, td {{
                        padding: 14px 16px;
                        text-align: left;
                        border-bottom: 1px solid var(--gray-3);
                        }}

                        th {{
                        background: var(--primary);
                        color: white;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.4px;
                        font-size: 0.88rem;
                        }}

                        tr:nth-child(even) {{
                        background-color: var(--gray-1);
                        }}

                        tr:hover {{
                        background-color: #eff6ff;
                        transition: background-color 0.12s;
                        }}

                        .number {{
                        text-align: right;
                        font-variant-numeric: tabular-nums;
                        }}

                        blockquote {{
                        border-left: 4px solid #93c5fd;
                        padding-left: 1.4rem;
                        margin: 2rem 0;
                        color: #4b5563;
                        font-style: italic;
                        }}

                        code {{
                        font-family: 'Consolas', 'Monaco', monospace;
                        background: #f1f5f9;
                        padding: 0.25em 0.45em;
                        border-radius: 4px;
                        color: #d6336c;
                        }}

                        pre {{
                        background: #0f172a;
                        color: #e2e8f0;
                        padding: 1.4rem;
                        border-radius: 8px;
                        overflow-x: auto;
                        margin: 1.6rem 0;
                        font-size: 0.94rem;
                        }}

                        .toc {{
                        background: var(--gray-2);
                        padding: 1.6rem;
                        border-radius: 8px;
                        margin: 2rem 0 3.5rem;
                        }}

                        .toc h2 {{
                        margin-top: 0;
                        border-left: none;
                        padding-left: 0;
                        font-size: 1.3rem;
                        }}

                        hr {{
                        border: none;
                        border-top: 1px solid var(--gray-3);
                        margin: 3rem 0;
                        }}

                        footer {{
                        margin-top: 5rem;
                        padding-top: 2rem;
                        border-top: 1px solid var(--gray-3);
                        color: var(--gray-6);
                        text-align: center;
                        font-size: 0.9rem;
                        }}

                        @media print {{
                        .container {{
                            box-shadow: none;
                            padding: 1.2cm 1.8cm;
                            max-width: none;
                        }}
                        }}
                    </style>
                    </head>
                    <body>

                    <div class="container">

                    <header>
                        <h1>Sales Report</h1>
                        <div class="subtitle">Q4 2025 • January 2026</div>
                    </header>

                    {html_body}

                    <footer>
                        Confidential • Internal Use Only • © 2026 Your Company
                    </footer>

                    </div>

                    </body>
                    </html>
                    """

    html_file = pathlib.Path("report_modern.html")
    html_file.write_text(html_page, encoding="utf-8")
    print("Modern HTML report created → report_modern.html")
    return "report_modern.html"