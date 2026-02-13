from app.models.model import GlobalState
from langgraph.graph import StateGraph, END
from app.nodes.chat_node import chat
from app.nodes.file2sqlite_node import file_to_sqlite
from app.nodes.classify_file import classify_file
from app.nodes.get_schema_node import get_dbschema
from app.nodes.summarise_node import *
from app.nodes.planner_node import *
from app.nodes.conditional_nodes import *
from app.nodes.sql_node import end_node
from app.utils.local_db import *


def add_values(state):
    new_state = load_session_file_state(state['session_id'])
    state['uploaded_file'] = new_state['uploaded_file']
    state['file_type'] = new_state['file_type']
    state['schema'] = new_state['schema']
    return state

def condition(state):
    if state['query'] == None:
        return 'classify_file'
    return 'add_values'

workflow = StateGraph(GlobalState)
workflow.add_node('classify_file', classify_file)
workflow.add_node('insert_node', file_to_sqlite)
workflow.add_node('get_schema', get_dbschema)
workflow.add_node('sql_node', sql_node)
workflow.add_node('chart_node', chart_node)
workflow.add_node('summarize_with_llm', summarize_with_llm)
workflow.add_node('planner', planning_agent)
workflow.add_node("generate_report", report_node)
workflow.add_node('decision', lambda x: x)
workflow.add_node('end_node', end_node)
workflow.add_node('chat', chat)
workflow.add_node('entry_node', lambda x : x)
workflow.add_node('add_values', add_values)
workflow.add_node('intent_check', lambda x : x)



workflow.set_entry_point('entry_node')
workflow.add_conditional_edges(
    'entry_node',
    condition, 
    {
        'classify_file' : 'classify_file',
        'add_values' : 'add_values'
    }
)
workflow.add_edge('add_values', 'intent_check')
workflow.add_conditional_edges(
    'classify_file',
    is_sql,
    {
        'get_schema' : 'get_schema',
        'insert_node': 'insert_node'
    }
)
workflow.add_edge('insert_node', 'get_schema')
workflow.add_edge('get_schema', END)
workflow.add_conditional_edges(
    'intent_check',
    check_intent,
    {
        'sql_node' :'planner',
        'chat' : 'chat'
    }
)
workflow.add_edge('chat', END)
workflow.add_conditional_edges(
    'planner',
    router,
    {
        'sql_node': 'sql_node',
        'generate_report' : 'generate_report'
    }
)
workflow.add_conditional_edges(
    'sql_node', 
    is_valid,
    {
        'decision' : 'decision',
        'end' : 'end_node'
    }
)
workflow.add_edge('end_node', END)
workflow.add_conditional_edges(
    'decision', 
    is_chart,
    {
        'chart_node' : 'chart_node',
        'summarize' : 'summarize_with_llm'
    }
)
workflow.add_edge('chart_node', 'summarize_with_llm')
workflow.add_edge('summarize_with_llm', END)
workflow.add_edge('generate_report', END)

graph = workflow.compile()