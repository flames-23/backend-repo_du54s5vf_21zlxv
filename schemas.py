"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class Drink(BaseModel):
    """
    Drinks collection schema
    Collection name: "drink"
    """
    name: str = Field(..., description="Drink name")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in local currency")
    image: Optional[str] = Field(None, description="Image URL")
    category: Optional[str] = Field(None, description="Category like coffee/tea/fruit")
    in_stock: bool = Field(True, description="Availability flag")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Drink document _id as string")
    name: str = Field(..., description="Drink name at time of purchase")
    price: float = Field(..., ge=0, description="Unit price at time of purchase")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    subtotal: float = Field(..., ge=0, description="Calculated price * quantity")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="Customer phone number")
    items: List[OrderItem] = Field(..., description="Line items")
    total: float = Field(..., ge=0, description="Total amount")
    status: str = Field("pending", description="Order status: pending/paid/cancelled")
    payment_method: str = Field("ewallet", description="Payment method used")
    payment_provider: Optional[str] = Field(None, description="eWallet provider (OVO, GoPay, DANA)")
    payment_token: Optional[str] = Field(None, description="Payment token/reference")
    payment_qr: Optional[str] = Field(None, description="Simulated QR or deeplink content")
