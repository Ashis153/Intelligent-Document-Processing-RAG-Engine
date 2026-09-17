from fastapi import FastAPI, HTTPException, File, UploadFile
from backend.schemas import DocumentAnalysisRequest, ContractAnalysisResponse
from backend.rag_engine import AdvancedRAGPipeline
from backend.idp_pipeline import (ExtractedDocument, classify_document, extract_fields,
                                  fetch_erp_delivery_date, local_ocr, publish_assessment,
                                  vision_retry)

app = FastAPI(
    title="Tata Steel - Enterprise IDP & Advanced RAG System",
    description="FastAPI service for contract parsing, LC checks, and LD validation.",
    version="2.0.0"
)

rag_service = AdvancedRAGPipeline()
@app.get("/")
def read_root():
    return {"status": "Online", "system": "FastAPI Advanced RAG Engine"}
@app.post("/api/v1/analyze-contract", response_model=ContractAnalysisResponse)
async def analyze_contract(payload: DocumentAnalysisRequest):
    try:
        results = rag_service.evaluate_compliance(
            query=payload.query_text,
            obiz_date=payload.obiz_delivery_date,
            actual_date=payload.actual_delivery_date
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")


@app.post("/api/v1/analyze-documents", response_model=ContractAnalysisResponse)
async def analyze_documents(files: list[UploadFile] = File(...)):
    """Fully automated PO/GRN/LC batch intake endpoint."""
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least one document.")
    extracted: list[ExtractedDocument] = []
    merged_fields: dict[str, str] = {}
    for upload in files:
        content = await upload.read()
        if not content:
            continue
        text = local_ocr(content, upload.filename or "document", upload.content_type)
        fields, confidence = extract_fields(text)
        # Validation-agent correction loop: try vision again when no core
        # fields can be trusted from the initial recognition pass.
        if confidence < 0.81:
            retry_text = vision_retry(content, upload.filename or "document", upload.content_type)
            if retry_text:
                retry_fields, retry_confidence = extract_fields(retry_text)
                if retry_confidence > confidence:
                    text, fields, confidence = retry_text, retry_fields, retry_confidence
        document_type = classify_document(text, upload.filename or "")
        extracted.append(ExtractedDocument(upload.filename or "document", text, document_type, confidence, fields, confidence < 0.81))
        # GRN values should override generic PO delivery fields, while the PO
        # remains the authoritative source for the agreed schedule.
        for key, value in fields.items():
            if key not in merged_fields or (key == "actual_delivery_date" and document_type == "Goods_Receipt_Note"):
                merged_fields[key] = value
    if not extracted:
        raise HTTPException(status_code=400, detail="No readable documents were uploaded.")
    erp_date = fetch_erp_delivery_date(merged_fields.get("purchase_order_number"))
    if erp_date:
        merged_fields["actual_delivery_date"] = erp_date
    combined_text = "\n\n".join(item.text for item in extracted)
    result = rag_service.evaluate_compliance(combined_text, merged_fields.get("obiz_delivery_date"), merged_fields.get("actual_delivery_date"))
    result["document_id"] = merged_fields.get("purchase_order_number", "UNRESOLVED-PO")
    result["extracted_fields"] = merged_fields
    result["processed_documents"] = [f"{item.filename} ({item.document_type}, {item.confidence:.0%})" for item in extracted]
    result["requires_manual_review"] = any(item.needs_review for item in extracted) or not all(
        merged_fields.get(key) for key in ("purchase_order_number", "obiz_delivery_date", "actual_delivery_date")
    )
    result["webhook_dispatched"] = publish_assessment(result)
    return result
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
