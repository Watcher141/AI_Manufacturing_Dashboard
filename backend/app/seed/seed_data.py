import sys
import os
import random
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path to enable execution from any working directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.database import sync_engine, SyncSessionLocal, Base
from app.models.equipment import Equipment
from app.models.defect import DefectRecord
from app.models.inventory import InventoryItem, ForecastRecord
from app.models.alert import Alert, MaintenanceLog


# ─── Equipment Definitions ─────────────────────────────────────────
EQUIPMENT_DEFS = [
    {"name": "CNC Mill Alpha-01", "type": "CNC Machine", "location": "Building A - Floor 1", "manufacturer": "Haas Automation", "model_number": "VF-2SS"},
    {"name": "CNC Mill Alpha-02", "type": "CNC Machine", "location": "Building A - Floor 1", "manufacturer": "Haas Automation", "model_number": "VF-3"},
    {"name": "CNC Lathe Beta-01", "type": "CNC Machine", "location": "Building A - Floor 2", "manufacturer": "DMG Mori", "model_number": "NLX 2500"},
    {"name": "CNC Lathe Beta-02", "type": "CNC Machine", "location": "Building A - Floor 2", "manufacturer": "DMG Mori", "model_number": "NLX 3000"},
    {"name": "Conveyor Line C-01", "type": "Conveyor Belt", "location": "Building B - Assembly", "manufacturer": "Dorner", "model_number": "3200"},
    {"name": "Conveyor Line C-02", "type": "Conveyor Belt", "location": "Building B - Assembly", "manufacturer": "Dorner", "model_number": "2200"},
    {"name": "Conveyor Line C-03", "type": "Conveyor Belt", "location": "Building B - Packaging", "manufacturer": "Hytrol", "model_number": "E24"},
    {"name": "Robotic Arm R-01", "type": "Robotic Arm", "location": "Building A - Cell 1", "manufacturer": "FANUC", "model_number": "M-20iD/25"},
    {"name": "Robotic Arm R-02", "type": "Robotic Arm", "location": "Building A - Cell 2", "manufacturer": "FANUC", "model_number": "M-710iC/50"},
    {"name": "Robotic Arm R-03", "type": "Robotic Arm", "location": "Building B - Welding", "manufacturer": "ABB", "model_number": "IRB 6700"},
    {"name": "Robotic Arm R-04", "type": "Robotic Arm", "location": "Building B - Painting", "manufacturer": "KUKA", "model_number": "KR 16"},
    {"name": "Hydraulic Press HP-01", "type": "Hydraulic Press", "location": "Building C - Stamping", "manufacturer": "Beckwood", "model_number": "4P-200"},
    {"name": "Hydraulic Press HP-02", "type": "Hydraulic Press", "location": "Building C - Stamping", "manufacturer": "Beckwood", "model_number": "4P-300"},
    {"name": "Hydraulic Press HP-03", "type": "Hydraulic Press", "location": "Building C - Forming", "manufacturer": "Macrodyne", "model_number": "HP-500"},
    {"name": "Industrial Oven IO-01", "type": "Industrial Oven", "location": "Building D - Heat Treat", "manufacturer": "Despatch", "model_number": "LCC2-14"},
    {"name": "Industrial Oven IO-02", "type": "Industrial Oven", "location": "Building D - Heat Treat", "manufacturer": "Despatch", "model_number": "LFD2-42"},
    {"name": "Industrial Oven IO-03", "type": "Industrial Oven", "location": "Building D - Curing", "manufacturer": "Wisconsin Oven", "model_number": "SPC-8"},
    {"name": "CNC Router Gamma-01", "type": "CNC Machine", "location": "Building A - Floor 3", "manufacturer": "Mazak", "model_number": "VCN-530C"},
    {"name": "Conveyor Line C-04", "type": "Conveyor Belt", "location": "Building B - QC", "manufacturer": "Hytrol", "model_number": "ProSort"},
    {"name": "Hydraulic Press HP-04", "type": "Hydraulic Press", "location": "Building C - Forming", "manufacturer": "Macrodyne", "model_number": "HP-750"},
]

# Normal operating ranges per equipment type
SENSOR_RANGES = {
    "CNC Machine":       {"temp": (35, 65), "vib": (0.5, 3.0), "pres": (80, 120), "rpm": (800, 3500), "power": (5, 25), "humid": (30, 60), "noise": (65, 85)},
    "Conveyor Belt":     {"temp": (25, 45), "vib": (0.2, 1.5), "pres": (20, 50),  "rpm": (50, 200),   "power": (1, 8),  "humid": (30, 70), "noise": (55, 75)},
    "Robotic Arm":       {"temp": (30, 55), "vib": (0.3, 2.5), "pres": (60, 100), "rpm": (100, 500),  "power": (3, 15), "humid": (25, 55), "noise": (50, 70)},
    "Hydraulic Press":   {"temp": (40, 75), "vib": (1.0, 5.0), "pres": (500, 2000), "rpm": None,      "power": (15, 50),"humid": (25, 50), "noise": (75, 95)},
    "Industrial Oven":   {"temp": (150, 400),"vib": (0.1, 0.8),"pres": (10, 30),  "rpm": None,        "power": (20, 60),"humid": (10, 30), "noise": (40, 60)},
}

DEFECT_TYPES = ["crack", "corrosion", "misalignment", "surface_scratch", "deformation", "overheating"]
SEVERITIES = ["critical", "high", "medium", "low"]

INVENTORY_ITEMS = [
    {"name": "Ball Bearings (6205-2RS)", "sku": "BB-6205", "category": "spare_parts", "min": 20, "max": 200, "reorder": 50, "cost": 12.50, "lead": 5, "supplier": "SKF Components"},
    {"name": "Drive Belts (HTD-5M)", "sku": "DB-HTD5M", "category": "spare_parts", "min": 10, "max": 100, "reorder": 25, "cost": 28.00, "lead": 7, "supplier": "Gates Industrial"},
    {"name": "Hydraulic Oil (ISO VG 46)", "sku": "HO-VG46", "category": "consumables", "min": 50, "max": 500, "reorder": 100, "cost": 8.75, "lead": 3, "supplier": "Mobil Industrial"},
    {"name": "Cutting Fluid Concentrate", "sku": "CF-CONC", "category": "consumables", "min": 30, "max": 300, "reorder": 75, "cost": 15.00, "lead": 4, "supplier": "Castrol Metalworking"},
    {"name": "Servo Motor (750W)", "sku": "SM-750W", "category": "spare_parts", "min": 5, "max": 30, "reorder": 8, "cost": 450.00, "lead": 14, "supplier": "Siemens Automation"},
    {"name": "Linear Guide Rails", "sku": "LGR-20", "category": "spare_parts", "min": 8, "max": 50, "reorder": 15, "cost": 85.00, "lead": 10, "supplier": "THK America"},
    {"name": "Filter Elements (10μm)", "sku": "FE-10UM", "category": "consumables", "min": 25, "max": 250, "reorder": 60, "cost": 22.00, "lead": 5, "supplier": "Parker Hannifin"},
    {"name": "Coolant Hoses (1/2 inch)", "sku": "CH-HALF", "category": "spare_parts", "min": 15, "max": 150, "reorder": 40, "cost": 6.50, "lead": 3, "supplier": "Eaton Hydraulics"},
    {"name": "PLC Controller Module", "sku": "PLC-MOD", "category": "spare_parts", "min": 3, "max": 20, "reorder": 5, "cost": 1200.00, "lead": 21, "supplier": "Allen-Bradley"},
    {"name": "Welding Wire (ER70S-6)", "sku": "WW-ER70", "category": "raw_materials", "min": 40, "max": 400, "reorder": 100, "cost": 3.25, "lead": 5, "supplier": "Lincoln Electric"},
    {"name": "Steel Sheet (1.5mm CR)", "sku": "SS-15CR", "category": "raw_materials", "min": 100, "max": 1000, "reorder": 250, "cost": 18.50, "lead": 7, "supplier": "ArcelorMittal"},
    {"name": "Aluminum Bar Stock (6061)", "sku": "AB-6061", "category": "raw_materials", "min": 50, "max": 500, "reorder": 125, "cost": 24.00, "lead": 6, "supplier": "Alcoa Corporation"},
    {"name": "Safety Gloves (Box of 100)", "sku": "SG-BOX", "category": "consumables", "min": 10, "max": 100, "reorder": 25, "cost": 35.00, "lead": 3, "supplier": "3M Safety"},
    {"name": "Grinding Wheels (Type 27)", "sku": "GW-T27", "category": "consumables", "min": 20, "max": 200, "reorder": 50, "cost": 7.50, "lead": 4, "supplier": "Norton Abrasives"},
    {"name": "Pneumatic Cylinders", "sku": "PC-40MM", "category": "spare_parts", "min": 5, "max": 40, "reorder": 10, "cost": 95.00, "lead": 8, "supplier": "SMC Corporation"},
    {"name": "Thermal Paste (Tube)", "sku": "TP-TUBE", "category": "consumables", "min": 15, "max": 100, "reorder": 30, "cost": 12.00, "lead": 3, "supplier": "Henkel Adhesives"},
    {"name": "Encoder Cables (5m)", "sku": "EC-5M", "category": "spare_parts", "min": 10, "max": 80, "reorder": 20, "cost": 42.00, "lead": 7, "supplier": "Beckhoff Automation"},
    {"name": "Rubber Gaskets (Set)", "sku": "RG-SET", "category": "spare_parts", "min": 20, "max": 200, "reorder": 50, "cost": 5.50, "lead": 4, "supplier": "Parker Hannifin"},
    {"name": "Stainless Steel Rod (304)", "sku": "SR-304", "category": "raw_materials", "min": 30, "max": 300, "reorder": 75, "cost": 32.00, "lead": 8, "supplier": "Outokumpu"},
    {"name": "Nylon Spacers (Bag of 500)", "sku": "NS-BAG", "category": "consumables", "min": 5, "max": 50, "reorder": 12, "cost": 18.00, "lead": 3, "supplier": "McMaster-Carr"},
    {"name": "Proximity Sensors", "sku": "PS-IND", "category": "spare_parts", "min": 8, "max": 60, "reorder": 15, "cost": 55.00, "lead": 6, "supplier": "Sick Sensors"},
    {"name": "Lubrication Grease (Cartridge)", "sku": "LG-CART", "category": "consumables", "min": 25, "max": 250, "reorder": 60, "cost": 9.00, "lead": 3, "supplier": "Shell Lubricants"},
    {"name": "Conveyor Rollers", "sku": "CR-ROLL", "category": "spare_parts", "min": 10, "max": 100, "reorder": 25, "cost": 38.00, "lead": 10, "supplier": "Hytrol Conveyors"},
    {"name": "Copper Wire Spool (1.5mm)", "sku": "CW-15MM", "category": "raw_materials", "min": 20, "max": 200, "reorder": 50, "cost": 45.00, "lead": 5, "supplier": "Southwire Company"},
    {"name": "O-Ring Kit (Metric)", "sku": "OR-KIT", "category": "spare_parts", "min": 10, "max": 80, "reorder": 20, "cost": 28.00, "lead": 4, "supplier": "Trelleborg Sealing"},
    {"name": "Abrasive Sandpaper Sheets", "sku": "SP-SHEET", "category": "consumables", "min": 50, "max": 500, "reorder": 125, "cost": 1.50, "lead": 3, "supplier": "3M Abrasives"},
    {"name": "Spindle Motor (2.2kW)", "sku": "SM-22KW", "category": "spare_parts", "min": 2, "max": 10, "reorder": 3, "cost": 850.00, "lead": 21, "supplier": "Siemens Automation"},
    {"name": "Titanium Sheet (Grade 5)", "sku": "TS-GR5", "category": "raw_materials", "min": 10, "max": 100, "reorder": 25, "cost": 120.00, "lead": 14, "supplier": "TIMET"},
    {"name": "Anti-Seize Compound", "sku": "AS-COMP", "category": "consumables", "min": 10, "max": 100, "reorder": 25, "cost": 14.00, "lead": 3, "supplier": "Loctite"},
    {"name": "Emergency Stop Buttons", "sku": "ES-BTN", "category": "spare_parts", "min": 5, "max": 30, "reorder": 8, "cost": 25.00, "lead": 5, "supplier": "Schneider Electric"},
]

TECHNICIANS = ["James Morrison", "Sarah Chen", "Mike Patel", "Linda Nguyen", "Carlos Rivera", "Emma Wilson"]


def generate_sensor_readings(equipment: Equipment, days: int = 90):
    """Generate realistic sensor readings with anomaly injection."""
    readings = []
    ranges = SENSOR_RANGES[equipment.type]
    now = datetime.utcnow()
    start = now - timedelta(days=days)

    # Decide anomaly windows (2-3 degradation periods per equipment)
    num_anomalies = random.randint(1, 3)
    anomaly_windows = []
    for _ in range(num_anomalies):
        if days > 20:
            anomaly_start = random.randint(10, days - 10)
        else:
            anomaly_start = random.randint(0, max(0, days - 1))
        anomaly_duration = random.randint(12, 72)  # hours
        anomaly_windows.append((anomaly_start * 24, anomaly_start * 24 + anomaly_duration))

    interval_minutes = 15
    total_readings = int(days * 24 * 60 / interval_minutes)

    for i in range(total_readings):
        ts = start + timedelta(minutes=i * interval_minutes)
        hour_index = i * interval_minutes / 60

        # Check if in anomaly window
        in_anomaly = any(s <= hour_index <= e for s, e in anomaly_windows)
        anomaly_factor = 1.0

        if in_anomaly:
            # Progressive degradation
            for s, e in anomaly_windows:
                if s <= hour_index <= e:
                    progress = (hour_index - s) / (e - s)
                    anomaly_factor = 1.0 + progress * random.uniform(0.3, 0.8)

        # Add daily cycle (slight temperature variation)
        daily_cycle = np.sin(2 * np.pi * (hour_index % 24) / 24) * 0.05

        temp_range = ranges["temp"]
        vib_range = ranges["vib"]
        pres_range = ranges["pres"]
        power_range = ranges["power"]

        reading = SensorReading(
            equipment_id=equipment.id,
            timestamp=ts,
            temperature=round(random.uniform(*temp_range) * anomaly_factor * (1 + daily_cycle) + random.gauss(0, 1), 2),
            vibration=round(random.uniform(*vib_range) * anomaly_factor + random.gauss(0, 0.1), 3),
            pressure=round(random.uniform(*pres_range) * (1 + (anomaly_factor - 1) * 0.5) + random.gauss(0, 2), 1),
            rpm=round(random.uniform(*ranges["rpm"]) + random.gauss(0, 10), 0) if ranges["rpm"] else None,
            power_consumption=round(random.uniform(*power_range) * anomaly_factor + random.gauss(0, 0.5), 2),
            humidity=round(random.uniform(*ranges["humid"]) + random.gauss(0, 2), 1) if ranges["humid"] else None,
            noise_level=round(random.uniform(*ranges["noise"]) * (anomaly_factor ** 0.5) + random.gauss(0, 1), 1) if ranges["noise"] else None,
        )
        readings.append(reading)

    return readings


def generate_defects(equipment_list, days=90):
    """Generate realistic defect records."""
    defects = []
    now = datetime.utcnow()

    for equip in equipment_list:
        num_defects = random.randint(3, 12)
        for _ in range(num_defects):
            days_ago = random.randint(0, days)
            ts = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            defect_type = random.choice(DEFECT_TYPES)
            severity = random.choices(SEVERITIES, weights=[10, 20, 40, 30])[0]
            confidence = round(random.uniform(0.65, 0.99), 3)
            is_resolved = days_ago > 5 and random.random() > 0.3

            descriptions = {
                "crack": f"Hairline crack detected on {equip.type.lower()} component. Vibration pattern indicates stress fracture.",
                "corrosion": f"Surface corrosion identified on {equip.type.lower()} housing. Humidity exposure likely cause.",
                "misalignment": f"Shaft misalignment detected. Angular offset exceeding tolerance by {round(random.uniform(0.5, 3.0), 1)}°.",
                "surface_scratch": f"Surface scratch pattern on workpiece output. Tool wear indicator at {round(random.uniform(60, 95), 0)}%.",
                "deformation": f"Structural deformation detected under load. Pressure deviation: {round(random.uniform(5, 20), 1)}%.",
                "overheating": f"Thermal anomaly detected. Temperature exceeded safe range by {round(random.uniform(5, 30), 1)}°C.",
            }

            defect = DefectRecord(
                equipment_id=equip.id,
                timestamp=ts,
                defect_type=defect_type,
                severity=severity,
                confidence_score=confidence,
                description=descriptions[defect_type],
                is_resolved=is_resolved,
                resolved_at=ts + timedelta(hours=random.randint(2, 48)) if is_resolved else None,
                detected_by=random.choices(["ml_model", "manual"], weights=[80, 20])[0],
            )
            defects.append(defect)

    return defects


def generate_alerts(equipment_list, defects, days=90):
    """Generate alerts from equipment status and defects."""
    alerts = []
    now = datetime.utcnow()

    # Maintenance alerts
    for equip in equipment_list:
        if random.random() > 0.4:
            days_ago = random.randint(0, 14)
            severity = random.choice(["critical", "warning", "info"])
            titles = {
                "critical": f"CRITICAL: {equip.name} failure probability exceeds 80%",
                "warning": f"WARNING: {equip.name} showing degradation patterns",
                "info": f"Scheduled maintenance due for {equip.name}",
            }
            messages = {
                "critical": f"Predictive model indicates imminent failure risk for {equip.name}. Vibration and temperature readings are outside normal parameters. Immediate inspection recommended.",
                "warning": f"Sensor readings for {equip.name} show a gradual increase in vibration ({round(random.uniform(15, 40), 0)}% above baseline). Monitor closely and schedule preventive maintenance within 48 hours.",
                "info": f"Routine maintenance window approaching for {equip.name}. Last service was {random.randint(20, 60)} days ago. No anomalies detected.",
            }
            alert = Alert(
                type="maintenance",
                severity=severity,
                title=titles[severity],
                message=messages[severity],
                equipment_id=equip.id,
                is_read=days_ago > 3,
                created_at=now - timedelta(days=days_ago, hours=random.randint(0, 23)),
            )
            alerts.append(alert)

    # Defect alerts
    for defect in random.sample(defects, min(len(defects), 20)):
        alert = Alert(
            type="defect",
            severity=defect.severity if defect.severity in ["critical", "warning"] else "warning",
            title=f"Defect detected: {defect.defect_type.replace('_', ' ').title()} on Equipment #{defect.equipment_id}",
            message=defect.description or f"A {defect.defect_type} defect was detected with {round(defect.confidence_score * 100, 1)}% confidence.",
            equipment_id=defect.equipment_id,
            is_read=random.random() > 0.5,
            created_at=defect.timestamp,
        )
        alerts.append(alert)

    # Inventory alerts
    for _ in range(random.randint(5, 10)):
        item_name = random.choice(INVENTORY_ITEMS)["name"]
        alert = Alert(
            type="inventory",
            severity=random.choice(["warning", "info"]),
            title=f"Low stock alert: {item_name}",
            message=f"{item_name} stock level has fallen below the reorder point. Current stock: {random.randint(5, 20)} units. Recommended order quantity: {random.randint(50, 200)} units.",
            equipment_id=None,
            is_read=random.random() > 0.5,
            created_at=now - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23)),
        )
        alerts.append(alert)

    return alerts


def generate_maintenance_logs(equipment_list, days=90):
    """Generate maintenance history."""
    logs = []
    now = datetime.utcnow()

    for equip in equipment_list:
        num_logs = random.randint(1, 4)
        for _ in range(num_logs):
            days_ago = random.randint(5, days)
            performed = now - timedelta(days=days_ago)
            mtype = random.choice(["preventive", "corrective", "predictive"])

            descriptions = {
                "preventive": f"Routine preventive maintenance. Checked all sensors, replaced filters, lubricated moving parts.",
                "corrective": f"Corrective maintenance due to {random.choice(DEFECT_TYPES).replace('_', ' ')} issue. Replaced damaged component.",
                "predictive": f"Predictive maintenance based on ML model alert. Addressed early-stage degradation in sensor readings.",
            }

            log = MaintenanceLog(
                equipment_id=equip.id,
                maintenance_type=mtype,
                performed_at=performed,
                completed_at=performed + timedelta(hours=random.randint(1, 8)),
                technician=random.choice(TECHNICIANS),
                description=descriptions[mtype],
                parts_replaced=random.choice(["Bearings", "Drive belt", "Filter", "Seals", "Motor brush", "Coolant lines", None]),
                cost=round(random.uniform(150, 3500), 2),
                notes=random.choice(["No further issues.", "Recommend follow-up in 2 weeks.", "Equipment returned to full operation.", None]),
            )
            logs.append(log)

    return logs


def generate_inventory_data():
    """Generate inventory items with current stock."""
    items = []
    for item_def in INVENTORY_ITEMS:
        stock = random.randint(item_def["min"] - 5, item_def["max"])
        stock = max(0, stock)

        item = InventoryItem(
            name=item_def["name"],
            sku=item_def["sku"],
            category=item_def["category"],
            current_stock=stock,
            min_stock=item_def["min"],
            max_stock=item_def["max"],
            reorder_point=item_def["reorder"],
            unit_cost=item_def["cost"],
            lead_time_days=item_def["lead"],
            supplier=item_def["supplier"],
            location=f"Warehouse {random.choice(['A', 'B', 'C'])}-{random.choice(['Shelf', 'Bin', 'Rack'])} {random.randint(1, 20)}",
            last_restocked=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
        )
        items.append(item)

    return items


def generate_forecast_records(items, days=30):
    """Generate demand forecast records for inventory items."""
    forecasts = []
    now = datetime.utcnow()

    for item in items:
        # Base daily demand varies by category
        base_demand = {"spare_parts": 3, "consumables": 8, "raw_materials": 12}.get(item.category, 5)
        base_demand *= random.uniform(0.5, 2.0)

        for d in range(days):
            forecast_date = now + timedelta(days=d)
            # Add weekly seasonality
            day_factor = 1.0 + 0.2 * np.sin(2 * np.pi * d / 7)
            predicted = max(0, round(base_demand * day_factor + random.gauss(0, base_demand * 0.2), 1))
            margin = base_demand * 0.3

            forecast = ForecastRecord(
                item_id=item.id,
                forecast_date=forecast_date,
                predicted_demand=predicted,
                confidence_lower=max(0, round(predicted - margin, 1)),
                confidence_upper=round(predicted + margin, 1),
                actual_demand=round(predicted + random.gauss(0, margin * 0.5), 1) if d < 7 else None,
            )
            forecasts.append(forecast)

    return forecasts


# Need to import SensorReading after defining functions that use it
from app.models.equipment import SensorReading


def seed_database():
    """Main function to seed the entire database with realistic data."""
    print("🏭 Starting database seeding...")

    # Create all tables
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    print("  ✓ Tables created")

    session = SyncSessionLocal()

    try:
        # 1. Create equipment
        now = datetime.utcnow()
        equipment_list = []
        for eq_def in EQUIPMENT_DEFS:
            equip = Equipment(
                name=eq_def["name"],
                type=eq_def["type"],
                location=eq_def["location"],
                manufacturer=eq_def["manufacturer"],
                model_number=eq_def["model_number"],
                status=random.choices(
                    ["operational", "warning", "critical", "maintenance", "offline"],
                    weights=[60, 20, 8, 8, 4]
                )[0],
                health_score=round(random.uniform(45, 100), 1),
                install_date=now - timedelta(days=random.randint(180, 1800)),
                last_maintenance=now - timedelta(days=random.randint(5, 60)),
            )
            session.add(equip)
            equipment_list.append(equip)

        session.flush()
        print(f"  ✓ {len(equipment_list)} equipment items created")

        # 2. Generate sensor readings (limited for speed — last 7 days at 15-min intervals)
        total_readings = 0
        for equip in equipment_list:
            readings = generate_sensor_readings(equip, days=7)
            session.bulk_save_objects(readings)
            total_readings += len(readings)
        session.flush()
        print(f"  ✓ {total_readings:,} sensor readings generated")

        # 3. Generate defects
        defects = generate_defects(equipment_list, days=90)
        session.bulk_save_objects(defects)
        session.flush()
        print(f"  ✓ {len(defects)} defect records created")

        # 4. Generate alerts
        alerts = generate_alerts(equipment_list, defects)
        session.bulk_save_objects(alerts)
        session.flush()
        print(f"  ✓ {len(alerts)} alerts created")

        # 5. Generate maintenance logs
        logs = generate_maintenance_logs(equipment_list)
        session.bulk_save_objects(logs)
        session.flush()
        print(f"  ✓ {len(logs)} maintenance logs created")

        # 6. Generate inventory items
        inv_items = generate_inventory_data()
        for item in inv_items:
            session.add(item)
        session.flush()
        print(f"  ✓ {len(inv_items)} inventory items created")

        # 7. Generate forecast records
        forecasts = generate_forecast_records(inv_items)
        session.bulk_save_objects(forecasts)
        session.flush()
        print(f"  ✓ {len(forecasts)} forecast records created")

        session.commit()
        print("\n🎉 Database seeding complete!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Seeding failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
