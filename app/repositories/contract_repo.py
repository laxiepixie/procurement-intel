import pandas as pd
from sqlalchemy import create_engine, text
from app.schemas.extraction import SLATerm

# Konfigurasi Koneksi Absolut
DB_URL = "postgresql://admin:adminpassword@localhost:5432/procurement_intel"
engine = create_engine(DB_URL)

def initialize_missing_schema():
    """
    [CRITICAL] Fungsi penambal arsitektur. 
    Mengeksekusi pembuatan tabel sla_terms jika belum ada saat aplikasi menyala.
    """
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sla_terms (
                id SERIAL PRIMARY KEY,
                vendor_id VARCHAR(50) REFERENCES vendors(vendor_id),
                late_penalty_percentage NUMERIC(5,2),
                penalty_metric VARCHAR(50),
                max_penalty_percentage NUMERIC(5,2)
            );
        """))
        print("[System] Validasi skema tabel sla_terms selesai.")

def save_sla_term(vendor_id: str, term: SLATerm):
    """
    Menyimpan hasil JSON Llama 3 yang sudah divalidasi Pydantic ke PostgreSQL.
    Menerapkan pemetaan tipe data (float Python ke NUMERIC SQL).
    """
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO sla_terms (vendor_id, late_penalty_percentage, penalty_metric, max_penalty_percentage)
                VALUES (:vid, :pen_pct, :metric, :max_pct)
            """),
            {
                "vid": vendor_id,
                "pen_pct": term.late_penalty_percentage,
                "metric": term.penalty_metric,
                "max_pct": term.max_penalty_percentage
            }
        )

def fetch_contracted_rules_df() -> pd.DataFrame:
    """
    Menarik aturan Denda/SLA untuk disuplai murni ke leakage_calculator.py.
    """
    try:
        # Menarik kolom secara spesifik agar identik dengan ekspektasi DataFrame mesin hitung
        query = text("""
            SELECT vendor_id, late_penalty_percentage, penalty_metric, max_penalty_percentage 
            FROM sla_terms
        """)
        return pd.read_sql_query(query, engine)
    except Exception as e:
        print(f"[Fatal] Gagal menarik aturan SLA: {e}")
        return pd.DataFrame()

# Eksekusi instan saat modul diimpor pertama kali oleh FastAPI
initialize_missing_schema()