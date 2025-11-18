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


class CrearEnvio(graphene.Mutation):
    class Arguments:
        pedido_id = graphene.ID(required=True)
        direccion_envio = graphene.String(required=True)
        transportador = graphene.String()
        costo_envio = graphene.Float()

    envio = graphene.Field(EnvioType)

    def mutate(self, info, pedido_id, direccion_envio, transportador=None, costo_envio=None):
        from apps.pedidos.models import Pedido

        try:
            pedido = Pedido.objects.get(pk=pedido_id)
        except Pedido.DoesNotExist:
            raise Exception("Pedido no encontrado")

        if hasattr(pedido, "envio"):
            raise Exception("Este pedido ya tiene un envío asignado")

        if pedido.estado == "canceled":
            raise Exception("No se puede crear envío para un pedido cancelado")

        envio = Envio.objects.create(
            pedido=pedido,
            direccion_envio=direccion_envio,
            transportador=transportador,
            costo_envio=costo_envio
        )

        return CrearEnvio(envio=envio)

class ActualizarEnvio(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        direccion_envio = graphene.String()
        transportador = graphene.String()
        costo_envio = graphene.Float()

    envio = graphene.Field(EnvioType)

    def mutate(self, info, id, **data):
        try:
            envio = Envio.objects.get(pk=id)
        except Envio.DoesNotExist:
            raise Exception("Envio no encontrado")

        for field, value in data.items():
            setattr(envio, field, value)

        envio.save()
        return ActualizarEnvio(envio=envio)

from django.utils import timezone

class CambiarEstadoEnvio(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        estado_envio = graphene.String(required=True)

    envio = graphene.Field(EnvioType)

    def mutate(self, info, id, estado_envio):
        try:
            envio = Envio.objects.get(pk=id)
        except Envio.DoesNotExist:
            raise Exception("Envio no encontrado")

        if estado_envio not in dict(Envio.ESTADO_CHOICES):
            raise Exception("Estado de envío no válido")

        envio.estado_envio = estado_envio

        # lógica automática
        if estado_envio == "in_transit" and envio.fecha_envio is None:
            envio.fecha_envio = timezone.now()

        if estado_envio == "delivered" and envio.fecha_entrega is None:
            envio.fecha_entrega = timezone.now()

        envio.save()
        return CambiarEstadoEnvio(envio=envio)

class EliminarEnvio(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            envio = Envio.objects.get(pk=id)
        except Envio.DoesNotExist:
            raise Exception("Envio no encontrado")

        # solo permitir borrar si no ha sido enviado
        if envio.estado_envio in ["in_transit", "delivered"]:
            raise Exception("No puedes eliminar un envío ya en tránsito o entregado.")

        envio.delete()
        return EliminarEnvio(ok=True)

class Mutation(graphene.ObjectType):
    crear_envio = CrearEnvio.Field()
    actualizar_envio = ActualizarEnvio.Field()
    cambiar_estado_envio = CambiarEstadoEnvio.Field()
    eliminar_envio = EliminarEnvio.Field()
