import json
import requests
from pydantic import ValidationError
from typing import Optional
from app.schemas.extraction import ContractExtraction

# Konfigurasi LLM (Di produksi, ini harus ditarik dari .env via app/core/config.py)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def extract_clause_data(chunk_text: str, max_retries: int = 3) -> Optional[ContractExtraction]:
    """
    Mengirim potongan teks ke Llama 3 untuk ekstraksi struktural.
    Dilengkapi dengan mekanisme Pydantic retry-loop sesuai standar cetak biru.
    """
    
    # Prompt dengan "Few-Shot Examples" untuk mengarahkan model parameter 8B
    system_prompt = f"""
    Anda adalah analis hukum korporat B2B. Tugas Anda mengekstrak klausul denda keterlambatan (SLA) dari teks kontrak ke dalam format JSON yang presisi.
    
    ATURAN JSON MUTLAK:
    - is_sla_clause: true HANYA JIKA teks berisi denda, penalti, atau potongan tagihan karena keterlambatan pengiriman.
    - late_penalty_percentage: persentase denda (float, contoh: 5.0). Null jika tidak ada.
    - penalty_metric: rentang waktu denda ("per_hari", "per_minggu", "per_bulan"). Null jika tidak ada.
    - max_penalty_percentage: batas maksimal denda kumulatif (float, contoh: 10.0). Null jika tidak ada.

    CONTOH 1 (Valid SLA):
    Teks: "Apabila vendor terlambat mengirimkan pasokan, dikenakan denda 1% per hari dari total Invoice, maksimal 5%."
    Output: {{"is_sla_clause": true, "sla_terms": {{"late_penalty_percentage": 1.0, "penalty_metric": "per_hari", "max_penalty_percentage": 5.0}}}}

    CONTOH 2 (Bukan SLA - Klausul Umum):
    Teks: "Pembayaran akan ditransfer dalam waktu 30 hari kalender setelah Berita Acara Serah Terima ditandatangani."
    Output: {{"is_sla_clause": false, "sla_terms": null}}
    
    EKSTRAK TEKS BERIKUT:
    {chunk_text}
    """
    
    current_prompt = system_prompt
    
    for attempt in range(max_retries):
        payload = {
            "model": MODEL_NAME,
            "prompt": current_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0 # Mematikan probabilitas kreativitas (absolut deterministik)
            }
        }
        
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=45)
            response.raise_for_status()
            
            # Mengekstrak string JSON dari Ollama
            result_text = response.json().get("response", "{}")
            
            # [CRITICAL STEP] Validasi tipe data ketat menggunakan Pydantic
            extracted_data = ContractExtraction.model_validate_json(result_text)
            
            return extracted_data
            
        except ValidationError as e:
            # Mekanisme Self-Correction: Menangkap error Pydantic dan mengembalikannya ke Llama 3
            print(f"[Warning] Validasi JSON gagal pada percobaan ke-{attempt + 1}. Menginstruksikan koreksi ke model...")
            error_feedback = f"\nPERINGATAN SISTEM: JSON yang Anda hasilkan melanggar skema Pydantic. Berikut adalah pesan errornya:\n{e}\nPerbaiki dan hasilkan ulang JSON yang benar."
            current_prompt += error_feedback
            
        except requests.exceptions.RequestException as e:
            print(f"[Fatal] Koneksi jaringan ke Ollama terputus: {e}")
            break
            
    # Eksekusi blok ini terjadi jika model gagal memperbaiki JSON setelah 3 kali percobaan (Exhausted)
    print("[Error] Model Llama 3 gagal memproduksi skema yang valid setelah maksimal percobaan.")
    return None