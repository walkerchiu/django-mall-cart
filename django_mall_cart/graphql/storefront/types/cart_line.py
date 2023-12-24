from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

from django_filters import FilterSet, OrderingFilter
from graphene import ResolveInfo
from graphene_django import DjangoListField, DjangoObjectType
from graphql_relay import to_global_id
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.relay.connection import ExtendedConnection
from django_app_core.types import Money
from django_mall_cart.models import CartLine
from django_mall_product.models import ProductTrans


class CartLineType(DjangoObjectType):
    class Meta:
        model = CartLine
        fields = ()


class CartMerchandiseTransType(DjangoObjectType):
    class Meta:
        model = ProductTrans
        fields = (
            "language_code",
            "name",
        )


class CartMerchandiseType(DjangoObjectType):
    class Meta:
        model = CartLine
        fields = ()

    product_serial = graphene.String()
    product_slug = graphene.String(required=True)
    variant_slug = graphene.String(required=True)
    photo_url = graphene.String()
    variant_id = graphene.Field(graphene.ID, required=True)
    variant_price = graphene.Field(Money)
    variant_price_sale = graphene.Field(Money)
    variant_price_final = graphene.Field(Money)
    status = graphene.String(description="Possible value: NORMAL, TAKEN OFF")
    selected_option_values = graphene.List(graphene.String)
    translations = DjangoListField(CartMerchandiseTransType)

    @staticmethod
    def resolve_product_serial(root: CartLine, info: ResolveInfo):
        return root.variant.product.serial

    @staticmethod
    def resolve_product_slug(root: CartLine, info: ResolveInfo):
        return root.variant.product.slug

    @staticmethod
    def resolve_variant_slug(root: CartLine, info: ResolveInfo):
        return root.variant.slug

    @staticmethod
    def resolve_photo_url(root: CartLine, info: ResolveInfo):
        object = root.variant.product.productphoto_set.filter(is_primary=True).first()
        if not object:
            object = (
                root.variant.product.productphoto_set.order_by("sort_key")
                .order_by("created_at")
                .first()
            )
            if not object:
                return None

        key = (
            str(object.product.organization_id).replace("-", "")
            + "/product/"
            + str(object.product_id).replace("-", "")
            + "/img-"
            + object.s3_key
        )
        url = cache.get(key)
        if url:
            return url
        else:
            if default_storage.exists(object.s3_key):
                url = default_storage.url(object.s3_key)

                cache.set(
                    key,
                    url,
                    int(settings.AWS_QUERYSTRING_EXPIRE) - 600,
                )

                return url

            return None

    @staticmethod
    def resolve_variant_id(root: CartLine, info: ResolveInfo):
        return to_global_id("VariantNode", root.variant.id)

    @staticmethod
    def resolve_variant_price(root: CartLine, info: ResolveInfo):
        if root.variant.is_visible and root.variant.product.is_visible:
            return root.variant.price
        else:
            return None

    @staticmethod
    def resolve_variant_price_sale(root: CartLine, info: ResolveInfo):
        if root.variant.is_visible and root.variant.product.is_visible:
            return root.variant.price_sale
        else:
            return None

    @staticmethod
    def resolve_variant_price_final(root: CartLine, info: ResolveInfo):
        if root.variant.is_visible and root.variant.product.is_visible:
            return root.variant.price_sale
        else:
            return None

    @staticmethod
    def resolve_status(root: CartLine, info: ResolveInfo):
        if root.variant.is_visible and root.variant.product.is_visible:
            return "NORMAL"
        else:
            return "TAKEN OFF"

    @staticmethod
    def resolve_selected_option_values(root: CartLine, info: ResolveInfo):
        selected_option_values = []

        option_values = root.variant.selected_option_values.order_by(
            "product_option__sort_key"
        )
        for option_value in option_values:
            trans = option_value.translations.filter(
                language_code=root.variant.product.organization.language_code
            ).first()

            if trans:
                selected_option_values.append(trans.name)

        return selected_option_values

    @staticmethod
    def resolve_translations(root: CartLine, info: ResolveInfo):
        return root.variant.product.translations


class CartLineFilter(FilterSet):
    class Meta:
        model = CartLine
        fields = []

    order_by = OrderingFilter(
        fields=(
            "created_at",
            "updated_at",
        )
    )


class CartLineConnection(graphene.relay.Connection):
    class Meta:
        node = CartLineType


class CartLineNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = CartLine
        exclude = (
            "variant",
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = CartLineFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    merchandise = graphene.Field(CartMerchandiseType)
    cost = graphene.Field(Money, required=True)
    cost_final = graphene.Field(Money, required=True)
    cost_sale = graphene.Field(Money, required=True)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return queryset.select_related("cart", "variant", "variant__product").filter(
            cart__customer_id=info.context.user.id
        )

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            cls._meta.model.objects.select_related(
                "cart", "variant", "variant__product"
            )
            .filter(pk=id, cart__customer_id=info.context.user.id)
            .first()
        )

    @staticmethod
    def resolve_merchandise(root: CartLine, info: ResolveInfo):
        return root

    @staticmethod
    def resolve_cost(root: CartLine, info: ResolveInfo):
        if root.variant.price_amount is None:
            amount = 0
        else:
            amount = root.variant.price_amount * root.quantity

        result = {
            "amount": amount,
            "currency": root.variant.currency,
        }

        return result

    @staticmethod
    def resolve_cost_final(root: CartLine, info: ResolveInfo):
        if root.variant.price_sale_amount is None:
            amount = 0
        else:
            amount = root.variant.price_sale_amount * root.quantity

        result = {
            "amount": amount,
            "currency": root.variant.currency,
        }

        return result

    @staticmethod
    def resolve_cost_sale(root: CartLine, info: ResolveInfo):
        if root.variant.price_sale_amount is None:
            amount = 0
        else:
            amount = root.variant.price_sale_amount * root.quantity

        result = {
            "amount": amount,
            "currency": root.variant.currency,
        }

        return result
