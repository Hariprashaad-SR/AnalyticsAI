from helper.get_schema import get_schema
from langsmith import traceable

from models.model import GlobalState

@traceable(name='get_dbschema')
def get_dbschema(state : GlobalState) -> GlobalState:
    state['schema'] = get_schema(state['uploaded_file'])
    return state