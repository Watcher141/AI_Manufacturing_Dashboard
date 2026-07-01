from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import pandas as pd
import io
import datetime

from app.database import get_db
from app.models.equipment import Equipment, SensorReading

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.post("/clear-data")
async def clear_data(db: AsyncSession = Depends(get_db)):
    """Wipe synthetic sensor readings and related data to prepare for real data."""
    try:
        # We will delete sensor readings, defects, alerts, but keep basic equipment 
        await db.execute(text("TRUNCATE TABLE sensor_readings CASCADE"))
        await db.execute(text("TRUNCATE TABLE defects CASCADE"))
        await db.execute(text("TRUNCATE TABLE alerts CASCADE"))
        await db.commit()
        return {"status": "success", "message": "Synthetic telemetry data wiped successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-data")
async def upload_data(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Accepts a CSV of sensor readings, parses it, and inserts it into the database."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate columns
        required_columns = ['equipment_id', 'timestamp', 'temperature', 'vibration', 'pressure', 'power_consumption']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}. Please ensure your CSV has the template format.")
        
        # Insert data in chunks
        records = []
        for index, row in df.iterrows():
            reading = SensorReading(
                equipment_id=int(row['equipment_id']),
                timestamp=pd.to_datetime(row['timestamp']),
                temperature=float(row['temperature']),
                vibration=float(row['vibration']),
                pressure=float(row['pressure']),
                power_consumption=float(row['power_consumption']),
                rpm=float(row['rpm']) if 'rpm' in row and not pd.isna(row['rpm']) else None,
                humidity=float(row['humidity']) if 'humidity' in row and not pd.isna(row['humidity']) else None,
                noise_level=float(row['noise_level']) if 'noise_level' in row and not pd.isna(row['noise_level']) else None
            )
            db.add(reading)
            
            # Commit every 1000 records to prevent memory bloat
            if index > 0 and index % 1000 == 0:
                await db.commit()
        
        await db.commit()
        
        return {"status": "success", "message": f"Successfully ingested {len(df)} records.", "count": len(df)}
        
    except pd.errors.EmptyDataError:
         raise HTTPException(status_code=400, detail="The uploaded CSV is empty.")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain-models")
async def retrain_models(background_tasks: BackgroundTasks):
    """Triggers ML model retraining in the background."""
    def run_training():
        try:
            from app.ml.train_models import train_all
            train_all()
        except Exception as e:
            print(f"Error during retraining: {e}")
            
    background_tasks.add_task(run_training)
    return {"status": "success", "message": "ML models are retraining in the background. This may take a few minutes."}
