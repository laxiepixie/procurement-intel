import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional

# Konfigurasi Koneksi (Di produksi mutlak dipindah ke app/core/config.py / file .env)
# URL disesuaikan dengan kredensial dari docker-compose.yml milikmu
DB_URL = "postgresql://admin:adminpassword@localhost:5432/procurement_intel"
engine = create_engine(DB_URL)

def fetch_erp_transactions_as_df(vendor_id: Optional[str] = None) -> pd.DataFrame:
    """
    Menarik data transaksi logistik dari PostgreSQL dan langsung mengonversinya 
    menjadi Pandas DataFrame untuk disuplai ke leakage_calculator.py.
    """
    try:
        if vendor_id:
            # Menggunakan parameterized query (text()) untuk mencegah SQL Injection
            query = text("SELECT * FROM erp_transactions WHERE vendor_id = :v_id")
            df = pd.read_sql_query(query, engine, params={"v_id": vendor_id})
        else:
            query = text("SELECT * FROM erp_transactions")
            df = pd.read_sql_query(query, engine)
            
        return df
        
    except Exception as e:
        print(f"[Fatal Error] Gagal mengeksekusi kueri pada erp_repo: {e}")
        # Mengembalikan DataFrame kosong agar leakage_calculator tidak crash (Fail-Safe)
        return pd.DataFrame()