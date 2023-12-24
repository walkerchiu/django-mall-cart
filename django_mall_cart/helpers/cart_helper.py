from typing import Tuple

from django.conf import settings

from graphql_relay import from_global_id

from django_app_core.types import Money
from django_mall_cart.models import Cart
from django_mall_shipment.models import Shipment


class CartHelper:
    def __init__(self, cart: Cart):
        self.cart = cart
        self.organization = cart.organization

    def get_cost_final(self) -> Money:
        cost_final_total = 0

        cartline_set = self.cart.cartline_set.all()
        for cartline in cartline_set:
            if cartline.variant.is_visible and cartline.variant.product.is_visible:
                cost_final_total = cost_final_total + (
                    0
                    if cartline.variant.price_sale_amount is None
                    else cartline.variant.price_sale_amount * cartline.quantity
                )

        result = {
            "amount": cost_final_total,
            "currency": settings.DEFAULT_CURRENCY_CODE,
        }

        return result

    def get_cost_shipment(self, shipmentId=None) -> Tuple[bool, float, str]:
        if shipmentId is None:
            return True, 0, ""

        try:
            _, shipment_id = from_global_id(shipmentId)
        except:
            return False, 0, ""

        shipment = (
            Shipment.objects.only("currency", "price_amount")
            .filter(organization=self.organization, pk=shipment_id)
            .first()
        )
        if shipment and shipment.is_visible:
            return True, shipment.price_amount, shipment.currency

        return False, 0, ""

    def get_cost_total(self, shipmentId=None) -> Tuple[bool, float, str]:
        result_shipment, shipment_amount, shipment_currency = self.get_cost_shipment(
            shipmentId=shipmentId
        )

        cost_final = self.get_cost_final()
        amount = cost_final["amount"]

        if result_shipment:
            amount = amount + shipment_amount

            return True, amount, settings.DEFAULT_CURRENCY_CODE
        else:
            return False, 0, ""

    def get_quantity(self) -> int:
        quantity_total = 0

        cartline_set = self.cart.cartline_set.all()
        for cartline in cartline_set:
            if cartline.variant.is_visible and cartline.variant.product.is_visible:
                quantity_total = quantity_total + cartline.quantity

        return quantity_total
