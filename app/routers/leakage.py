from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas.api_models import LeakageReport
from app.repositories.erp_repo import fetch_erp_transactions_as_df
from app.repositories.contract_repo import fetch_contracted_rules_df
from app.services.leakage_calculator import compute_leakage

router = APIRouter(tags=["Leakage Analysis"])

@router.get("/leakage-analysis", response_model=LeakageReport)
def analyze_leakage(vendor_id: Optional[str] = None):
    """
    Titik akhir murni. Orkestrasi: Repositori -> DataFrame -> Kalkulator Pandas -> Klien.
    """
    # 1. Ekstraksi Data via Repositori
    erp_df = fetch_erp_transactions_as_df(vendor_id)
    rules_df = fetch_contracted_rules_df()

    if erp_df.empty:
        raise HTTPException(status_code=404, detail="Data transaksi ERP tidak ditemukan atau kosong.")
    
    # 2. Operasi Komputasi Terisolasi
    try:
        # Jika rules_df kosong (belum ada kontrak di-parsing), hasil leakage_df juga akan kosong secara aman
        leakage_df = compute_leakage(rules_df, erp_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kegagalan mesin kalkulasi internal: {e}")

    # 3. Serialisasi ke JSON
    # Konversi DataFrame NaN/NaT menjadi None agar valid di JSON Pydantic
    leakage_df = leakage_df.where(leakage_df.notnull(), None)
    
    return LeakageReport(
        status="success",
        total_leaks_found=len(leakage_df),
        data=leakage_df.to_dict(orient="records")
    )