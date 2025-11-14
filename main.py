import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="Kedai Kita API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Schemas -----
from schemas import Drink, Order, OrderItem

# Utility to convert ObjectId to string

def serialize_doc(doc):
    if not doc:
        return doc
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

@app.get("/")
def read_root():
    return {"message": "Kedai Kita backend is running"}

# Public endpoints to list drinks
@app.get("/api/drinks")
def list_drinks():
    items = get_documents("drink")
    return [serialize_doc(x) for x in items]

class DrinkCreate(Drink):
    pass

@app.post("/api/drinks")
def create_drink(drink: DrinkCreate):
    drink_id = create_document("drink", drink)
    return {"id": drink_id}

# Create order and simulate e-wallet payment
class CheckoutRequest(BaseModel):
    customer_name: str
    phone: str
    items: List[OrderItem]
    provider: str  # e.g., "OVO", "GoPay", "DANA"

class CheckoutResponse(BaseModel):
    order_id: str
    total: float
    provider: str
    payment_token: str
    payment_qr: str
    deeplink: Optional[str] = None

@app.post("/api/checkout", response_model=CheckoutResponse)
def checkout(req: CheckoutRequest):
    # Calculate total and augment items
    total = 0.0
    for it in req.items:
        it.subtotal = it.price * it.quantity
        total += it.subtotal

    # Simulate payment gateway by generating token/qr
    import uuid
    token = str(uuid.uuid4())
    qr_content = f"kedai-kita://pay?provider={req.provider}&token={token}&amount={total}"
    deeplink = f"kedai-kita://open-payment/{token}"

    order = Order(
        customer_name=req.customer_name,
        phone=req.phone,
        items=req.items,
        total=total,
        status="pending",
        payment_method="ewallet",
        payment_provider=req.provider,
        payment_token=token,
        payment_qr=qr_content,
    )
    order_id = create_document("order", order)

    return CheckoutResponse(
        order_id=order_id,
        total=total,
        provider=req.provider,
        payment_token=token,
        payment_qr=qr_content,
        deeplink=deeplink,
    )

@app.get("/api/orders")
def list_orders():
    items = get_documents("order")
    return [serialize_doc(x) for x in items]

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
