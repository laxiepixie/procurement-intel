import re
from typing import List, Dict

def chunk_contract_text(text: str, max_chunk_size: int = 1500, overlap_percent: float = 0.15) -> List[Dict]:
    """
    Memecah teks dokumen menjadi potongan struktural berdasarkan deteksi batas pasal/klausul.
    Menambahkan tagging parent_clause_id sesuai dengan cetak biru arsitektur.
    """
    if not text:
        return []

    # Deteksi pola Regex untuk struktur hukum standar 
    # (Mendeteksi: "Pasal 1", "Bagian A", "1.1.", "Article X")
    clause_pattern = re.compile(
        r'(?i)^\s*(pasal\s+\d+|bagian\s+[a-z]+|\d+\.\d+[\.\d]*|article\s+\d+)', 
        re.MULTILINE
    )
    
    matches = list(clause_pattern.finditer(text))
    chunks = []
    
    # Kondisi anomali: Jika dokumen tidak memiliki struktur pasal baku
    if not matches:
        return _apply_mathematical_chunking(text, max_chunk_size, overlap_percent, parent_id="unstructured_doc")

    for i, match in enumerate(matches):
        # Ekstraksi ID Pasal (misal: "Pasal 1")
        parent_clause_id = match.group(1).strip()
        start_idx = match.start()
        
        # Titik potong akhir adalah titik awal pasal berikutnya
        if i + 1 < len(matches):
            end_idx = matches[i + 1].start()
        else:
            end_idx = len(text)
            
        clause_text = text[start_idx:end_idx].strip()
        
        # Validasi batas ukuran jendela konteks Llama 3
        if len(clause_text) > max_chunk_size:
            # Jika satu pasal terlalu panjang, potong secara paksa dengan overlap 15%
            sub_chunks = _apply_mathematical_chunking(clause_text, max_chunk_size, overlap_percent, parent_clause_id)
            chunks.extend(sub_chunks)
        else:
            chunks.append({
                "parent_clause_id": parent_clause_id,
                "chunk_text": clause_text
            })
            
    return chunks

def _apply_mathematical_chunking(text: str, max_size: int, overlap_pct: float, parent_id: str) -> List[Dict]:
    """
    Fungsi internal (fallback) untuk chunking matematis murni dengan toleransi overlap.
    Dieksekusi hanya jika pasal melebihi max_size atau dokumen tidak terstruktur.
    """
    chunks = []
    text_length = len(text)
    overlap_size = int(max_size * overlap_pct)
    start = 0
    
    while start < text_length:
        end = start + max_size
        chunks.append({
            "parent_clause_id": parent_id,
            "chunk_text": text[start:end].strip()
        })
        start += (max_size - overlap_size)
        
    return chunks