def cart_count(request):
    cart = request.session.get("cart", {})
    count = 0
    for qty in cart.values():
        try:
            count += max(0, int(qty))
        except (TypeError, ValueError):
            continue
    return {
        "cart_count": count,
        "query": request.GET.get("q", "").strip(),
    }
