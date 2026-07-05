import fitz  # PyMuPDF untuk ekstraksi teks dan layout
import pdfplumber # Untuk deteksi grid tabel deterministik (Sesuai Phase 2)

def parse_contract_document(file_path: str) -> str:
    """
    Fungsi murni (pure function) untuk ekstraksi dokumen.
    TIDAK ADA pemanggilan LLM. TIDAK ADA chunking di sini.
    """
    extracted_content = ""
    
    try:
        # Tahap 1: Ekstraksi teks berbasis layout spasial menggunakan PyMuPDF
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc):
            extracted_content += f"\n--- Halaman {page_num + 1} ---\n"
            extracted_content += page.get_text("text") + "\n"
        doc.close()

        # Tahap 2: Deteksi tabel deterministik menggunakan pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    extracted_content += f"\n[Tabel Terdeteksi - Halaman {i + 1}, Indeks {j}]\n"
                    for row in table:
                        # Membersihkan nilai None dari sel tabel yang kosong
                        cleaned_row = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                        extracted_content += " | ".join(cleaned_row) + "\n"
                        
        return extracted_content

    except Exception as e:
        print(f"Kegagalan fatal pada pdf_parser: {e}")
        # Dalam produksi, ini harus menggunakan modul logging, bukan print.
        return ""