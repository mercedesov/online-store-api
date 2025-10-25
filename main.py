
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Dict
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI(title="Online Store API")
security = HTTPBasic()

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float

class CartItem(BaseModel):
    product_id: int

class Order(BaseModel):
    email: EmailStr
    items: List[int]

products: Dict[int, Product] = {}
carts: Dict[str, List[int]] = {}

users = {
    "manager": {"password": "manager123", "role": "manager"},
    "admin": {"password": "admin123", "role": "admin"},
}

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = users.get(credentials.username)
    if not user or not secrets.compare_digest(user["password"], credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"username": credentials.username, "role": user["role"]}

def require_role(required_roles: List[str]):
    def role_checker(user = Depends(get_current_user)):
        if user["role"] not in required_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user
    return role_checker

# Client endpoints
@app.get("/products", response_model=List[Product])
def get_products():
    return list(products.values())

@app.post("/cart/{user_email}", response_model=List[int])
def add_to_cart(user_email: str, item: CartItem):
    if user_email not in carts:
        carts[user_email] = []
    carts[user_email].append(item.product_id)
    return carts[user_email]

@app.delete("/cart/{user_email}", response_model=List[int])
def remove_from_cart(user_email: str, item: CartItem):
    if user_email not in carts or item.product_id not in carts[user_email]:
        raise HTTPException(status_code=404, detail="Item not in cart")
    carts[user_email].remove(item.product_id)
    return carts[user_email]

@app.post("/order")
def create_order(order: Order):
    if order.email not in carts or not carts[order.email]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    carts[order.email] = []
    return {"message": f"Order placed for {order.email}"}

# Admin endpoints
@app.put("/product/{product_id}", dependencies=[Depends(require_role(["manager","admin"]))])
def update_product(product_id: int, product: Product):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    products[product_id].name = product.name
    products[product_id].description = product.description
    products[product_id].price = product.price
    return products[product_id]

@app.post("/product", dependencies=[Depends(require_role(["admin"]))])
def create_product(product: Product):
    if product.id in products:
        raise HTTPException(status_code=400, detail="Product ID exists")
    products[product.id] = product
    return product
