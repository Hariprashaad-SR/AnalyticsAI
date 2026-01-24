from langgraph.graph import StateGraph, END
from models.model import GlobalState
from nodes.chart_node import create_charts, execute_chart_code
        
chart_workflow = StateGraph(GlobalState)
chart_workflow.add_node('create_charts', create_charts)
chart_workflow.add_node('execute_chart_code', execute_chart_code)

chart_workflow.set_entry_point('create_charts')
chart_workflow.add_edge('create_charts', 'execute_chart_code')
chart_workflow.add_edge('execute_chart_code', END)

chart_graph = chart_workflow.compile()