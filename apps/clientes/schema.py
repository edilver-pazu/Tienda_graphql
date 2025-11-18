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
    

class CreateCliente(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        correo = graphene.String(required=True)
        telefono = graphene.String()
        direccion = graphene.String()

    cliente = graphene.Field(ClienteType)

    def mutate(self, info, nombre, correo, telefono=None, direccion=None):
        cliente = Cliente.objects.create(
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            direccion=direccion
        )
        return CreateCliente(cliente=cliente)
    
class UpdateCliente(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        nombre = graphene.String()
        correo = graphene.String()
        telefono = graphene.String()
        direccion = graphene.String()

    cliente = graphene.Field(ClienteType)

    def mutate(self, info, id, nombre=None, correo=None, telefono=None, direccion=None):
        cliente = Cliente.objects.get(pk=id)

        if nombre is not None:
            cliente.nombre = nombre
        if correo is not None:
            cliente.correo = correo
        if telefono is not None:
            cliente.telefono = telefono
        if direccion is not None:
            cliente.direccion = direccion

        cliente.save()
        return UpdateCliente(cliente=cliente)

class DeleteCliente(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        cliente = Cliente.objects.get(pk=id)
        cliente.delete()
        return DeleteCliente(ok=True)

class Mutation(graphene.ObjectType):
    crear_cliente = CreateCliente.Field()
    actualizar_cliente = UpdateCliente.Field()
    eliminar_cliente = DeleteCliente.Field()

