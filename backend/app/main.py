
from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
from app.schemas import ( SupplierCreate, SupplierUpdate, ProductCreate, ProductUpdate,
                          InventoryCreate, InventoryUpdate,OrderCreate)
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

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
@app.post("/inventory", status_code=201)
def create_inventory(inventory: InventoryCreate):

    product_check = text("""
    SELECT product_id
    FROM products
    WHERE product_id = :product_id
    """)

    with engine.connect() as connection:
        product = connection.execute(
            product_check,
            {"product_id": inventory.product_id}
        ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


    inventory_check = text("""
    SELECT inventory_id
    FROM inventory
    WHERE product_id = :product_id
    """)

    with engine.connect() as connection:
        existing_inventory = connection.execute(
            inventory_check,
            {"product_id": inventory.product_id}
        ).first()

    if existing_inventory is not None:
        raise HTTPException(
            status_code=409,
            detail="Inventory already exists for this product"
        )

    query = text("""
        INSERT INTO inventory
            (product_id, quantity_on_hand, reorder_level, warehouse_location)
        VALUES
            (:product_id, :quantity_on_hand, :reorder_level, :warehouse_location)
        RETURNING *
    """)

    try:
        with engine.begin() as connection:
            result = connection.execute(
                query,
                inventory.model_dump()
            )

            new_inventory = result.mappings().one()

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Inventory could not be created because it conflicts with existing data"
        )

    return {
        "message": "Inventory created successfully",
        "inventory": dict(new_inventory)
    }
@app.patch("/inventory/{inventory_id}")
def update_inventory(inventory_id: int, inventory: InventoryUpdate):

    updates = inventory.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    set_clause = ", ".join(
        f"{field} = :{field}" for field in updates
    )

    query = text(f"""
        UPDATE inventory
        SET {set_clause},
            last_updated = CURRENT_TIMESTAMP
        WHERE inventory_id = :inventory_id
        RETURNING *
    """)

    updates["inventory_id"] = inventory_id

    with engine.begin() as connection:
        result = connection.execute(query, updates)
        updated_inventory = result.mappings().one_or_none()

        if updated_inventory is None:
            raise HTTPException(
                status_code=404,
                detail="Inventory record not found"
            )

    return {
        "message": "Inventory updated successfully",
        "inventory": dict(updated_inventory)
    }

@app.get("/orders")
def get_orders():

    query = text("""
        SELECT
            o.order_id,
            o.customer_name,
            o.order_date,
            o.status,
            COALESCE(
                SUM(oi.quantity * oi.unit_price),
                0
            ) AS total_amount
        FROM orders o
        LEFT JOIN order_items oi
            ON o.order_id = oi.order_id
        GROUP BY
            o.order_id,
            o.customer_name,
            o.order_date,
            o.status
        ORDER BY o.order_id
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        orders = result.mappings().all()

    return {
        "total": len(orders),
        "orders": [dict(order) for order in orders]
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    query = text("""
        SELECT
            o.order_id,
            o.customer_name,
            o.order_date,
            o.status,
            p.product_name,
            oi.quantity,
            oi.unit_price,
            (oi.quantity * oi.unit_price) AS subtotal
        FROM orders o
        LEFT JOIN order_items oi
            ON o.order_id = oi.order_id
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        WHERE o.order_id = :order_id
        ORDER BY oi.order_item_id
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"order_id": order_id}
        )
        order_items = result.mappings().all()

    if not order_items:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    first_item = order_items[0]

    total_amount = sum(
        (item["subtotal"] or 0) for item in order_items
    )

    return {
        "order_id": first_item["order_id"],
        "customer_name": first_item["customer_name"],
        "order_date": first_item["order_date"],
        "status": first_item["status"],
        "items": [
            {
                "product_name": item["product_name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "subtotal": item["subtotal"]
            }
            for item in order_items
            if item["product_name"] is not None
        ],
        "total_amount": total_amount
    }
@app.post("/orders", status_code=201)
def create_order(order: OrderCreate):
    query = text("""
    INSERT INTO orders (customer_name)
    VALUES (:customer_name)
    RETURNING *
    """)
    with engine.begin() as connection:
        result = connection.execute(
            query,
            {"customer_name": order.customer_name}
        )

        new_order = result.mappings().one()
        item_query = text("""
        INSERT INTO order_items
            (order_id, product_id, quantity, unit_price)
        VALUES
            (:order_id, :product_id, :quantity, :unit_price)
        RETURNING *
       """)

        price_query = text("""
        SELECT unit_price
     FROM products
    WHERE product_id = :product_id
""")
        stock_query = text("""
    SELECT quantity_on_hand
    FROM inventory
    WHERE product_id = :product_id
    FOR UPDATE
""")
        update_stock_query = text("""
    UPDATE inventory
    SET quantity_on_hand = quantity_on_hand - :quantity,
        last_updated = CURRENT_TIMESTAMP
    WHERE product_id = :product_id
AND quantity_on_hand >= :quantity
""")
        order_item_results = []
        sorted_items = sorted(
    order.items,
    key=lambda item: item.product_id
)

        for item in sorted_items:

            price_result = connection.execute(
                price_query,
                {"product_id": item.product_id}
            )

            product = price_result.mappings().one_or_none()

            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {item.product_id} not found"
                )

            unit_price = product["unit_price"]

            stock_result = connection.execute(
                stock_query,
                {"product_id": item.product_id}
            )

            stock = stock_result.mappings().one_or_none()

            if stock is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Inventory not found for product ID {item.product_id}"
                )

            available_quantity = stock["quantity_on_hand"]

            if available_quantity < item.quantity:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Insufficient stock for product ID {item.product_id}. "
                        f"Available: {available_quantity}, "
                        f"Requested: {item.quantity}"
                    )
                )

            item_result = connection.execute(
                item_query,
                {
                    "order_id": new_order["order_id"],
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": unit_price
                }
            )


            stock_update_result = connection.execute(
                update_stock_query,
                {
                    "quantity": item.quantity,
                    "product_id": item.product_id
                }
            )

            if stock_update_result.rowcount == 0:
                raise HTTPException(
                    status_code=409,
                    detail=f"Unable to update stock for product ID {item.product_id}"
                )

            created_item = item_result.mappings().one()
            order_item_results.append(dict(created_item))

        total_amount = sum(
            (
                item["quantity"] * item["unit_price"]
                for item in order_item_results
            ),
            Decimal("0.00")
        )



    return {
        "message": "Order created successfully",
        "order": dict(new_order),
        "items": order_item_results,
        "total_amount": total_amount
    }

