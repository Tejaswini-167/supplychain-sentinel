
from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
from app.schemas import SupplierCreate, SupplierUpdate, ProductCreate, ProductUpdate
from fastapi import HTTPException

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
@app.post("/suppliers")
def create_supplier(supplier: SupplierCreate):

    query = text("""
        INSERT INTO suppliers
            (supplier_name, contact_email, city, country, is_active)
        VALUES
            (:supplier_name, :contact_email, :city, :country, :is_active)
        RETURNING *
    """)

    with engine.begin() as connection:

        result = connection.execute(
            query,
            supplier.model_dump()
        )

        new_supplier = result.mappings().one()

    return {
        "message": "Supplier created successfully",
        "supplier": dict(new_supplier)
    }
@app.put("/suppliers/{supplier_id}")
def update_supplier(supplier_id: int, supplier: SupplierCreate):

    query = text("""
        UPDATE suppliers
        SET
            supplier_name = :supplier_name,
            contact_email = :contact_email,
            city = :city,
            country = :country,
            is_active = :is_active
        WHERE supplier_id = :supplier_id
        RETURNING *
    """)

    supplier_data = supplier.model_dump()
    supplier_data["supplier_id"] = supplier_id

    with engine.begin() as connection:
        result = connection.execute(query, supplier_data)

        updated_supplier = result.mappings().one_or_none()

        if updated_supplier is None:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

    return {
        "message": "Supplier updated successfully",
        "supplier": dict(updated_supplier)
    }
@app.patch("/suppliers/{supplier_id}")
def patch_supplier(supplier_id: int, supplier: SupplierUpdate):

    updates = supplier.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    set_clause = ", ".join(
        f"{field} = :{field}" for field in updates
    )

    query = text(f"""
        UPDATE suppliers
        SET {set_clause}
        WHERE supplier_id = :supplier_id
        RETURNING *
    """)

    updates["supplier_id"] = supplier_id

    with engine.begin() as connection:
        result = connection.execute(query, updates)

        updated_supplier = result.mappings().one_or_none()

        if updated_supplier is None:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

    return {
        "message": "Supplier partially updated",
        "supplier": dict(updated_supplier)
    }

@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int):

    query = text("""
        DELETE FROM suppliers
        WHERE supplier_id = :supplier_id
        RETURNING supplier_id
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {"supplier_id": supplier_id}
        )

        deleted_supplier = result.fetchone()

        if deleted_supplier is None:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

    return {
        "message": "Supplier deleted successfully",
        "supplier_id": supplier_id
    }

@app.get("/products")
def get_products():
    query = text("""
        SELECT
            p.product_id,
            p.product_name,
            p.sku,
            p.unit_price,
            p.category,
            s.supplier_name
        FROM products p
        JOIN suppliers s
            ON p.supplier_id = s.supplier_id
        ORDER BY p.product_id
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        products = result.mappings().all()

    return {
        "total": len(products),
        "products": [dict(product) for product in products]
    }

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):

    query = text("""
        INSERT INTO products
            (product_name, sku, supplier_id, unit_price, category)
        VALUES
            (:product_name, :sku, :supplier_id, :unit_price, :category)
        RETURNING *
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            product.model_dump()
        )

        new_product = result.mappings().one()

    return {
        "message": "Product created successfully",
        "product": dict(new_product)
    }

@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductCreate):

    query = text("""
        UPDATE products
        SET
            product_name = :product_name,
            sku = :sku,
            supplier_id = :supplier_id,
            unit_price = :unit_price,
            category = :category
        WHERE product_id = :product_id
        RETURNING *
    """)

    product_data = product.model_dump()
    product_data["product_id"] = product_id

    with engine.begin() as connection:
        result = connection.execute(query, product_data)
        updated_product = result.mappings().one_or_none()

        if updated_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

    return {
        "message": "Product updated successfully",
        "product": dict(updated_product)
    }
@app.patch("/products/{product_id}")
def patch_product(product_id: int, product: ProductUpdate):

    updates = product.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    set_clause = ", ".join(
        f"{field} = :{field}" for field in updates
    )

    query = text(f"""
        UPDATE products
        SET {set_clause}
        WHERE product_id = :product_id
        RETURNING *
    """)

    updates["product_id"] = product_id

    with engine.begin() as connection:
        result = connection.execute(query, updates)
        updated_product = result.mappings().one_or_none()

        if updated_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

    return {
        "message": "Product partially updated successfully",
        "product": dict(updated_product)
    }
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    query = text("""
        DELETE FROM products
        WHERE product_id = :product_id
        RETURNING product_id
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {"product_id": product_id}
        )

        deleted_product = result.mappings().one_or_none()

        if deleted_product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

    return {
        "message": "Product deleted successfully",
        "product_id": deleted_product["product_id"]
    }

@app.get("/inventory")
def get_inventory():

    query = text("""
        SELECT
            i.inventory_id,
            p.product_name,
            p.sku,
            i.quantity_on_hand,
            i.reorder_level,
            i.warehouse_location
        FROM inventory i
        JOIN products p
            ON i.product_id = p.product_id
        ORDER BY i.inventory_id
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        inventory = result.mappings().all()

    return {
        "total": len(inventory),
        "inventory": [dict(item) for item in inventory]
    }

@app.get("/inventory/low-stock")
def get_low_stock():

    query = text("""
        SELECT
            i.inventory_id,
            p.product_name,
            p.sku,
            i.quantity_on_hand,
            i.reorder_level,
            i.warehouse_location
        FROM inventory i
        JOIN products p
            ON i.product_id = p.product_id
        WHERE i.quantity_on_hand <= i.reorder_level
        ORDER BY i.quantity_on_hand ASC
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        low_stock_items = result.mappings().all()

    return {
        "total_low_stock": len(low_stock_items),
        "low_stock_items": [dict(item) for item in low_stock_items]
    }