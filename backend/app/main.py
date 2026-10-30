
from fastapi import FastAPI

from sqlalchemy import text
from app.database import engine

app = FastAPI(
    title="SupplyChain Sentinel API",
    description="API for supply chain operations and analytics",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Welcome to SupplyChain Sentinel!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.get("/db-health")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "success",
            "message": "PostgreSQL connection is working!"
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }
@app.get("/suppliers")
def get_suppliers():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM suppliers ORDER BY supplier_id")
        )

        suppliers = result.mappings().all()

    return {
        "total": len(suppliers),
        "suppliers": [dict(supplier) for supplier in suppliers]
    }