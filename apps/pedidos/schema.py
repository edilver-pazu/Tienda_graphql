import graphene
from graphene_django import DjangoObjectType
from .models import Pedido, DetallePedido
from apps.productos.models import Producto


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


class CrearPedido(graphene.Mutation):
    class Arguments:
        cliente_id = graphene.ID(required=True)
        metodo_entrega = graphene.String()
        notas = graphene.String()

    pedido = graphene.Field(PedidoType)

    def mutate(self, info, cliente_id, metodo_entrega=None, notas=None):
        pedido = Pedido.objects.create(
            cliente_id=cliente_id,
            metodo_entrega=metodo_entrega,
            notas=notas
        )
        return CrearPedido(pedido=pedido)

class ActualizarPedido(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        metodo_entrega = graphene.String()
        notas = graphene.String()

    pedido = graphene.Field(PedidoType)

    def mutate(self, info, id, **data):
        try:
            pedido = Pedido.objects.get(pk=id)
        except Pedido.DoesNotExist:
            raise Exception("Pedido no encontrado")

        for key, value in data.items():
            setattr(pedido, key, value)

        pedido.save()
        return ActualizarPedido(pedido=pedido)

class CambiarEstadoPedido(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        estado = graphene.String(required=True)

    pedido = graphene.Field(PedidoType)

    def mutate(self, info, id, estado):
        try:
            pedido = Pedido.objects.get(pk=id)
        except Pedido.DoesNotExist:
            raise Exception("Pedido no encontrado")

        if estado not in dict(Pedido.ESTADO_CHOICES):
            raise Exception("Estado inválido")

        pedido.estado = estado
        pedido.save()

        return CambiarEstadoPedido(pedido=pedido)

class EliminarPedido(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            pedido = Pedido.objects.get(pk=id)
        except Pedido.DoesNotExist:
            raise Exception("Pedido no encontrado")

        # Evitar borrar pedidos entregados
        if pedido.estado == "delivered":
            raise Exception("No puedes eliminar un pedido ya entregado")

        pedido.delete()
        return EliminarPedido(ok=True)

#----------------------------------
class AgregarDetallePedido(graphene.Mutation):
    class Arguments:
        pedido_id = graphene.ID(required=True)
        producto_id = graphene.ID(required=True)
        cantidad = graphene.Int(required=True)

    detalle = graphene.Field(DetallePedidoType)
    pedido = graphene.Field(PedidoType)

    def mutate(self, info, pedido_id, producto_id, cantidad):
        try:
            pedido = Pedido.objects.get(pk=pedido_id)
        except Pedido.DoesNotExist:
            raise Exception("Pedido no encontrado")

        try:
            producto = Producto.objects.get(pk=producto_id)
        except Producto.DoesNotExist:
            raise Exception("Producto no encontrado")

        if cantidad <= 0:
            raise Exception("La cantidad debe ser mayor a 0")

        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=producto.precio * cantidad
        )

        # actualizar total automáticamente por save()
        return AgregarDetallePedido(detalle=detalle, pedido=pedido)

class ActualizarDetallePedido(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        cantidad = graphene.Int(required=True)

    detalle = graphene.Field(DetallePedidoType)
    pedido = graphene.Field(PedidoType)

    def mutate(self, info, id, cantidad):
        try:
            detalle = DetallePedido.objects.get(pk=id)
        except DetallePedido.DoesNotExist:
            raise Exception("Detalle no encontrado")

        if cantidad <= 0:
            raise Exception("La cantidad debe ser mayor a 0")

        detalle.cantidad = cantidad
        detalle.save()  # recalcula subtotal y total pedido

        return ActualizarDetallePedido(detalle=detalle, pedido=detalle.pedido)

class EliminarDetallePedido(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    pedido = graphene.Field(PedidoType)

    def mutate(self, info, id):
        try:
            detalle = DetallePedido.objects.get(pk=id)
        except DetallePedido.DoesNotExist:
            raise Exception("Detalle no encontrado")

        pedido = detalle.pedido
        detalle.delete()
        pedido.recalcular_total()

        return EliminarDetallePedido(ok=True, pedido=pedido)

#-----------MUTACIONES--------------
class Mutation(graphene.ObjectType):
    # Pedido
    crear_pedido = CrearPedido.Field()
    actualizar_pedido = ActualizarPedido.Field()
    cambiar_estado_pedido = CambiarEstadoPedido.Field()
    eliminar_pedido = EliminarPedido.Field()

    # Detalles
    agregar_detalle_pedido = AgregarDetallePedido.Field()
    actualizar_detalle_pedido = ActualizarDetallePedido.Field()
    eliminar_detalle_pedido = EliminarDetallePedido.Field()
