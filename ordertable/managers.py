from mezzanine.core.managers import SearchableManager


class OrderTableItemManager(SearchableManager):

    def published(self, for_user=None):
        """
        For non-staff users, return available items
        """
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(available=True).filter(performer=None)
