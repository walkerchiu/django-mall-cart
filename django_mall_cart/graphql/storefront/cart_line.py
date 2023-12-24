import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from graphene import ResolveInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
import graphene

from django_app_core.decorators import strip_input
from django_app_core.relay.connection import DjangoFilterConnectionField
from django_app_core.types import TaskWarningType
from django_mall_cart.graphql.storefront.types.cart import CartNode
from django_mall_cart.graphql.storefront.types.cart_line import CartLineNode
from django_mall_cart.models import Cart, CartLine
from django_mall_product.models import Variant


class CreateCartLineBatch(graphene.relay.ClientIDMutation):
    class Input:
        cartId = graphene.ID(required=True)
        variantIdList = graphene.List(graphene.NonNull(graphene.ID), required=True)
        quantityList = graphene.List(
            graphene.NonNull(graphene.Int), required=True, min_value=1
        )

    success = graphene.Boolean()
    warnings = graphene.Field(TaskWarningType)
    cart = graphene.Field(CartNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(
        cls,
        root,
        info: ResolveInfo,
        **input,
    ):
        cartId = input["cartId"]
        variantIdList = input["variantIdList"]
        quantityList = input["quantityList"]

        warnings = {
            "done": [],
            "in_protected": [],
            "in_use": [],
            "not_found": [],
            "error": [],
        }

        try:
            _, cart_id = from_global_id(cartId)
        except:
            raise ValidationError("Bad Request!")

        if variantIdList is None or len(variantIdList) == 0:
            raise ValidationError("variantIdList should not be empty!")
        elif len(variantIdList) != len(quantityList):
            raise ValidationError(
                "variantIdList and quantityList must be the same length!"
            )

        try:
            cart = Cart.objects.only("id").get(id=cart_id)
        except:
            raise ValidationError("Can not find this cart!")

        for index, variantId in enumerate(variantIdList):
            quantity = int(quantityList[index])
            if quantity <= 0:
                warnings["error"].append(variantId)
            elif isinstance(variantId, str):
                try:
                    _, variant_id = from_global_id(variantId)
                except:
                    warnings["error"].append(variantId)
                else:
                    variant = (
                        Variant.objects.filter(pk=variant_id)
                        .filter(
                            Q(published_at__lte=datetime.date.today())
                            | Q(published_at__isnull=True),
                            is_published=True,
                        )
                        .filter(
                            Q(product__published_at__lte=datetime.date.today())
                            | Q(product__published_at__isnull=True),
                            product__is_published=True,
                        )
                        .first()
                    )
                    if variant:
                        if (
                            variant.is_primary
                            and Variant.objects.filter(product=variant.product).count()
                            > 1
                        ):
                            warnings["in_protected"].append(variantId)
                        else:
                            cart_line = CartLine.objects.filter(
                                cart_id=cart_id, variant_id=variant_id
                            ).first()
                            if cart_line:
                                warnings["in_use"].append(variantId)
                            else:
                                CartLine.objects.create(
                                    cart_id=cart_id,
                                    variant_id=variant_id,
                                    quantity=quantity,
                                )
                                warnings["done"].append(variantId)
                    else:
                        warnings["not_found"].append(variantId)
            else:
                warnings["error"].append(variantId)

        return CreateCartLineBatch(success=True, warnings=warnings, cart=cart)


class DeleteCartLineBatch(graphene.relay.ClientIDMutation):
    class Input:
        cartId = graphene.ID(required=True)
        variantIdList = graphene.List(graphene.NonNull(graphene.ID), required=True)

    success = graphene.Boolean()
    warnings = graphene.Field(TaskWarningType)
    cart = graphene.Field(CartNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(
        cls,
        root,
        info: ResolveInfo,
        **input,
    ):
        cartId = input["cartId"]
        variantIdList = input["variantIdList"]

        warnings = {
            "done": [],
            "in_protected": [],
            "in_use": [],
            "not_found": [],
            "error": [],
        }

        try:
            _, cart_id = from_global_id(cartId)
        except:
            raise ValidationError("Bad Request!")

        if variantIdList is None or len(variantIdList) == 0:
            raise ValidationError("variantIdList should not be empty!")

        try:
            cart = Cart.objects.only("id").get(id=cart_id)
        except:
            raise ValidationError("Can not find this cart!")

        for index, variantId in enumerate(variantIdList):
            if isinstance(variantId, str):
                try:
                    _, variant_id = from_global_id(variantId)
                except:
                    warnings["error"].append(variantId)
                else:
                    cart_line = CartLine.objects.filter(
                        cart_id=cart_id, variant_id=variant_id
                    ).first()
                    if cart_line:
                        cart_line.delete()

                        warnings["done"].append(variantId)
                    else:
                        warnings["not_found"].append(variantId)
            else:
                warnings["error"].append(variantId)

        return DeleteCartLineBatch(success=True, warnings=warnings, cart=cart)


class UpdateCartLineBatch(graphene.relay.ClientIDMutation):
    class Input:
        cartId = graphene.ID(required=True)
        variantIdList = graphene.List(graphene.NonNull(graphene.ID), required=True)
        quantityList = graphene.List(
            graphene.NonNull(graphene.Int), required=True, min_value=1
        )

    success = graphene.Boolean()
    warnings = graphene.Field(TaskWarningType)
    cart = graphene.Field(CartNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(
        cls,
        root,
        info: ResolveInfo,
        **input,
    ):
        cartId = input["cartId"]
        variantIdList = input["variantIdList"]
        quantityList = input["quantityList"]

        warnings = {
            "done": [],
            "in_protected": [],
            "in_use": [],
            "not_found": [],
            "error": [],
        }

        try:
            _, cart_id = from_global_id(cartId)
        except:
            raise ValidationError("Bad Request!")

        if variantIdList is None or len(variantIdList) == 0:
            raise ValidationError("variantIdList should not be empty!")
        elif len(variantIdList) != len(quantityList):
            raise ValidationError(
                "variantIdList and quantityList must be the same length!"
            )

        try:
            cart = Cart.objects.only("id").get(id=cart_id)
        except:
            raise ValidationError("Can not find this cart!")

        for index, variantId in enumerate(variantIdList):
            quantity = int(quantityList[index])
            if quantity <= 0:
                warnings["error"].append(variantId)
            elif isinstance(variantId, str):
                try:
                    _, variant_id = from_global_id(variantId)
                except:
                    warnings["error"].append(variantId)
                else:
                    variant = (
                        Variant.objects.filter(pk=variant_id)
                        .filter(
                            Q(published_at__lte=datetime.date.today())
                            | Q(published_at__isnull=True),
                            is_published=True,
                        )
                        .filter(
                            Q(product__published_at__lte=datetime.date.today())
                            | Q(product__published_at__isnull=True),
                            product__is_published=True,
                        )
                        .first()
                    )
                    if variant:
                        cart_line = CartLine.objects.filter(
                            cart_id=cart_id, variant_id=variant_id
                        ).first()
                        if cart_line:
                            if (
                                variant.is_primary
                                and Variant.objects.filter(
                                    product=variant.product
                                ).count()
                                > 1
                            ):
                                cart_line.delete()
                                warnings["error"].append(variantId)
                            else:
                                cart_line.quantity = quantity
                                cart_line.save()
                                warnings["done"].append(variantId)
                        else:
                            warnings["not_found"].append(variantId)
                    else:
                        warnings["error"].append(variantId)
            else:
                warnings["error"].append(variantId)

        return UpdateCartLineBatch(success=True, warnings=warnings, cart=cart)


class CartLineMutation(graphene.ObjectType):
    cart_line_create_batch = CreateCartLineBatch.Field()
    cart_line_delete_batch = DeleteCartLineBatch.Field()
    cart_line_update_batch = UpdateCartLineBatch.Field()


class CartLineQuery(graphene.ObjectType):
    cart_lines = DjangoFilterConnectionField(
        CartLineNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
