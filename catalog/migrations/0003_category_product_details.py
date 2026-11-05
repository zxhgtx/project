import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_product_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="Название")),
                ("slug", models.SlugField(unique=True, verbose_name="URL")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="products",
                to="catalog.category",
                verbose_name="Категория",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Добавлен",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True, verbose_name="Описание"),
        ),
        migrations.AddField(
            model_name="product",
            name="in_stock",
            field=models.BooleanField(default=True, verbose_name="В наличии"),
        ),
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="products/", verbose_name="Фото"),
        ),
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Название"),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Цена"),
        ),
        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Товар",
                "verbose_name_plural": "Товары",
            },
        ),
    ]
