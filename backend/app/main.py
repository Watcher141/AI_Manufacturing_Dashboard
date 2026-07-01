"""Main entry point for the FastAPI application."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import (
    dashboard,
    equipment,
    maintenance,
    defects,
    inventory,
    alerts,
    ai_assistant,
    analytics,
    settings as settings_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade AI Manufacturing Dashboard API",
)

# CORS middleware config
import re

origins = settings.cors_origins_list
literal_origins = [o for o in origins if "*" not in o]
wildcard_origins = [o for o in origins if "*" in o]

allow_origin_regex = None
if wildcard_origins:
    patterns = []
    for wo in wildcard_origins:
        # Convert wildcard like https://*.vercel.app to a valid regex
        pattern = re.escape(wo).replace(r"\*", r"[\w-]+")
        patterns.append(f"^{pattern}$")
    allow_origin_regex = "|".join(patterns)

app.add_middleware(
    CORSMiddleware,
    allow_origins=literal_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(equipment.router)
app.include_router(maintenance.router)
app.include_router(defects.router)
app.include_router(inventory.router)
app.include_router(alerts.router)
app.include_router(ai_assistant.router)
app.include_router(analytics.router)
app.include_router(settings_router.router)


@app.on_event("startup")
async def on_startup():
    """Startup event: initialize db, auto-seed if empty, and train ML models."""
    print("🚀 App starting up...")
    await create_tables()
    print("  ✓ Database tables verified")

    # Auto-seed if database is empty (first deployment)
    try:
        from app.database import AsyncSessionLocal
        from app.models.equipment import Equipment
        from sqlalchemy import select, func

        async with AsyncSessionLocal() as session:
            count = await session.execute(select(func.count(Equipment.id)))
            equipment_count = count.scalar_one()

        if equipment_count == 0:
            print("  → Empty database detected, running auto-seed...")
            import threading
            def _seed_and_train():
                try:
                    from app.seed.seed_data import seed_database
                    seed_database()
                    print("  ✓ Database seeded successfully")
                except Exception as e:
                    print(f"  ⚠ Seed failed: {e}")

                try:
                    from app.ml.train_models import train_all
                    train_all()
                    print("  ✓ ML models trained successfully")
                except Exception as e:
                    print(f"  ⚠ ML training failed: {e}")

            thread = threading.Thread(target=_seed_and_train, daemon=True)
            thread.start()
            thread.join(timeout=120)  # Wait up to 2 min
        else:
            print(f"  ✓ Database has {equipment_count} equipment records")
            # Load existing ML models
            from app.ml.predictive_maintenance import PredictiveMaintenanceModel
            from app.ml.defect_detection import DefectDetectionModel
            from app.ml.inventory_forecasting import InventoryForecastModel
            PredictiveMaintenanceModel().load_models()
            DefectDetectionModel().load_models()
            InventoryForecastModel().load_models()
            print("  ✓ ML models loaded")
    except Exception as e:
        print(f"  ⚠ Startup check failed: {e}")


@app.get("/")
async def root():
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
