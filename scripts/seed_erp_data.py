import pandas as pd
from faker import Faker
import random
from datetime import timedelta

# Inisialisasi generator
fake = Faker('id_ID')

# Parameter vendor tiruan yang sesuai dengan tabel 'vendors' di init.sql
vendor_ids = ['VND-001', 'VND-002', 'VND-003', 'VND-004', 'VND-005']

data = []
for _ in range(10000):
    order_date = fake.date_between(start_date='-1y', end_date='today')
    # Target pengiriman 7 hingga 14 hari setelah order
    target_delivery = order_date + timedelta(days=random.randint(7, 14))
    
    # Simulasi keterlambatan aktual (80% tepat waktu, 20% telat)
    is_late = random.random() > 0.8
    delay_days = random.randint(1, 10) if is_late else random.randint(-3, 0)
    actual_delivery = target_delivery + timedelta(days=delay_days)

    data.append({
        'transaction_id': f"TRX-{fake.unique.random_number(digits=8)}",
        'vendor_id': random.choice(vendor_ids),
        'order_date': order_date,
        'target_delivery_date': target_delivery,
        'actual_delivery_date': actual_delivery,
        'order_volume': random.randint(50, 5000),
        'total_value': round(random.uniform(10_000_000, 500_000_000), 2)
    })

df_erp_dummy = pd.DataFrame(data)
df_erp_dummy.to_csv('dummy_erp_transactions.csv', index=False)
print("10.000 baris data ERP berhasil digenerate ke dummy_erp_transactions.csv")