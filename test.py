class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price



item1 = Product("RTX 4060", 150000)
item2 = Product("GTX 1660", 70000)

item1.price = 145000

print(item1.price)
print(item2.price)