from sqlalchemy import create_engine, text
engine = create_engine("postgresql://admin:adminpassword@localhost:5432/procurement_intel")

with engine.begin() as conn:
    conn.execute(text("""
        INSERT INTO vendors (vendor_id, vendor_name, email) VALUES 
        ('VND-003', 'Gamma Manufaktur Solusi', 'gamma@vendor.com');
    """))
print("Data vendor berhasil diinjeksi.")