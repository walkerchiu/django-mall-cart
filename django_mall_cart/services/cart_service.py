from typing import Tuple

from django.db import transaction

from django_app_account.models import User
from django_app_organization.models import Organization
from django_mall_cart.models import Cart


class CartService:
    def __init__(self, organization: Organization, customer: User):
        self.organization = organization
        self.customer = customer

    @transaction.atomic
    def create_cart(self, slug: str = "default") -> Tuple[bool, Cart]:
        cart, created = Cart.objects.get_or_create(
            organization=self.organization, customer=self.customer, slug=slug
        )

        return created, cart
