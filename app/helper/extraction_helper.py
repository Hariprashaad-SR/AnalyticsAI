from typing import Dict, Any
import base64
import json
import re
from pathlib import Path


def _build_image_payload(image_input: str) -> Dict[str, Any] | None:
    """
    Create an image payload compatible with vision LLMs.
    Supports URLs and local image files.
    """
    if image_input.startswith(("http://", "https://")):
        return {
            "type": "image_url",
            "image_url": {"url": image_input},
        }

    image_path = Path(image_input)
    if not image_path.exists():
        return None

    mime_type = _detect_mime_type(image_path.suffix.lower())

    with image_path.open("rb") as file:
        image_b64 = base64.b64encode(file.read()).decode("utf-8")

    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:{mime_type};base64,{image_b64}"
        },
    }


def _detect_mime_type(suffix: str) -> str:
    """
    Detect MIME type from file extension.
    """
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"


def _parse_llm_response(raw_content: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from LLM output.
    """
    raw = raw_content.strip()

    if raw.startswith("```"):
        raw = re.sub(
            r"^```json|^```|```$",
            "",
            raw,
            flags=re.MULTILINE,
        ).strip()

    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found")

        data = json.loads(json_match.group())

    except Exception:
        return {
        "structured": {"columns": [], "rows": []},
        "unstructured": raw,
    }

    return {
        "structured": data.get("structured", {"columns": [], "rows": []}),
        "unstructured": data.get("unstructured", ""),
    }
