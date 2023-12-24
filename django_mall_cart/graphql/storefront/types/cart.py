from django.core.exceptions import ValidationError

from django_filters import CharFilter, FilterSet, OrderingFilter
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.relay.connection import ExtendedConnection
from django_app_core.types import Money
from django_mall_cart.helpers.cart_helper import CartHelper
from django_mall_cart.models import Cart


class CartType(DjangoObjectType):
    class Meta:
        model = Cart
        fields = ()


class CartFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")

    class Meta:
        model = Cart
        fields = []

    order_by = OrderingFilter(
        fields=(
            "slug",
            "created_at",
            "updated_at",
        )
    )


class CartConnection(graphene.relay.Connection):
    class Meta:
        node = CartType


class CartNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = Cart
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = CartFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    cost_final = graphene.Field(Money, required=True)
    cost_shipment = graphene.Field(Money, shipment_id=graphene.ID(default_value=None))
    cost_total = graphene.Field(Money, shipment_id=graphene.ID(default_value=None))
    quantity = graphene.Field(graphene.Int, required=True)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            queryset.select_related("customer", "customer__profile")
            .prefetch_related("cartline_set")
            .filter(customer_id=info.context.user.id)
        )

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            cls._meta.model.objects.select_related("customer")
            .filter(pk=id, customer_id=info.context.user.id)
            .first()
        )

    @staticmethod
    def resolve_cost_final(root: Cart, info: ResolveInfo):
        cart_helper = CartHelper(cart=root)

        return cart_helper.get_cost_final()

    @staticmethod
    def resolve_cost_shipment(
        root: Cart, info: ResolveInfo, shipment_id=None, **kwargs
    ):
        cart_helper = CartHelper(cart=root)
        result, cost, currency = cart_helper.get_cost_shipment(shipmentId=shipment_id)

        if result:
            result = {"amount": cost, "currency": currency}
            return result
        else:
            raise ValidationError("Can not find this shipment!")

    @staticmethod
    def resolve_cost_total(root: Cart, info: ResolveInfo, shipment_id=None, **kwargs):
        cart_helper = CartHelper(cart=root)
        result, cost, currency = cart_helper.get_cost_total(shipmentId=shipment_id)

        if result:
            result = {"amount": cost, "currency": currency}
            return result
        else:
            raise ValidationError("Can not find this payment or shipment!")

    @staticmethod
    def resolve_quantity(root: Cart, info: ResolveInfo):
        cart_helper = CartHelper(cart=root)

        return cart_helper.get_quantity()
