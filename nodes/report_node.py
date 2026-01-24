from core.model import get_llm
from core.prompts import REPORT_PLANNING_PROMPT, SQL_QUERY_PROMPT, SUMMARY_PROMPT, REPORT_PROMPT
from graphs.chart_graph import chart_graph
from graphs.sql_graph import sql_graph
from models.model import GlobalState
from typing import List, Dict, Any
from datetime import datetime
import pathlib
import markdown
from langsmith import traceable



@traceable(name='report_planner')
def report_planner(state : GlobalState) -> GlobalState:
    llm = get_llm()

    planning_response = llm.invoke(
        REPORT_PLANNING_PROMPT.format(
            query=state["query"],
            schema=state["schema"]
        )
    )

    report_plan = eval(planning_response.content)
    state['report_plan'] = report_plan
    return state

@traceable(name='generate_summaries')
def generate_summaries(state: GlobalState) -> GlobalState:
    llm = get_llm()
    report_plan = state['report_plan']

    if not report_plan or not isinstance(report_plan, list):
        return [{"error": "Invalid or empty report plan"}]

    state["plan"] = state.get("plan", {})
    summaries = []
    steps = 1
    for step in report_plan:
        step_type = step.get("type")
        question = step.get("question")
        state["current_step"] = steps


        if not question or not step_type:
            continue
        
        state["plan"]["create_sql_query"] = llm.invoke(SQL_QUERY_PROMPT.format(question = question, schema = state['schema'])).content
        state["plan"]["verify_sql_query"] = "VERIFY THE QUERY"

        sql_state = sql_graph.invoke(state)
        query_result = sql_state.get("query_result")
        chart_url = None

        if step_type.startswith("chart"):
            state["plan"]["create_charts"] = question
            state["plan"]["execute_chart_code"] = "EXECUTE THE QUERY"
            chart_state = chart_graph.invoke({
                **sql_state,
                "chart_type": step_type
            })
            chart_url = chart_state.get("chart_url")
            

        summary_prompt = SUMMARY_PROMPT.format(question = question, query_result = query_result)
        summary_response = llm.invoke(summary_prompt)

        summaries.append({
            "type": step_type,
            "question": question,
            "summary": summary_response.content.strip(),
            "chart_url": chart_url
        })
    steps += 1
     
    state['summaries'] = summaries
    return state


@traceable(name='generate_report')
def generate_report(state : GlobalState) -> GlobalState:
    summaries_list = state['summaries']
    if not isinstance(summaries_list, list) or not summaries_list:
        return "# Error\nNo valid summaries provided for report generation."

    current_date = datetime.now().strftime("%B %d, %Y")  

    summaries_text = ""
    for item in summaries_list:
        summaries_text += f"**Question:** {item['question']}\n"
        summaries_text += f"**Type:** {item['type']}\n"
        summaries_text += f"**Summary:** {item.get('summary', 'No summary available')}\n"
        
        if item.get('chart_url'):
            summaries_text += f"**Chart URL:** {item['chart_url']}\n"
            summaries_text += f"**Chart Description (for reference):** Relevant chart visualizing the answer to the question above.\n"
        
        summaries_text += "-" * 80 + "\n\n"

    try:
        llm = get_llm()  
        response = llm.invoke(REPORT_PROMPT.format(current_date = current_date, summaries_text = summaries_text))
        state['report'] = response.content.strip()
        return state
    except Exception as e:
        return f"# Report Generation Error\n\nAn error occurred while generating the report:\n\n{str(e)}\n"


@traceable(name='md_to_pdfs')
def md_to_pdfs(state : GlobalState) -> GlobalState:
    input_md = "sales_report.md"
    summary_md = state['report']

    summary_md = summary_md.replace('/saved_graphs', 'saved_graphs')

    with open(input_md, "w", encoding="utf-8") as f:
        f.write(summary_md)

    md_content = open(input_md, encoding="utf-8").read()

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
      height: auto;
      display: block;
      margin: 1.5rem auto;
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
      border-bottom: 1px solid var(--gray-3);
    }}

    th {{
      background: var(--primary);
      color: white;
      text-transform: uppercase;
      font-size: 0.88rem;
    }}

    tr:nth-child(even) {{
      background-color: var(--gray-1);
    }}

    blockquote {{
      border-left: 4px solid #93c5fd;
      padding-left: 1.4rem;
      margin: 2rem 0;
      font-style: italic;
    }}

    .toc {{
      background: var(--gray-2);
      padding: 1.6rem;
      border-radius: 8px;
      margin: 2rem 0 3.5rem;
    }}

    footer {{
      margin-top: 5rem;
      padding-top: 2rem;
      border-top: 1px solid var(--gray-3);
      text-align: center;
      font-size: 0.9rem;
      color: var(--gray-6);
    }}

    @media print {{
      .container {{
        box-shadow: none;
        padding: 1.2cm 1.8cm;
      }}
    }}
  </style>
</head>

<body>
  <div class="container">
    <header>
      <h1>Report</h1>
      <div class="subtitle">Generated by AnalyticsAI</div>
    </header>

    {html_body}

    <footer>
      Confidential • Internal Use Only • © 2026 AnalyticsAI
    </footer>
  </div>
</body>
</html>
"""

    html_file = pathlib.Path("report_modern.html")
    html_file.write_text(html_page, encoding="utf-8")

    print("Modern HTML report created → report_modern.html")

    return state
