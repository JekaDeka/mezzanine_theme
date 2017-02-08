from django.db import models
from mezzanine.core.fields import RichTextField


class MyProfile(models.Model):
    user = models.OneToOneField("auth.User")
    image = models.ImageField(
        upload_to='users/avatars/', blank=True, verbose_name=("Изображение"))
    city = models.CharField(max_length=255, blank=True,
                            verbose_name=("Расположение"))
    phone = models.CharField(max_length=255, blank=True,
                             verbose_name=("Телефон"))
    bio = RichTextField(default="", verbose_name=("Биография"))
