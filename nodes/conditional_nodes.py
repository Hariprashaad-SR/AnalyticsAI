from core.model import get_llm
from core.prompts import CLASSIFY_PROMPT
from graphs.chart_graph import chart_graph
from graphs.report_graph import report_graph
from graphs.sql_graph import sql_graph

def router(state):
    if 'report' in state['query'].lower() or 'detailed' in state['query'].lower():
        return "generate_report"
    else:
        return "sql_node"
    
def router2(state):
    if 'chart' in state['query'].lower() or 'graph' in state['query'].lower():
        return "create_charts"
    else:
        return "summarize_with_llm"
    
def sql_node(state):
    return sql_graph.invoke(state)

def chart_node(state):
    return chart_graph.invoke(state)

def report_node(state):
    return report_graph.invoke(state)

def is_sql(state):
    if state['file_type'] in ['csv', 'excel']:
        return "insert_node"
    else:
        return "get_schema"  
    
def is_chart(state):
    if state['plan'].get('execute_chart_code', '') != '':
        return 'chart_node'
    else:
        return 'summarize'

def is_valid(state):
    if state['sql_query'] == 'This action cannot be done':
        return 'end'
    else:
        return 'decision'
    
def check_intent(state):
    return get_llm().invoke(CLASSIFY_PROMPT + f"query = {state['query']}").content