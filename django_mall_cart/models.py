import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from safedelete.models import SOFT_DELETE_CASCADE

from django_app_account.models import User
from django_app_core.models import CommonDateAndSafeDeleteMixin
from django_app_organization.models import Organization
from django_mall_product.models import Variant


class Cart(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, models.CASCADE)
    customer = models.ForeignKey(User, models.CASCADE)
    slug = models.CharField(max_length=255, db_index=True)
    sort_key = models.IntegerField(db_index=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_cart_cart"
        get_latest_by = "updated_at"
        index_together = (("organization", "slug"),)
        unique_together = [["organization", "customer", "slug"]]
        ordering = ["sort_key"]

    def __str__(self):
        return str(self.id)


class CartLine(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, models.CASCADE)
    variant = models.ForeignKey(Variant, models.CASCADE)
    quantity = models.IntegerField(db_index=True, validators=[MinValueValidator(1)])

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_cart_cartline"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    def __str__(self):
        return str(self.id)
