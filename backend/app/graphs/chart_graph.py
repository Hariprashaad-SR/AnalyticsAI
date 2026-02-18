from langgraph.graph import StateGraph, END
from app.models.model import GlobalState
from app.nodes.chart_node import create_charts, execute_chart_code, create_charts_report, execute_chart_code_report
        
chart_workflow = StateGraph(GlobalState)
chart_workflow.add_node('create_charts', create_charts)
chart_workflow.add_node('execute_chart_code', execute_chart_code)

chart_workflow.set_entry_point('create_charts')
chart_workflow.add_edge('create_charts', 'execute_chart_code')
chart_workflow.add_edge('execute_chart_code', END)

chart_graph = chart_workflow.compile()

chart_report_workflow = StateGraph(GlobalState)
chart_report_workflow.add_node('create_charts', create_charts_report)
chart_report_workflow.add_node('execute_chart_code', execute_chart_code_report)

chart_report_workflow.set_entry_point('create_charts')
chart_report_workflow.add_edge('create_charts', 'execute_chart_code')
chart_report_workflow.add_edge('execute_chart_code', END)

chart_report_graph = chart_report_workflow.compile()