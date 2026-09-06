import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sales_data(num_rows=120000, output_path="c:/Users/eujwa/insightflow/data/sales.csv"):
    np.random.seed(42)
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range = (end_date - start_date).days
    
    # Base configuration
    regions = ['North', 'South', 'East', 'West', 'Central']
    region_weights = [0.28, 0.18, 0.24, 0.20, 0.10]
    
    segments = ['Enterprise', 'Mid-Market', 'SMB', 'Consumer']
    segment_weights = [0.40, 0.25, 0.20, 0.15]
    
    categories = {
        'Cloud Solutions': ['Cloud Hosting Pro', 'Enterprise AI Suite', 'Data Lakehouse Storage', 'Serverless Compute'],
        'Hardware': ['Workstation Pro', 'Edge Server X1', 'Network Gateway Gen4', 'Security Appliance'],
        'Software': ['DevOps Automation', 'Analytics Studio', 'CRM Enterprise', 'CyberDefense Suite'],
        'Professional Services': ['Implementation & Onboarding', 'Cloud Migration Consulting', 'Annual Maintenance', '24/7 Premium Support']
    }
    
    all_products = []
    product_category_map = {}
    base_prices = {
        'Cloud Hosting Pro': 1200.0,
        'Enterprise AI Suite': 3500.0,
        'Data Lakehouse Storage': 850.0,
        'Serverless Compute': 450.0,
        'Workstation Pro': 2200.0,
        'Edge Server X1': 4800.0,
        'Network Gateway Gen4': 1600.0,
        'Security Appliance': 3100.0,
        'DevOps Automation': 950.0,
        'Analytics Studio': 1800.0,
        'CRM Enterprise': 2400.0,
        'CyberDefense Suite': 2900.0,
        'Implementation & Onboarding': 5000.0,
        'Cloud Migration Consulting': 7500.0,
        'Annual Maintenance': 1500.0,
        '24/7 Premium Support': 2000.0
    }
    
    for cat, prods in categories.items():
        for p in prods:
            all_products.append(p)
            product_category_map[p] = cat
            
    salespeople = [
        'Sarah Jenkins', 'Michael Chang', 'David Ross', 'Elena Rostova', 
        'Amara Okafor', 'James Wilson', 'Priya Sharma', 'Lucas Meyer'
    ]
    
    customer_ids = [f"CUST-{1000 + i}" for i in range(4000)]
    
    records = []
    
    for i in range(num_rows):
        day_offset = np.random.randint(0, date_range + 1)
        order_date = start_date + timedelta(days=day_offset)
        month = order_date.month
        
        region = np.random.choice(regions, p=region_weights)
        segment = np.random.choice(segments, p=segment_weights)
        prod = np.random.choice(all_products)
        cat = product_category_map[prod]
        customer_id = np.random.choice(customer_ids)
        salesperson = np.random.choice(salespeople)
        
        # Quantity
        if segment == 'Enterprise':
            quantity = np.random.randint(3, 25)
        elif segment == 'Mid-Market':
            quantity = np.random.randint(2, 10)
        else:
            quantity = np.random.randint(1, 5)
            
        unit_price = base_prices[prod] * np.random.uniform(0.95, 1.05)
        
        # Discount logic
        discount = 0.0
        if segment == 'Enterprise' and np.random.rand() > 0.4:
            discount = np.random.choice([0.05, 0.10, 0.15, 0.20])
        elif np.random.rand() > 0.7:
            discount = np.random.choice([0.05, 0.10])
            
        # Realistic business scenario: August decline anomaly!
        # In August (month 8), Enterprise deals in North region and 'Enterprise AI Suite' saw major drop
        if month == 8:
            if segment == 'Enterprise' and region == 'North':
                if np.random.rand() < 0.65:  # 65% cancellation/drop
                    continue
            if prod == 'Enterprise AI Suite':
                if np.random.rand() < 0.50:
                    continue
                    
        # In June/July, massive growth
        if month in [6, 7]:
            if segment == 'Enterprise':
                unit_price *= 1.08
                quantity = int(quantity * 1.15)
                
        gross_revenue = quantity * unit_price
        revenue = gross_revenue * (1.0 - discount)
        cost = gross_revenue * np.random.uniform(0.45, 0.65)
        profit = revenue - cost
        profit_margin = (profit / revenue) if revenue > 0 else 0.0
        
        records.append({
            'order_id': f"ORD-{20250000 + i}",
            'order_date': order_date.strftime('%Y-%m-%d'),
            'customer_id': customer_id,
            'customer_segment': segment,
            'region': region,
            'salesperson': salesperson,
            'product_category': cat,
            'product_name': prod,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'discount': round(discount, 2),
            'gross_revenue': round(gross_revenue, 2),
            'revenue': round(revenue, 2),
            'cost': round(cost, 2),
            'profit': round(profit, 2),
            'profit_margin': round(profit_margin, 4)
        })
        
    df = pd.DataFrame(records)
    
    # Introduce small realistic data quality quirks (e.g. 0.05% nulls for testing Data Quality / Profiler Agent)
    null_idx = np.random.choice(df.index, size=int(len(df) * 0.0005), replace=False)
    df.loc[null_idx, 'discount'] = np.nan
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows of sales data at {output_path}")

if __name__ == "__main__":
    generate_sales_data()
