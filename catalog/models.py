from django.db import models


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL", unique=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Название", max_length=200)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="products",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField("Фото", upload_to="products/", blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    in_stock = models.BooleanField("В наличии", default=True)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        PROCESSING = "processing", "В работе"
        DONE = "done", "Выполнен"

    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=40)
    email = models.EmailField("Email", blank=True)
    comment = models.TextField("Комментарий", blank=True)
    total = models.DecimalField("Сумма", max_digits=12, decimal_places=2)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.pk} — {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField("Название", max_length=200)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.name} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
