import stripe


def create_stripe_product(product_name: str) -> str:
    """
    Создает продукт в Stripe.
    Возвращает ID продукта.
    """
    product = stripe.Product.create(name=product_name)
    return product['id']


def create_stripe_price(product_id: str, price: int) -> str:
    """
    Создает цену в Stripe.
    Возвращает ID цены.
    """
    price_data = stripe.Price.create(
        unit_amount=price,
        currency="usd",
        product=product_id
    )
    return price_data['id']


def create_stripe_session(price_id: str) -> str:
    """
    Создает сессию оплаты в Stripe.
    Возвращает URL сессии оплаты.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        success_url="http://127.0.0.1:8000/success/",
        cancel_url="http://127.0.0.1:8000/cancel/",
    )
    return session['url']
