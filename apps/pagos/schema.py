import graphene
from graphene_django import DjangoObjectType
from .models import Pago

class PagoType(DjangoObjectType):
    class Meta:
        model = Pago
        fields = "__all__"

class Query(graphene.ObjectType):
    pagos = graphene.List(PagoType)

    def resolve_pagos(self, info):
        return Pago.objects.all()
    