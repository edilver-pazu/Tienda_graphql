import graphene
from graphene_django import DjangoObjectType
from .models import Pedido, DetallePedido

class PedidoType(DjangoObjectType):
    class Meta:
        model = Pedido
        fields = "__all__"

class DetallePedidoType(DjangoObjectType):
    class Meta:
        model = DetallePedido
        fields = "__all__"

class Query(graphene.ObjectType):
    pedidos = graphene.List(PedidoType)
    pedido = graphene.Field(PedidoType, id=graphene.ID())

    def resolve_pedidos(self, info):
        return Pedido.objects.all()
    
    def resolve_pedido(self, info, id):
        return Pedido.objects.get(pk=id)
    