from django.contrib import admin

from profiles.models import UserProfile, MasterReview


class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    search_fields = ('user', 'first_name', 'last_name')
    list_display = ('full_name', 'status',
                    'allow_blogpost_count',
                    'allow_ordertable_count',
                    'allow_product_count',
                    'show_link',)
    list_editable = ('allow_blogpost_count',
                     'allow_ordertable_count',
                     'allow_product_count',)
    list_filter = ('status',)

    def show_link(self, obj):
        return '<a href="%s">Посмотреть на сайте</a>' % obj.get_absolute_url()
    show_link.allow_tags = True
    show_link.short_description = "Посмотреть на сайте"

    def full_name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)
    full_name.allow_tags = True
    full_name.short_description = "Имя пользователя"


class MasterReviewAdmin(admin.ModelAdmin):
    model =  MasterReview
    search_fields = ('content', 'author', 'master', 'order')
    list_display = ('id', 'author', 'content', 'master', 'order', 'avg_rating', 'approved')
    list_editable = ('approved',)
    list_filter = ('approved',)



admin.site.register(MasterReview, MasterReviewAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
