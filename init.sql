-- Mengaktifkan ekstensi pgvector untuk pencarian ANN
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabel Master Vendor
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id VARCHAR(50) PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    email VARCHAR(255)
);

-- Tabel Transaksi ERP (Tempat Injeksi CSV)
CREATE TABLE IF NOT EXISTS erp_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    vendor_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    target_delivery_date DATE NOT NULL,
    actual_delivery_date DATE NOT NULL,
    order_volume INT NOT NULL,
    total_value NUMERIC(15, 2) NOT NULL
);

-- Tabel Kontrak untuk Jalur Ekstraksi LLM
CREATE TABLE IF NOT EXISTS contracts (
    contract_id SERIAL PRIMARY KEY,
    vendor_id VARCHAR(50) REFERENCES vendors(vendor_id),
    contract_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Vektor untuk RAG (Menggunakan model 768 dimensi nomic-embed-text)
CREATE TABLE IF NOT EXISTS contract_embeddings (
    id SERIAL PRIMARY KEY,
    contract_id INT REFERENCES contracts(contract_id),
    chunk_text TEXT NOT NULL,
    embedding vector(768)
);

-- Mendaftarkan Indeks HNSW untuk kebutuhan Kueri Semantik (ANN Search)
CREATE INDEX IF NOT EXISTS contract_embeddings_hsnw_idx 
ON contract_embeddings USING hnsw (embedding vector_cosine_ops);

-- Populasi Awal Data Vendor agar Foreign Key pada CSV Terpenuhi
INSERT INTO vendors (vendor_id, vendor_name, email) VALUES
('VND-001', 'Vendor Alfa Utama', 'alfa@vendor.com'),
('VND-002', 'Beta Logistik Nusantara', 'beta@vendor.com'),
('VND-003', 'Gamma Manufaktur Solusi', 'gamma@vendor.com'),
('VND-004', 'Delta Distribusi Global', 'delta@vendor.com'),
('VND-005', 'Epsilon Industri Tekno', 'epsilon@vendor.com')
ON CONFLICT (vendor_id) DO NOTHING;