import graphene

from django_mall_cart.graphql.storefront.cart import CartQuery
from django_mall_cart.graphql.storefront.cart_line import (
    CartLineMutation,
    CartLineQuery,
)


class Mutation(
    CartLineMutation,
    graphene.ObjectType,
):
    pass


class Query(
    CartLineQuery,
    CartQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
