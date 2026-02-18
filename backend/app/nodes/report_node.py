from app.core.model import get_llm
from app.core.prompts import REPORT_PLANNING_PROMPT, SQL_QUERY_PROMPT, SUMMARY_PROMPT, REPORT_PROMPT
from app.graphs.chart_graph import chart_report_graph
from app.graphs.sql_graph import sql_graph
from app.models.model import GlobalState
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
        
        state["plan"]["create_sql_query"] = llm.invoke(SQL_QUERY_PROMPT.format(question = question, schema = state['schema'], history = '')).content
        state["plan"]["verify_sql_query"] = "VERIFY THE QUERY"

        sql_state = sql_graph.invoke(state)
        query_result = sql_state.get("query_result")
        chart_url = None

        if step_type.startswith("chart"):
            state["plan"]["create_charts"] = question
            state["plan"]["execute_chart_code"] = "EXECUTE THE QUERY"
            chart_state = chart_report_graph.invoke({
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

    html_page = f"""
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Analysis Report</title>

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

        <style>
          :root {{
            --primary: #2563eb;
            --primary-light: #60a5fa;
            --bg-dark: #0f172a;
            --bg-darker: #0a0f1e;
            --surface: #1e293b;
            --surface-light: #334155;
            --border: #475569;
            --text: #e2e8f0;
            --text-dim: #94a3b8;
            --text-bright: #f1f5f9;
          }}

          * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }}

          body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: var(--bg-darker);
            color: var(--text);
            line-height: 1.6;
            font-size: 15px;
            padding: 0;
            margin: 0;
          }}

          .report-container {{
            max-width: 100%;
            margin: 0;
            background: var(--bg-dark);
            padding: 2rem;
          }}

          header {{
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 3px solid var(--primary);
            position: relative;
          }}

          header::after {{
            content: "";
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 120px;
            height: 3px;
            background: linear-gradient(to right, var(--primary), var(--primary-light));
          }}

          h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-bright);
            margin-bottom: 0.5rem;
          }}

          .subtitle {{
            color: var(--text-dim);
            font-size: 1rem;
          }}

          h2 {{
            color: var(--text-bright);
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem;
            border-left: 5px solid var(--primary);
            padding-left: 1rem;
          }}

          h3 {{
            color: var(--text);
            font-size: 1.2rem;
            font-weight: 600;
            margin: 1.8rem 0 1rem;
          }}

          h4, h5, h6 {{
            color: var(--text);
            font-weight: 600;
            margin: 1.5rem 0 0.8rem;
          }}

          p {{
            margin-bottom: 1rem;
            color: var(--text);
          }}

          ul, ol {{
            margin-left: 1.8rem;
            margin-bottom: 1rem;
            padding-left: 0.5rem;
          }}

          li {{
            margin-bottom: 0.4rem;
            color: var(--text);
          }}

          table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.92rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            border-radius: 8px;
            overflow: hidden;
            background: var(--surface);
          }}

          th {{
            padding: 12px 14px;
            background: var(--primary);
            color: white;
            text-transform: uppercase;
            font-size: 0.84rem;
            font-weight: 600;
            text-align: left;
          }}

          td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border);
            color: var(--text);
          }}

          tr:nth-child(even) {{
            background: rgba(51, 65, 85, 0.3);
          }}

          tr:hover {{
            background: rgba(51, 65, 85, 0.5);
          }}

          tbody tr:last-child td {{
            border-bottom: none;
          }}

          blockquote {{
            border-left: 4px solid var(--primary-light);
            padding-left: 1.2rem;
            margin: 1.5rem 0;
            font-style: italic;
            color: var(--text-dim);
          }}

          strong, b {{
            color: var(--text-bright);
            font-weight: 600;
          }}

          a {{
            color: var(--primary-light);
            text-decoration: underline;
            transition: color 0.2s;
          }}

          a:hover {{
            color: #93c5fd;
          }}

          code {{
            background: var(--surface);
            color: #fbbf24;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.88rem;
          }}

          pre {{
            background: var(--surface);
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1.2rem 0;
            border: 1px solid var(--border);
          }}

          pre code {{
            background: none;
            padding: 0;
            color: var(--text);
          }}

          hr {{
            border: none;
            border-top: 1px solid var(--border);
            margin: 2rem 0;
          }}

          img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5rem auto;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
          }}

          footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-dim);
          }}

          .toc {{
            background: var(--surface);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 2rem 0;
            border: 1px solid var(--border);
          }}

          .highlight {{
            background: rgba(37, 99, 235, 0.2);
            padding: 0.1rem 0.3rem;
            border-radius: 3px;
          }}

          .muted {{
            color: var(--text-dim);
          }}
        </style>
      </head>

      <body>
        <div class="report-container">
          <header>
            <h1>Analysis Report</h1>
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
    state['report'] = html_page

    print("Modern HTML report created → report_modern.html")

    return state
