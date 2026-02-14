from langgraph.graph import StateGraph, END
from app.nodes.sql_node import create_sql_query, verify_sql_query, execute_sql_query, end_node
from app.models.model import GlobalState

def check_sql(state):
    if state['verified_sql']:
            return "execute_sql_query"
    else:
        if state['check_count'] <= 2:
            return "create_sql_query"
        else:
            return "end_node"
    

sql_workflow = StateGraph(GlobalState)
sql_workflow.add_node('create_sql_query', create_sql_query)
sql_workflow.add_node('verify_sql_query', verify_sql_query)
sql_workflow.add_node('execute_sql_query', execute_sql_query)
sql_workflow.add_node('end_node', end_node)

sql_workflow.set_entry_point('create_sql_query')
sql_workflow.add_edge('create_sql_query', 'verify_sql_query')
sql_workflow.add_conditional_edges(
    'verify_sql_query',
    check_sql,
    {
        'execute_sql_query' : 'execute_sql_query',
        'create_sql_query' : 'create_sql_query',
        'end_node' : 'end_node'
    }
)
sql_workflow.add_edge('end_node', END)
sql_workflow.add_edge('execute_sql_query', END)

sql_graph = sql_workflow.compile()