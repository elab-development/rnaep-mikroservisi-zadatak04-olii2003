from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import HashModel, NotFoundError
from database import redis
from typing import List

app = FastAPI(title="Inventory Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Product(HashModel, index=True):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


def format_product(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }


@app.get("/products", response_model=List[dict])
async def all_products():
    return [format_product(pk) for pk in Product.all_pks()]


@app.post("/products")
async def create(product: Product):
    return product.save()


@app.get("/products/{pk}")
async def get_one(pk: str):
    try:
        return Product.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{pk}")
async def delete(pk: str):
    return Product.delete(pk)
