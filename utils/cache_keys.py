def cart_key(user_id):
    return f"cart_user_{user_id}"


def orders_list_key(user_id):
    return f"orders_list_user_{user_id}"


def order_detail_key(order_id):
    return f"order_{order_id}"


def service_key(service_id):
    return f"service_{service_id}"
