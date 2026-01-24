from langgraph.graph import StateGraph, END
from nodes.report_node import report_planner, generate_summaries, md_to_pdfs, generate_report
from models.model import GlobalState


report_workflow = StateGraph(GlobalState)
report_workflow.add_node('report_planner', report_planner)
report_workflow.add_node('generate_summaries', generate_summaries)
report_workflow.add_node('generate_report', generate_report)
report_workflow.add_node('md_to_pdf', md_to_pdfs)

report_workflow.set_entry_point('report_planner')
report_workflow.add_edge('report_planner', 'generate_summaries')
report_workflow.add_edge('generate_summaries', 'generate_report')
report_workflow.add_edge('generate_report', 'md_to_pdf')
report_workflow.add_edge('md_to_pdf', END)

report_graph = report_workflow.compile()
