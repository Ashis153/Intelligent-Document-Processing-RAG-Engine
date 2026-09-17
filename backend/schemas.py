from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentAnalysisRequest(BaseModel):
    query_text: str = Field(..., description="Document text or query string from OCR")
    doc_type: str = Field("Purchase_Order", description="Type: Purchase_Order, Bank_LC, or Shipment_Doc")
    obiz_delivery_date: Optional[str] = Field(None, description="Agreed OBIZ date (YYYY-MM-DD)")
    actual_delivery_date: Optional[str] = Field(None, description="Actual receipt date (YYYY-MM-DD)")

class DiscrepancyDetail(BaseModel):
    parameter: str
    status: str  
    observation: str

class ContractAnalysisResponse(BaseModel):
    document_id: str
    overall_compliance: bool
    lc_recommendation: str
    liquidated_damages_risk: str
    calculated_ld_amount: str
    discrepancies: List[DiscrepancyDetail]
    relevant_clauses_retrieved: List[str]
    confidence_score: float
    extracted_fields: dict[str, str] = Field(default_factory=dict)
    processed_documents: List[str] = Field(default_factory=list)
    requires_manual_review: bool = False
    webhook_dispatched: bool = False
