import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Tata Steel | Finance & Accounts Intelligence Engine",
    page_icon="📄",
    layout="wide"
)

API_URL = os.getenv("IDP_API_URL", "http://127.0.0.1:8001/api/v1/analyze-documents")

st.title(" Enterprise Contract & LC Verification Platform")
st.subheader("Powered by Hybrid Vector-BM25 Search & Reranking RAG Architecture")
st.divider()
col_left, col_right = st.columns([1, 1])
with col_left:
    st.markdown("###  Automated document intake")
    uploads = st.file_uploader(
        "Upload a PO, GRN, LC, shipment document, or scan batch",
        type=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "txt"],
        accept_multiple_files=True,
        help="Dates, PO number, and document type are detected automatically."
    )
    submit_btn = st.button("Analyze uploaded documents", use_container_width=True, disabled=not uploads)
with col_right:
    st.markdown("###  Automated Assessment Output")
    if submit_btn:
        upload_files = [("files", (file.name, file.getvalue(), file.type)) for file in uploads]
        with st.spinner("Extracting documents, validating fields, and running policy checks..."):
            try:
                response = requests.post(API_URL, files=upload_files, timeout=90)
                if response.status_code == 200:
                    data = response.json()
                    m1, m2 = st.columns(2)
                    m1.metric("Compliance Status", "PASSED" if data["overall_compliance"] else "FAILED")
                    m2.metric("Confidence Score", f"{data['confidence_score']*100:.1f}%")
                    st.error(f"**Liquidated Damage (LD) Risk:** {data['liquidated_damages_risk']}")
                    st.warning(f"**Calculated Penalty:** {data['calculated_ld_amount']}")
                    st.info(f"**LC Recommendation:** {data['lc_recommendation']}")
                    if data.get("requires_manual_review"):
                        st.warning("Some essential fields could not be verified. Review the source documents before approval.")
                    if data.get("webhook_dispatched"):
                        st.success("Compliance assessment posted to the configured enterprise webhook.")
                    st.markdown("#### Extracted document fields")
                    st.json(data.get("extracted_fields", {}))
                    st.caption("Processed: " + "; ".join(data.get("processed_documents", [])))
                    
                 
                    st.markdown("####  Discrepancy Parameter Check")
                    st.dataframe(data["discrepancies"], use_container_width=True)

                    st.markdown("#### Retrieved Policy Clauses (RAG Context)")
                    for i, clause in enumerate(data["relevant_clauses_retrieved"], 1):
                        st.caption(f"**Clause {i}:** {clause}")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to FastAPI backend. Ensure uvicorn is running.\n\nError: {e}")
