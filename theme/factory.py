import factory
import factory.django
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from profiles.models import *
from shops.models import UserShop, ShopProduct, ShopProductImage, ProductReview
from mezzanine.blog.models import BlogPost, BlogCategory
from cartridge.shop.models import Category
import random
import decimal

cnt = Country.objects.all()[0]
rgn = Region.objects.all()[0]
cty = City.objects.all()[0]

images = ['uploads/1_(43).jpeg',
          'uploads/1_(36).jpeg',
          'uploads/1_(24).jpeg',
          'uploads/1_(7).jpg',
          'uploads/1_(14).jpeg',
          'uploads/1_(41).jpeg',
          'uploads/1_(21).jpeg',
          'uploads/1_(28).jpeg',
          'uploads/1_(6).jpg',
          'uploads/1_(1).jpg',
          'uploads/1_(2).jpeg',
          'uploads/1_(8).jpg']

class ProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = UserProfile

    user = factory.SubFactory('theme.factory.UserFactory',  profile=None)
    first_name = factory.Faker('first_name_female', locale='ru_RU')
    last_name = factory.Faker('last_name_female', locale='ru_RU')
    image = factory.Sequence(lambda n: random.choice(images))
    background = factory.Sequence(lambda n: random.choice(images))
    phone = factory.Faker('phone_number', locale='ru_RU')
    status = factory.Faker('boolean', chance_of_getting_true=30)

    country = cnt
    region = rgn
    city = cty
    bio = factory.Faker('text', max_nb_chars=350, ext_word_list=None)

class ProductReviewFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ProductReview

    approved = True
    rating = factory.Sequence(lambda n: random.randint(1,10))
    content = factory.Faker('text', max_nb_chars=350, ext_word_list=None)
    author = factory.Iterator(User.objects.all())



class ShopProductImageFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ShopProductImage

    file = factory.Sequence(lambda n: random.choice(images))


class ShopProductFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ShopProduct

    # shop = factory.SubFactory(ShopFactory)
    # categories = factory.Iterator(Category.objects.first())
    title = factory.Sequence(lambda n: "Товар %03d" % n)
    price = factory.Sequence(lambda n: random.randint(1000,10000))
    material = factory.Faker('sentence', nb_words=3, variable_nb_words=True, ext_word_list=None)
    condition = 1
    available = True
    description = factory.Faker('text', max_nb_chars=250, ext_word_list=None)

    image1 = factory.RelatedFactory(ShopProductImageFactory, 'product')
    image2 = factory.RelatedFactory(ShopProductImageFactory, 'product')

    review1 = factory.RelatedFactory(ProductReviewFactory, 'product')
    review12 = factory.RelatedFactory(ProductReviewFactory, 'product')



    # product = factory.SubFactory(ShopProductFactory)

class ShopFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = UserShop

    user = factory.SubFactory('theme.factory.UserFactory',  shop=None)
    image = factory.Sequence(lambda n: random.choice(images))
    background = factory.Sequence(lambda n: random.choice(images))
    shopname = factory.Faker('company')
    bio = factory.Faker('text', max_nb_chars=350, ext_word_list=None)
    delivery_other = factory.Faker('text', max_nb_chars=150, ext_word_list=None)
    payment_other = factory.Faker('text', max_nb_chars=150, ext_word_list=None)
    rules = factory.Faker('text', max_nb_chars=250, ext_word_list=None)

    product1 = factory.RelatedFactory(ShopProductFactory, 'shop')
    product2 = factory.RelatedFactory(ShopProductFactory, 'shop')
    product3 = factory.RelatedFactory(ShopProductFactory, 'shop')
    # product4 = factory.RelatedFactory(ShopProductFactory, 'shop')
    # product5 = factory.RelatedFactory(ShopProductFactory, 'shop')
    # product6 = factory.RelatedFactory(ShopProductFactory, 'shop')
    # product7 = factory.RelatedFactory(ShopProductFactory, 'shop')
    # product8 = factory.RelatedFactory(ShopProductFactory, 'shop')
    # product9 = factory.RelatedFactory(ShopProductFactory, 'shop')
    # product10 = factory.RelatedFactory(ShopProductFactory, 'shop')

@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Faker('email')
    username = factory.Sequence(lambda n: "user_tmp_%d" % n)
    password = '1234567'
    profile = factory.RelatedFactory(ProfileFactory, 'user')
    shop = factory.RelatedFactory(ShopFactory, 'user')



class BlogPostFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = BlogPost

    user = factory.Iterator(User.objects.all())
    title = factory.Faker('sentence', nb_words=4)
    content = factory.Faker('text', max_nb_chars=1350, ext_word_list=None)
    featured_image = factory.Sequence(lambda n: random.choice(images))
    allow_comments = True




## make BLogPostFactory
### language = factory.Iterator(models.User.objects.all())


### make BlogPost comments factory


### make MasterReviewsComments

### make ShopReviewComments
