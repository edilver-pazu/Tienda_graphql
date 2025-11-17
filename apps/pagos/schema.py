import graphene
from graphene_django import DjangoObjectType
from .models import Pago
from decimal import Decimal

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
    
class CrearPago(graphene.Mutation):
    class Arguments:
        pedido_id = graphene.ID(required=True)
        monto = graphene.Float(required=True)
        metodo_pago = graphene.String(required=True)
        nota = graphene.String()

    pago = graphene.Field(PagoType)

    def mutate(self, info, pedido_id, monto, metodo_pago, nota=None):
        from apps.pedidos.models import Pedido

        try:
            pedido = Pedido.objects.get(pk=pedido_id)
        except Pedido.DoesNotExist:
            raise Exception("Pedido no encontrado")

        if monto <= 0:
            raise Exception("El monto debe ser mayor a 0")

        # Total pagado hasta ahora
        pagado = sum(p.monto for p in pedido.pagos.all())
        pendiente = pedido.total - pagado

        if monto > pendiente:
            raise Exception("El pago excede el total pendiente del pedido")

        # Estado basado en monto
        if monto == pendiente:
            estado = "succeeded"
        else:
            estado = "pending"  # Abono parcial

        monto = Decimal(str(monto))

        pago = Pago.objects.create(
            pedido=pedido,
            monto=monto,
            metodo_pago=metodo_pago,
            estado_pago=estado,
            nota=nota
        )

        return CrearPago(pago=pago)

class ActualizarPago(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        monto = graphene.Float()
        metodo_pago = graphene.String()
        nota = graphene.String()

    pago = graphene.Field(PagoType)

    def mutate(self, info, id, **data):
        try:
            pago = Pago.objects.get(pk=id)
        except Pago.DoesNotExist:
            raise Exception("Pago no encontrado")

        if pago.estado_pago in ["refunded", "failed"]:
            raise Exception("No se puede modificar un pago fallido o reembolsado.")

        # Validar nuevo monto si se pasa
        if "monto" in data:
            new_monto = data["monto"]
            if new_monto <= 0:
                raise Exception("El monto debe ser mayor a 0")

            pedido = pago.pedido

            pagado_sin_este = sum(p.monto for p in pedido.pagos.exclude(pk=pago.id))
            pendiente = pedido.total - pagado_sin_este

            if new_monto > pendiente:
                raise Exception("El nuevo monto excede el total pendiente")

        for key, value in data.items():
            setattr(pago, key, value)

        pago.save()
        return ActualizarPago(pago=pago)

class CambiarEstadoPago(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        estado_pago = graphene.String(required=True)

    pago = graphene.Field(PagoType)

    def mutate(self, info, id, estado_pago):
        try:
            pago = Pago.objects.get(pk=id)
        except Pago.DoesNotExist:
            raise Exception("Pago no encontrado")

        if estado_pago not in dict(Pago.ESTADO_CHOICES):
            raise Exception("Estado de pago no válido")

        # Regla: no puede cambiarse si ya está reembolsado
        if pago.estado_pago == "refunded":
            raise Exception("No se puede modificar un pago reembolsado")

        pago.estado_pago = estado_pago
        pago.save()
        return CambiarEstadoPago(pago=pago)

class EliminarPago(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            pago = Pago.objects.get(pk=id)
        except Pago.DoesNotExist:
            raise Exception("Pago no encontrado")

        if pago.estado_pago == "succeeded":
            raise Exception("No se puede eliminar un pago exitoso (solo reembolso)")

        pago.delete()
        return EliminarPago(ok=True)

class Mutation(graphene.ObjectType):
    crear_pago = CrearPago.Field()
    actualizar_pago = ActualizarPago.Field()
    cambiar_estado_pago = CambiarEstadoPago.Field()
    eliminar_pago = EliminarPago.Field()
