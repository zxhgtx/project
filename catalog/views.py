from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Category, Order, OrderItem, Product

SORT_CHOICES = {
    "new": ("-created_at", "Сначала новые"),
    "price_asc": ("price", "Сначала дешевле"),
    "price_desc": ("-price", "Сначала дороже"),
    "name": ("name", "По названию"),
}


def _cart(request):
    return request.session.get("cart", {})


def _safe_next(request, fallback="product_list"):
    candidate = request.POST.get("next") or request.GET.get("next") or ""
    parsed = urlparse(candidate)
    if candidate.startswith("/") and not parsed.netloc:
        return candidate
    return reverse(fallback)


def _parse_price(value):
    raw = (value or "").strip().replace(" ", "").replace(",", ".")
    if not raw:
        return None
    try:
        amount = Decimal(raw)
    except (InvalidOperation, ValueError):
        return None
    return amount if amount >= 0 else None


def _cart_items(request):
    cart = _cart(request)
    items = []
    total = Decimal("0")
    ids = [int(pk) for pk in cart.keys() if str(pk).isdigit()]
    products = {p.pk: p for p in Product.objects.select_related("category").filter(pk__in=ids)}

    for raw_pk, qty in list(cart.items()):
        product = products.get(int(raw_pk)) if str(raw_pk).isdigit() else None
        if not product:
            continue
        try:
            quantity = max(1, int(qty))
        except (TypeError, ValueError):
            quantity = 1
        subtotal = product.price * quantity
        total += subtotal
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
    return items, total


def product_list(request):
    products = Product.objects.select_related("category")
    categories = Category.objects.annotate(product_count=Count("products")).order_by(
        "sort_order", "name"
    )

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "new")
    if sort not in SORT_CHOICES:
        sort = "new"

    in_stock_only = request.GET.get("in_stock") == "1"
    min_price = _parse_price(request.GET.get("min_price"))
    max_price = _parse_price(request.GET.get("max_price"))

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if in_stock_only:
        products = products.filter(in_stock=True)
    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)

    products = products.order_by(SORT_CHOICES[sort][0])
    paginator = Paginator(products, 9)
    page = paginator.get_page(request.GET.get("page"))

    show_hero = (
        not query
        and not selected_category
        and not in_stock_only
        and min_price is None
        and max_price is None
        and not request.GET.get("page")
    )

    return render(
        request,
        "catalog/product_list.html",
        {
            "page": page,
            "products": page.object_list,
            "categories": categories,
            "selected_category": selected_category,
            "query": query,
            "sort": sort,
            "sort_choices": SORT_CHOICES,
            "total_count": paginator.count,
            "show_hero": show_hero,
            "in_stock_only": in_stock_only,
            "min_price": request.GET.get("min_price", "").strip(),
            "max_price": request.GET.get("max_price", "").strip(),
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk)
    related = (
        Product.objects.select_related("category")
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
        if product.category_id
        else Product.objects.exclude(pk=product.pk)[:4]
    )
    return render(
        request,
        "catalog/product_detail.html",
        {"product": product, "related": related},
    )


def about(request):
    return render(
        request,
        "catalog/about.html",
        {
            "product_count": Product.objects.count(),
            "category_count": Category.objects.count(),
        },
    )


def cart_view(request):
    items, total = _cart_items(request)
    return render(request, "catalog/cart.html", {"items": items, "total": total})


def checkout(request):
    items, total = _cart_items(request)
    if not items:
        messages.info(request, "Корзина пуста — добавьте товары перед оформлением.")
        return redirect("cart")

    form = {
        "name": request.POST.get("name", "").strip() if request.method == "POST" else "",
        "phone": request.POST.get("phone", "").strip() if request.method == "POST" else "",
        "email": request.POST.get("email", "").strip() if request.method == "POST" else "",
        "comment": request.POST.get("comment", "").strip() if request.method == "POST" else "",
    }
    errors = {}

    if request.method == "POST":
        if len(form["name"]) < 2:
            errors["name"] = "Укажите имя."
        if len(form["phone"]) < 6:
            errors["phone"] = "Укажите телефон."
        email = form["email"]
        if email and "@" not in email:
            errors["email"] = "Проверьте email."

        if not errors:
            with transaction.atomic():
                order = Order.objects.create(
                    name=form["name"],
                    phone=form["phone"],
                    email=email,
                    comment=form["comment"],
                    total=total,
                )
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        name=item["product"].name,
                        price=item["product"].price,
                        quantity=item["quantity"],
                    )
            request.session["cart"] = {}
            request.session.modified = True
            messages.success(request, f"Заказ №{order.pk} принят. Мы свяжемся с вами.")
            return redirect("order_success", pk=order.pk)

    return render(
        request,
        "catalog/checkout.html",
        {"items": items, "total": total, "form": form, "errors": errors},
    )


def order_success(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    return render(request, "catalog/order_success.html", {"order": order})


@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not product.in_stock:
        messages.warning(request, "Этого товара сейчас нет в наличии.")
        return redirect("product_detail", pk=pk)

    qty = request.POST.get("qty", "1")
    try:
        qty = max(1, min(99, int(qty)))
    except (TypeError, ValueError):
        qty = 1

    cart = _cart(request)
    key = str(product.pk)
    cart[key] = min(99, int(cart.get(key, 0)) + qty)
    request.session["cart"] = cart
    request.session.modified = True
    messages.success(request, f"«{product.name}» добавлен в корзину.")
    return redirect(_safe_next(request, "cart"))


@require_POST
def update_cart(request, pk):
    cart = _cart(request)
    key = str(pk)
    action = request.POST.get("action")
    qty = request.POST.get("qty")

    if action == "remove" or qty == "0":
        cart.pop(key, None)
        messages.info(request, "Товар удалён из корзины.")
    else:
        try:
            quantity = max(1, min(99, int(qty)))
        except (TypeError, ValueError):
            quantity = 1
        if key in cart or Product.objects.filter(pk=pk).exists():
            cart[key] = quantity
            messages.success(request, "Количество обновлено.")

    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


@require_POST
def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    messages.info(request, "Корзина очищена.")
    return redirect("cart")
