from pydantic import BaseModel, Field, EmailStr


class SupplierCreate(BaseModel):

    supplier_name: str = Field(
        min_length=2,
        max_length=150
    )

    contact_email: EmailStr | None = None

    city: str | None = None

    country: str = "India"

    is_active: bool = True

class SupplierUpdate(BaseModel):

    supplier_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    contact_email: EmailStr | None = None

    city: str | None = None

    country: str | None = None

    is_active: bool | None = None

class ProductCreate(BaseModel):
    product_name: str = Field(
        min_length=2,
        max_length=150
    )

    sku: str = Field(
        min_length=2,
        max_length=50
    )

    supplier_id: int

    unit_price: float = Field(
        ge=0
    )

    category: str | None = None



class ProductUpdate(BaseModel):
    product_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=50
    )

    supplier_id: int | None = None

    unit_price: float | None = Field(
        default=None,
        ge=0
    )

    category: str | None = None