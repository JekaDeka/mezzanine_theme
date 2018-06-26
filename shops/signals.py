from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from shops.models import ShopProduct, ProductReview


@receiver(post_save, sender=ProductReview)
@receiver(post_delete, sender=ProductReview)
def update_product_rating(sender, instance, **kwargs):
    """
    Calculates and saves the average rating.
    """
    product = instance.product
    ratings = [r.rating for r in ProductReview.objects.filter(product=product, approved=True)]
    count = len(ratings)
    _sum = sum(ratings)
    average = _sum / count if count > 0 else 0
    product.reviews_count = count
    product.reviews_sum = _sum
    product.reviews_average = average
    product.save()
    # count = len(ratings)
    # _sum = sum(ratings)
    # average = _sum / count if count > 0 else 0

    print('PRODUCT_RATING_UPDATE')
