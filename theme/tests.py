from django.test import TestCase
import factory
import factory.django
from theme.factory import *


# users = UserFactory.create_batch(10)
# for user in users:
#     profile = ProfileFactory.create(user=user)


# shop = ShopFactory()
# ShopProductFactory.create_batch(3, shop=shop)


for fst in range(0, 3):
    shop = ShopFactory()
    for snd in range(0, 10):
        product = ShopProductFactory.create(shop=shop)
        ShopProductImageFactory.create_batch(3, product=product)



products = ShopProduct.objects.all()
categories = Category.objects.all()

for product in products:
    product.categories = categories
    product.save()
