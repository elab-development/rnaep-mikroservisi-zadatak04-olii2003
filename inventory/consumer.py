from database import redis
from main import Product

key = "order_completed"
group = "inventory-group"

try:
    redis.xgroup_create(key, group, mkstream=True)
except Exception:
    print("Group already exists!")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, count=1, block=5000)

        if results:
            for result in results:
                obj = result[1][0][1]
                try:
                    product = Product.get(obj["product_id"])
                    product.quantity -= int(obj["quantity"])
                    product.save()
                    print(f"Stock updated for {product.name}")
                except Exception as e:
                    redis.xadd("refund_order", obj, "*")
                    print(f"Error updating stock, refund triggered: {e}")

    except Exception as e:
        print(f"Consumer error: {e}")
