import graphene


class Mutation(
    graphene.ObjectType,
):
    pass


class Query(
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
