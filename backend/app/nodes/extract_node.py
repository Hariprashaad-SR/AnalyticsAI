from typing import Dict, Any
from langchain_core.messages import HumanMessage
from app.core.model import get_vision_llm
from app.core.prompts import TABLE_EXTRACTION_PROMPT
from app.helper.extraction_helper import _build_image_payload, _parse_llm_response

def extract_table(image_input: str) -> Dict[str, Any]:
    """
    Extract tabular data from an image (URL or local file) using a vision LLM.
    """

    image_payload = _build_image_payload(image_input)
    if image_payload is None:
        return {
        "structured": {"columns": [], "rows": []},
        "unstructured": f"Image file not found: {image_input}",
    }

    message = HumanMessage(
        content=[
            {"type": "text", "text": TABLE_EXTRACTION_PROMPT},
            image_payload,
        ]
    )

    llm = get_vision_llm()
    response = llm.invoke([message])

    return _parse_llm_response(response.content)
