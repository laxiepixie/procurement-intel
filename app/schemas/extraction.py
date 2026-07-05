from pydantic import BaseModel, Field
from typing import Optional

class SLATerm(BaseModel):
    late_penalty_percentage: Optional[float] = Field(
        None, 
        description="Persentase denda keterlambatan absolut. Contoh: 5% direpresentasikan sebagai 5.0"
    )
    penalty_metric: Optional[str] = Field(
        None, 
        description="Satuan waktu berlakunya denda keterlambatan. Harus salah satu dari: 'per_hari', 'per_minggu', 'per_bulan'"
    )
    max_penalty_percentage: Optional[float] = Field(
        None, 
        description="Batas maksimal kumulatif denda yang bisa dijatuhkan. Contoh: 10% direpresentasikan sebagai 10.0"
    )

class ContractExtraction(BaseModel):
    is_sla_clause: bool = Field(
        ..., 
        description="Bernilai True HANYA JIKA teks mengandung aturan denda keterlambatan, SLA, atau penalti pengiriman."
    )
    sla_terms: Optional[SLATerm] = Field(
        None, 
        description="Parameter denda. Diisi jika is_sla_clause adalah True."
    )