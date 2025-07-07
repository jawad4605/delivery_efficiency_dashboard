"""
Enhanced Data Generation Script for Delivery Efficiency Dashboard
Generates realistic sample data with better distributions and patterns
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from faker import Faker

# Initialize Faker for realistic names and data
fake = Faker()

# Create data directory if not exists
os.makedirs('data', exist_ok=True)

# ---------- Device Master Data ----------
np.random.seed(42)
random.seed(42)
num_devices = 75  # Increased from 50 for better visualization

# Expanded city data with realistic distributions
cities = {
    'New York': {
        'coords': (40.7128, -74.0060),
        'weight': 0.35,
        'zones': ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
    },
    'Los Angeles': {
        'coords': (34.0522, -118.2437),
        'weight': 0.25,
        'zones': ['Downtown', 'Westside', 'San Fernando', 'San Gabriel', 'Harbor']
    },
    'Chicago': {
        'coords': (41.8781, -87.6298),
        'weight': 0.15,
        'zones': ['North', 'South', 'West', 'East', 'Central']
    },
    'Houston': {
        'coords': (29.7604, -95.3698),
        'weight': 0.15,
        'zones': ['Northside', 'Southside', 'East End', 'Westside', 'Downtown']
    },
    'Phoenix': {
        'coords': (33.4484, -112.0740),
        'weight': 0.10,
        'zones': ['North Valley', 'South Mountain', 'East Valley', 'West Valley', 'Downtown']
    }
}

# Generate devices with realistic distributions
devices = []
city_choices = random.choices(
    list(cities.keys()), 
    weights=[c['weight'] for c in cities.values()], 
    k=num_devices
)

for i in range(1, num_devices + 1):
    city = city_choices[i-1]
    city_data = cities[city]
    lat, lon = city_data['coords']
    
    # Add realistic geographic distribution within city
    lat += np.random.normal(0, 0.1)
    lon += np.random.normal(0, 0.1)
    
    # More realistic status distribution based on time of day
    hour = datetime.now().hour
    if hour >= 6 and hour < 10:
        status_probs = [0.6, 0.15, 0.2, 0.05]  # More moving in morning
    elif hour >= 10 and hour < 16:
        status_probs = [0.5, 0.25, 0.2, 0.05]  # More idling midday
    elif hour >= 16 and hour < 20:
        status_probs = [0.65, 0.1, 0.2, 0.05]  # More moving in evening
    else:
        status_probs = [0.2, 0.1, 0.1, 0.6]  # Mostly inactive at night
    
    status = np.random.choice(
        ['Moving', 'Idling', 'On-route', 'Inactive'],
        p=status_probs
    )
    
    # Assign zone based on city zones
    zone = random.choice(city_data['zones'])
    
    devices.append({
        'device_id': f'D{i:03d}',
        'city': city,
        'lat': lat,
        'lon': lon,
        'status': status,
        'zone': f'{zone}',
        'last_maintenance': (datetime.now() - timedelta(days=np.random.randint(0, 180))).strftime('%Y-%m-%d')
    })

master_df = pd.DataFrame(devices)
master_df.to_csv('data/device_master.csv', index=False)

# ---------- Performance Data ----------
performance = []
for device in devices:
    # Base performance based on city and status
    city_factor = {
        'New York': 1.2,
        'Los Angeles': 1.1,
        'Chicago': 1.0,
        'Houston': 0.9,
        'Phoenix': 0.8
    }[device['city']]
    
    status_factor = {
        'Moving': 1.1,
        'On-route': 1.0,
        'Idling': 0.7,
        'Inactive': 0.1
    }[device['status']]
    
    # Generate realistic performance metrics
    base_deliveries = np.random.randint(5, 50)
    total_deliveries = int(base_deliveries * city_factor * status_factor * np.random.uniform(0.8, 1.2))
    
    # More realistic speed distribution
    avg_speed = np.random.normal(35, 10)
    avg_speed = max(10, min(65, avg_speed))  # Clamp between 10-65 mph
    
    # Uptime based on maintenance age
    maintenance_days = (datetime.now() - datetime.strptime(device['last_maintenance'], '%Y-%m-%d')).days
    uptime = 95 - (maintenance_days / 10)  # Decrease uptime by 1% every 10 days since maintenance
    uptime = max(70, min(99, uptime + np.random.normal(0, 3)))
    
    performance.append({
        'device_id': device['device_id'],
        'total_deliveries': total_deliveries,
        'avg_speed': round(avg_speed, 1),
        'uptime_percent': round(uptime, 1),
        'fuel_efficiency': round(np.random.normal(8.5, 1.5), 1),  # MPG
        'distance_traveled': round(total_deliveries * np.random.uniform(5, 15)),  # Miles
    })

perf_df = pd.DataFrame(performance)
perf_df.to_csv('data/performance.csv', index=False)

# ---------- Loads by Day ----------
# Generate 4 weeks of data with weekly patterns
dates = [datetime.now() - timedelta(days=i) for i in range(28)]
loads = []
weekday_pattern = [1.0, 1.1, 1.2, 1.1, 1.0, 0.7, 0.5]  # Weekday/weekend pattern

for i, date in enumerate(dates):
    day_of_week = date.weekday()
    
    # Base load with weekly pattern and slight upward trend
    base_load = 100 + (i * 0.5)  # Slight upward trend over time
    daily_load = base_load * weekday_pattern[day_of_week]
    
    # Add some randomness
    daily_load *= np.random.uniform(0.9, 1.1)
    
    # Special events (holidays, etc.)
    if date.month == 12 and date.day in [24, 25, 31]:
        daily_load *= 1.5  # Holiday surge
    elif date.month == 7 and date.day == 4:
        daily_load *= 0.7  # Holiday drop
    
    loads.append({
        'date': date,
        'loads': int(daily_load),
        'week': 'current' if i < 7 else ('last' if i < 14 else 'older'),
        'day_of_week': date.strftime('%A'),
        'is_weekend': day_of_week >= 5
    })

loads_df = pd.DataFrame(loads)
loads_df.to_csv('data/loads_by_day.csv', index=False)

# ---------- Idle Heatmap ----------
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = []

# Create idle patterns that vary by day and device
for device in devices[:50]:  # Only first 50 devices for better visualization
    # Base idle time depends on city and device age
    base_idle = {
        'New York': 45,
        'Los Angeles': 60,
        'Chicago': 50,
        'Houston': 55,
        'Phoenix': 65
    }[device['city']]
    
    # Add some device-specific variation
    base_idle += np.random.randint(-15, 15)
    
    for day in days:
        # Weekends have different idle patterns
        if day in ['Saturday', 'Sunday']:
            idle_min = base_idle * np.random.uniform(1.2, 1.5)
        else:
            idle_min = base_idle * np.random.uniform(0.9, 1.1)
            
        # Add daily variation
        day_factor = {
            'Monday': 1.1,
            'Tuesday': 1.0,
            'Wednesday': 0.9,
            'Thursday': 1.0,
            'Friday': 1.2,
            'Saturday': 1.3,
            'Sunday': 1.5
        }[day]
        
        idle_min *= day_factor
        
        # Ensure idle time is reasonable
        idle_min = max(0, min(180, idle_min + np.random.normal(0, 10)))
        
        heatmap_data.append({
            'device_id': device['device_id'],
            'day': day,
            'idle_minutes': int(idle_min)
        })

heat_df = pd.DataFrame(heatmap_data).pivot(index='device_id', columns='day', values='idle_minutes')
heat_df.to_csv('data/idle_heatmap.csv')

# ---------- Sankey Flows ----------
# More detailed flow data with realistic patterns
zones = list(set([d['zone'] for d in devices]))
flows = []

# Warehouse to zone flows
for zone in zones:
    flows.append({
        'src': 'Warehouse',
        'trg': zone,
        'count': np.random.randint(50, 200),
        'type': 'dispatch'
    })

# Zone to status flows
status_weights = {
    'Moving': 0.6,
    'Idling': 0.25,
    'On-route': 0.1,
    'Inactive': 0.05
}

for zone in zones:
    total = np.random.randint(30, 150)
    for status, weight in status_weights.items():
        flows.append({
            'src': zone,
            'trg': status,
            'count': int(total * weight * np.random.uniform(0.8, 1.2)),
            'type': 'status'
        })

flows_df = pd.DataFrame(flows)
flows_df.to_csv('data/sankey_flows.csv', index=False)

# ---------- Warehouse Events ----------
events = []
event_types = {
    'Departure': 0.4,
    'Arrival': 0.4,
    'Maintenance': 0.1,
    'Inspection': 0.05,
    'Alert': 0.05
}

# Generate events for the last 7 days
for i in range(250):  # More events for better visualization
    hours_ago = np.random.uniform(0, 168)  # Last 7 days
    timestamp = (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
    
    event_type = random.choices(
        list(event_types.keys()),
        weights=list(event_types.values()),
        k=1
    )[0]
    
    # Choose a device, weighted by activity
    device = random.choices(
        devices,
        weights=[d['status'] != 'Inactive' and 2 or 1 for d in devices],
        k=1
    )[0]
    
    events.append({
        'timestamp': timestamp,
        'event_type': event_type,
        'device_id': device['device_id'],
        'location': device['zone'],
        'details': fake.sentence() if event_type in ['Maintenance', 'Inspection', 'Alert'] else ''
    })

events_df = pd.DataFrame(events).sort_values('timestamp', ascending=False)
events_df.to_csv('data/warehouse_events.csv', index=False)

# ---------- Summary Metrics ----------
active_statuses = ['Moving', 'On-route', 'Idling']
active_devices = [d for d in devices if d['status'] in active_statuses]

summary = {
    'active_devices': len(active_devices),
    'idling_devices': len([d for d in devices if d['status'] == 'Idling']),
    'completed_loads': perf_df['total_deliveries'].sum(),
    'total_idling_hr': round(heat_df.sum().sum() / 60, 1),
    'avg_deliveries': round(perf_df['total_deliveries'].mean(), 1),
    'avg_speed': round(perf_df['avg_speed'].mean(), 1),
    'avg_uptime': round(perf_df['uptime_percent'].mean(), 1),
    'critical_alerts': len([e for e in events if e['event_type'] == 'Alert']),
    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('data/summary_metrics.csv', index=False)

print("Enhanced data generation complete. Files saved to data/ folder")