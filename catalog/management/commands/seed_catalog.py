from django.core.management.base import BaseCommand

from catalog.models import Category, Product

CATEGORIES = [
    ("videokarty", "Видеокарты", 10, ["rtx", "gtx", "radeon", "rx ", "видеокарт"]),
    ("processory", "Процессоры", 20, ["ryzen", "intel", "core i", "процессор", "cpu"]),
    ("ozu", "Оперативная память", 30, ["ddr", "kingston", "corsair vengeance", "озу", "ram"]),
    ("materinki", "Материнские платы", 40, ["motherboard", "b550", "b650", "z790", "материн"]),
    ("nakopiteli", "Накопители", 50, ["ssd", "nvme", "hdd", "samsung 980", "накоп"]),
    ("bp", "Блоки питания", 60, ["psu", "watt", "блок питания", "be quiet", "seasonic"]),
]

DEMO_PRODUCTS = [
    ("videokarty", "NVIDIA GeForce RTX 4070 Super 12GB", "425000", "Игровая видеокарта для 1440p и трассировки лучей."),
    ("videokarty", "AMD Radeon RX 7800 XT 16GB", "389000", "16 ГБ памяти и отличный запас по разрешению."),
    ("videokarty", "NVIDIA GeForce RTX 4060 8GB", "245000", "Отличный старт для Full HD и трассировки лучей."),
    ("videokarty", "NVIDIA GeForce RTX 4080 Super 16GB", "689000", "Карта для 4K, стрима и тяжёлых игровых сцен."),
    ("videokarty", "AMD Radeon RX 7600 8GB", "198000", "Доступная видеокарта для Full HD без лишнего шума."),
    ("videokarty", "NVIDIA GeForce RTX 4070 Ti Super 16GB", "545000", "16 ГБ GDDR6X и запас под высокие настройки в 1440p/4K."),
    ("processory", "AMD Ryzen 7 7700X", "198000", "8 ядер для игр и стриминга на сокете AM5."),
    ("processory", "Intel Core i5-14600K", "189000", "Гибридная архитектура для игр и работы."),
    ("processory", "AMD Ryzen 5 7600", "145000", "6 ядер Zen 4 — хороший баланс цены и FPS."),
    ("processory", "Intel Core i7-14700K", "279000", "Мощный процессор для монтажа, игр и многозадачности."),
    ("processory", "AMD Ryzen 9 7900X", "329000", "12 ядер для рабочих станций и тяжёлого рендера."),
    ("ozu", "Kingston Fury Beast 32GB DDR5-6000", "62000", "Двухканальный комплект 2×16 ГБ."),
    ("ozu", "Corsair Vengeance 16GB DDR5-5600", "34000", "Надёжная память для стартовых AM5/LGA1700 сборок."),
    ("ozu", "G.Skill Trident Z5 RGB 32GB DDR5-6400", "78000", "Быстрый комплект с RGB для игровых сборок."),
    ("ozu", "Kingston Fury Beast 64GB DDR5-5600", "118000", "4×16 ГБ для монтажа, виртуалок и тяжёлых проектов."),
    ("materinki", "Gigabyte B650 Aorus Elite AX", "129000", "Wi-Fi, PCIe 5.0 и крепкая система питания."),
    ("materinki", "MSI MAG B760 Tomahawk WiFi", "118000", "Плата под Intel 12–14 поколений с Wi-Fi 6E."),
    ("materinki", "ASUS TUF Gaming B650-PLUS WiFi", "135000", "Надёжная AM5-плата с усиленным питанием и Wi-Fi."),
    ("materinki", "MSI MAG Z790 Tomahawk WiFi", "189000", "Плата под разгон Intel и быстрые SSD PCIe 5.0."),
    ("nakopiteli", "Samsung 990 EVO Plus 1TB NVMe", "58000", "Быстрый SSD для системы и игр."),
    ("nakopiteli", "WD Black SN850X 2TB NVMe", "98000", "Быстрый диск под игры и рабочие проекты."),
    ("nakopiteli", "Kingston NV2 1TB NVMe", "32000", "Недорогой SSD для апгрейда ноутбука или ПК."),
    ("nakopiteli", "Samsung 990 PRO 2TB NVMe", "129000", "Топовая скорость чтения/записи для игр и монтажа."),
    ("nakopiteli", "Seagate Barracuda 4TB HDD", "45000", "Объёмный диск для архива, медиатеки и бэкапов."),
    ("bp", "be quiet! Pure Power 12 M 750W", "72000", "80+ Gold, тихий и с запасом под RTX 40."),
    ("bp", "Corsair RM850x 850W", "89000", "Полностью модульный блок 80+ Gold для мощных сборок."),
    ("bp", "Seasonic Focus GX-650 650W", "64000", "Надёжный 80+ Gold для средних игровых ПК."),
    ("bp", "MSI MAG A750GL PCIE5 750W", "69000", "Блок с разъёмом 12VHPWR под современные видеокарты."),
]


class Command(BaseCommand):
    help = "Создаёт категории и демо-товары, если каталог пустой"

    def handle(self, *args, **options):
        categories = {}
        for slug, name, order, _keywords in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "sort_order": order},
            )
            categories[slug] = category
        self.stdout.write(f"Категорий: {Category.objects.count()}")

        for product in Product.objects.filter(category__isnull=True):
            name = product.name.lower()
            for slug, _name, _order, keywords in CATEGORIES:
                if any(word in name for word in keywords):
                    product.category = categories[slug]
                    product.save(update_fields=["category"])
                    break

        created = 0
        for slug, name, price, description in DEMO_PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": categories[slug],
                    "price": price,
                    "description": description,
                    "in_stock": True,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Добавлено товаров: {created}"))
