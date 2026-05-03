from database import redis
from main import Order

key = "refund_order"
group = "payment-group"

try:
    redis.xgroup_create(key, group, mkstream=True)
except Exception:
    print("Group already exists!")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, count=1, block=5000)

        if results:
            for result in results:
                message_data = result[1][0][1]
                try:
                    order = Order.get(message_data["pk"])
                    order.status = "refunded"
                    order.save()
                    print(f"Order {order.pk} successfully refunded.")
                except Exception as e:
                    print(f"Could not find order to refund: {e}")

    except Exception as e:
        print(f"Consumer error: {e}")
