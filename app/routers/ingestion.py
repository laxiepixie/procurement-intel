from fastapi import APIRouter, UploadFile, File
from app.services.pdf_parser import parse_contract_document
from app.services.chunker import chunk_contract_text
from app.services.llm_extractor import extract_clause_data
from app.repositories.contract_repo import save_sla_term
import os

router = APIRouter(tags=["Ingestion"])

@router.post("/contracts/upload")
async def upload_contract(vendor_id: str, file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        raw_text = parse_contract_document(temp_path)
        chunks = chunk_contract_text(raw_text)
        
        for chunk in chunks:
            extraction = extract_clause_data(chunk["chunk_text"])
            if extraction and extraction.is_sla_clause:
                save_sla_term(vendor_id, extraction.sla_terms)
        
        return {"status": "success", "message": f"Kontrak dari {vendor_id} diproses."}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)