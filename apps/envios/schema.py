import graphene
from graphene_django import DjangoObjectType
from .models import Envio

class EnvioType(DjangoObjectType):
    class Meta:
        model = Envio
        fields = "__all__"

class Query(graphene.ObjectType):
    envios = graphene.List(EnvioType)
    envio = graphene.Field(EnvioType, id=graphene.ID())

    def resolve_envios(self, info):
        return Envio.objects.all()
    
    def resolve_envio(self, info, id):
        return Envio.objects.get(pk=id)
    