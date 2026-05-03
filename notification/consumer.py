from database import redis

CONSUMER_NAME = "notification-consumer"

# Svaki stream ima svoju consumer grupu kako bi notification servis
# primao SVE poruke nezavisno od inventory i payment grupa.
STREAMS = {
    "order_completed": "notification-order-group",
    "refund_order": "notification-refund-group",
}

for stream, group in STREAMS.items():
    try:
        redis.xgroup_create(stream, group, mkstream=True)
        print(f"Consumer group '{group}' created for stream '{stream}'.")
    except Exception:
        print(f"Consumer group '{group}' already exists for stream '{stream}'.")


def handle_order_completed(data: dict):
    order_id = data.get("pk", "N/A")
    product_id = data.get("product_id", "N/A")
    total = data.get("total", "N/A")
    print(
        f"[NOTIFICATION] Porudžbina {order_id} je uspešno kreirana i plaćena. "
        f"Proizvod: {product_id}, Ukupno: {total} RSD."
    )


def handle_refund_order(data: dict):
    order_id = data.get("pk", "N/A")
    product_id = data.get("product_id", "N/A")
    print(
        f"[NOTIFICATION] Porudžbina {order_id} je refundirana. "
        f"Proizvod {product_id} biće vraćen na stanje."
    )


HANDLERS = {
    "order_completed": handle_order_completed,
    "refund_order": handle_refund_order,
}

print("Notification consumer started. Listening on streams: order_completed, refund_order...")

while True:
    try:
        for stream, group in STREAMS.items():
            results = redis.xreadgroup(
                group,
                CONSUMER_NAME,
                {stream: ">"},
                count=10,
                block=2000,
            )
            if results:
                for result in results:
                    stream_name = result[0]
                    messages = result[1]
                    for msg_id, data in messages:
                        try:
                            HANDLERS[stream_name](data)
                            # Potvrđujemo obradu poruke (ACK)
                            redis.xack(stream_name, group, msg_id)
                        except Exception as e:
                            print(f"[NOTIFICATION] Error processing message {msg_id}: {e}")

    except Exception as e:
        print(f"[NOTIFICATION] Consumer loop error: {e}")
