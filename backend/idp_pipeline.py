"""Document ingestion, extraction and integration adapters for the IDP API.

The OCR/VLM providers are deliberately swappable.  Local OCR is used when it is
installed; an HTTP vision service can be configured with VLM_ENDPOINT for more
complex vendor layouts.
"""
from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import requests


DATE_VALUE = r"(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
PO_PATTERN = r"\b(?:PO|PURCHASE\s+ORDER)\s*(?:NO\.?|NUMBER|#|:)?\s*([A-Z0-9][A-Z0-9-]{3,})\b"


@dataclass
class ExtractedDocument:
    filename: str
    text: str
    document_type: str
    confidence: float
    fields: dict[str, str] = field(default_factory=dict)
    needs_review: bool = False


def _normalise_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def classify_document(text: str, filename: str) -> str:
    haystack = f"{filename} {text}".upper()
    if "GOODS RECEIPT" in haystack or "GRN" in haystack:
        return "Goods_Receipt_Note"
    if "LETTER OF CREDIT" in haystack or "IRREVOCABLE LC" in haystack:
        return "Bank_LC"
    if "BILL OF LADING" in haystack or "SHIPMENT" in haystack:
        return "Shipment_Document"
    return "Purchase_Order"


def extract_fields(text: str) -> tuple[dict[str, str], float]:
    fields: dict[str, str] = {}
    po = re.search(PO_PATTERN, text, flags=re.IGNORECASE)
    if po:
        fields["purchase_order_number"] = po.group(1).upper()
    # Examine each labelled line independently.  This prevents "Agreed
    # Delivery Date" from also matching the generic word "delivery".
    for line in text.splitlines():
        match = re.search(DATE_VALUE, line)
        if not match:
            continue
        normalised = _normalise_date(match.group(1))
        if not normalised:
            continue
        label = line[:match.start()].lower()
        if any(word in label for word in ("obiz", "agreed", "scheduled", "target")):
            fields["obiz_delivery_date"] = normalised
        elif any(word in label for word in ("actual", "received", "receipt", "grn")):
            fields["actual_delivery_date"] = normalised
    confidence = min(0.98, 0.45 + (0.18 * len(fields)))
    return fields, confidence


def local_ocr(content: bytes, filename: str, content_type: str | None) -> str:
    """Extract text from TXT/PDF/images, degrading safely if OCR is unavailable."""
    if (content_type or "").startswith("text/") or filename.lower().endswith(".txt"):
        return content.decode("utf-8", errors="replace")
    if filename.lower().endswith(".pdf"):
        try:
            import fitz  # PyMuPDF
            document = fitz.open(stream=content, filetype="pdf")
            text = "\n".join(page.get_text() for page in document)
            if text.strip():
                return text
        except ImportError:
            pass
    try:
        from PIL import Image
        import pytesseract
        return pytesseract.image_to_string(Image.open(io.BytesIO(content)))
    except (ImportError, OSError, ValueError):
        return ""


def vision_retry(content: bytes, filename: str, content_type: str | None) -> str:
    """Ask a configured VLM to re-read low-confidence pages/regions.

    The endpoint contract is intentionally simple: multipart file in, JSON
    containing a `text` property out.  This works with an internal Llama
    vision gateway without coupling credentials to the dashboard.
    """
    endpoint = os.getenv("VLM_ENDPOINT")
    if not endpoint:
        return ""
    try:
        response = requests.post(endpoint, files={"file": (filename, content, content_type)}, timeout=25)
        response.raise_for_status()
        return response.json().get("text", "")
    except (requests.RequestException, ValueError):
        return ""


def fetch_erp_delivery_date(po_number: str | None) -> str | None:
    endpoint = os.getenv("ERP_DELIVERY_LOOKUP_URL")
    if not endpoint or not po_number:
        return None
    try:
        response = requests.get(endpoint, params={"po_number": po_number}, timeout=10)
        response.raise_for_status()
        return _normalise_date(response.json().get("actual_delivery_date"))
    except (requests.RequestException, ValueError):
        return None


def publish_assessment(result: dict[str, Any]) -> bool:
    endpoint = os.getenv("COMPLIANCE_WEBHOOK_URL")
    if not endpoint:
        return False
    try:
        response = requests.post(endpoint, json=result, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False
