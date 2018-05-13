import factory
import factory.django
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from profiles.models import *
from shops.models import UserShop, ShopProduct, ShopProductImage
from cartridge.shop.models import Category
import random
import decimal

cnt = Country.objects.all()[0]
rgn = Region.objects.all()[0]
cty = City.objects.all()[0]

images = ['uploads/easy-listening_4460x4460.jpg',
          'uploads/inflatable-donut-drink-holder_4460x4460.jpg',
          'uploads/green-smart-watch-fitness_4460x4460.jpg',
          'uploads/man-writing_4460x4460.jpg',
          'uploads/spinal-twist-yoga-wheel_4460x4460.jpg',
          'uploads/black-bag-over-the-shoulder_4460x4460.jpg']

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
    bio = factory.Faker('text', max_nb_chars=350, ext_word_list=None, locale='ru_RU')


class ShopFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = UserShop

    user = factory.SubFactory('theme.factory.UserFactory',  shop=None)
    image = factory.Sequence(lambda n: random.choice(images))
    background = factory.Sequence(lambda n: random.choice(images))
    shopname = factory.Faker('company')
    bio = factory.Faker('text', max_nb_chars=350, ext_word_list=None, locale='ru_RU')
    express_other = factory.Faker('text', max_nb_chars=150, ext_word_list=None, locale='ru_RU')
    payment_other = factory.Faker('text', max_nb_chars=150, ext_word_list=None, locale='ru_RU')
    rules = factory.Faker('text', max_nb_chars=250, ext_word_list=None, locale='ru_RU')

    express_point = factory.Faker('boolean', chance_of_getting_true=50)
    express_city = factory.Faker('boolean', chance_of_getting_true=50)
    express_country = factory.Faker('boolean', chance_of_getting_true=50)
    express_world = factory.Faker('boolean', chance_of_getting_true=50)
    express_mail = factory.Faker('boolean', chance_of_getting_true=50)
    express_personal = factory.Faker('boolean', chance_of_getting_true=50)

    payment_personal = factory.Faker('boolean', chance_of_getting_true=50)
    payment_bank_transfer = factory.Faker('boolean', chance_of_getting_true=50)
    payment_card_transfer = factory.Faker('boolean', chance_of_getting_true=50)


class ShopProductFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ShopProduct

    # shop = factory.SubFactory(ShopFactory)
    # categories = factory.Iterator(Category.objects.all())
    title = factory.Sequence(lambda n: "Товар %03d" % n)
    price = factory.Sequence(lambda n: random.randint(1000,10000))
    material = factory.Faker('sentence', nb_words=3, variable_nb_words=True, ext_word_list=None, locale='ru_RU')
    condition = 1
    description = factory.Faker('text', max_nb_chars=250, ext_word_list=None, locale='ru_RU')

    # images = factory.RelatedFactory(ShopProductImageFactory, 'shopproduct', action='CREATE')


class ShopProductImageFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ShopProductImage

    file = factory.Sequence(lambda n: random.choice(images))
    # product = factory.SubFactory(ShopProductFactory)



@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Faker('email')
    username = factory.Sequence(lambda n: "user_tmp_%d" % n)
    password = '1234567'
    profile = factory.RelatedFactory(ProfileFactory, 'user')
    shop = factory.RelatedFactory(ShopFactory, 'user')








## make BLogPostFactory
### language = factory.Iterator(models.User.objects.all())


### make BlogPost comments factory


### make MasterReviewsComments

### make ShopReviewComments
