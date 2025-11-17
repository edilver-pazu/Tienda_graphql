import graphene
from graphene_django import DjangoObjectType
from .models import Cliente

class ClienteType(DjangoObjectType):
    class Meta:
        model = Cliente
        fields = "__all__"

class Query(graphene.ObjectType):
    clientes = graphene.List(ClienteType)
    cliente = graphene.Field(ClienteType, id=graphene.ID()) #en singular para bucscar un solo cliente

    def resolve_clientes(self, info):
        return Cliente.objects.all()
    
    def resolve_cliente(self, info,id):
        return Cliente.objects.get(pk=id)
    