from models.model import GlobalState
from langgraph.graph import StateGraph, END
from nodes.chat_node import chat
from nodes.insert_node import file_to_sqlite
from nodes.classify_file import classify_file
from nodes.get_schema_node import get_dbschema
from nodes.csv_node import *
from nodes.summarise_node import *
from nodes.planner_node import *
from nodes.conditional_nodes import *
from nodes.sql_node import end_node
from langgraph.checkpoint.memory import InMemorySaver


# memory = InMemorySaver()

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


workflow.set_entry_point('classify_file')
workflow.add_conditional_edges(
    'classify_file',
    is_sql,
    {
        'get_schema' : 'get_schema',
        'insert_node': 'insert_node'
    }
)
workflow.add_edge('insert_node', 'get_schema')
# workflow.add_edge('get_schema', 'planner')
workflow.add_conditional_edges(
    'get_schema',
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