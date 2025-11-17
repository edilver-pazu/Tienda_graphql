import graphene
from graphene_django import DjangoObjectType
from .models import Cliente

class ClienteType(DjangoObjectType):
    class Meta:
        model = Cliente
        fields = "__all__"

class Query(graphene.ObjectType):
    clientes = graphene.List(ClienteType)

    def resolve_clientes(self, info):
        return Cliente.objects.all()
    