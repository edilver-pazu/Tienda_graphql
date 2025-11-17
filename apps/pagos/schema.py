import graphene
from graphene_django import DjangoObjectType
from .models import Pago

class PagoType(DjangoObjectType):
    class Meta:
        model = Pago
        fields = "__all__"

class Query(graphene.ObjectType):
    pagos = graphene.List(PagoType)
    pago = graphene.Field(PagoType, id=graphene.ID())

    def resolve_pagos(self, info):
        return Pago.objects.all()
    
    def resolve_pago(self, info, id):
        return Pago.objects.get(pk=id)
    