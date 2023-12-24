import graphene

from django_mall_cart.graphql.storefront.types.cart import CartNode


class CartMutation(graphene.ObjectType):
    pass


class CartQuery(graphene.ObjectType):
    cart = graphene.relay.Node.Field(CartNode)
