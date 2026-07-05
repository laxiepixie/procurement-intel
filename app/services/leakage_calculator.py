import pandas as pd
import numpy as np

def compute_leakage(rules_df: pd.DataFrame, erp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Kalkulator kebocoran finansial murni. 
    DILARANG KERAS mengimpor pustaka database atau LLM di dalam modul ini.
    """
    # Fail-fast jika salah satu sumber data kosong
    if rules_df.empty or erp_df.empty:
        return pd.DataFrame()

    # 1. Penyatuan Data (Join) berdasarkan relasi vendor_id
    df = pd.merge(erp_df, rules_df, on='vendor_id', how='inner')
    
    # 2. Normalisasi Tipe Data Waktu
    df['target_delivery_date'] = pd.to_datetime(df['target_delivery_date'])
    df['actual_delivery_date'] = pd.to_datetime(df['actual_delivery_date'])
    df['total_value'] = pd.to_numeric(df['total_value'])
    
    # 3. Hitung Keterlambatan (Hanya ambil yang bernilai positif)
    df['delay_days'] = (df['actual_delivery_date'] - df['target_delivery_date']).dt.days
    df['delay_days'] = df['delay_days'].apply(lambda x: max(0, x)) 
    
    # 4. Mesin Kalkulasi Denda
    def calculate_penalty(row):
        # Abaikan jika tidak telat atau kontrak tidak memiliki denda SLA
        if row['delay_days'] <= 0 or pd.isna(row['late_penalty_percentage']):
            return 0.0
            
        penalty_pct = float(row['late_penalty_percentage']) / 100.0
        
        # Jika tidak ada batas maksimal di kontrak, asumsikan 100% dari nilai transaksi
        max_penalty_pct = float(row['max_penalty_percentage']) / 100.0 if not pd.isna(row['max_penalty_percentage']) else 1.0
        
        # Konversi pengali matriks waktu
        multiplier = row['delay_days']
        if row['penalty_metric'] == 'per_minggu':
            multiplier = row['delay_days'] / 7.0
        elif row['penalty_metric'] == 'per_bulan':
            multiplier = row['delay_days'] / 30.0
            
        calculated_penalty = penalty_pct * multiplier * row['total_value']
        max_penalty = max_penalty_pct * row['total_value']
        
        # Denda aktual tidak boleh melebihi batas maksimal kontrak
        return min(calculated_penalty, max_penalty)

    # Aplikasikan fungsi kalkulasi ke setiap baris
    df['calculated_leakage'] = df.apply(calculate_penalty, axis=1)
    
    # 5. Filtrasi Akhir: Buang transaksi yang aman (tidak ada kebocoran denda)
    leakage_df = df[df['calculated_leakage'] > 0].copy()
    
    # Urutkan dari kerugian terbesar ke terkecil
    leakage_df = leakage_df.sort_values(by='calculated_leakage', ascending=False)
    
    return leakage_df