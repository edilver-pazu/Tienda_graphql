import graphene
from graphene_django import DjangoObjectType
from .models import Producto, Categoria, ProductoCategoria

class ProductoType(DjangoObjectType):
    class Meta:
        model = Producto
        fields = "__all__"

class CategoriaType(DjangoObjectType):
    class Meta:
        model = Categoria
        fields = "__all__"

class ProductoCategoriaType(DjangoObjectType):
    class Meta:
        model = ProductoCategoria
        fields = "__all__"

class Query(graphene.ObjectType):
    productos = graphene.List(ProductoType)
    producto = graphene.Field(ProductoType, id=graphene.ID())

    categorias = graphene.List(CategoriaType)
    categoria = graphene.Field(CategoriaType, id=graphene.ID())

    def resolve_productos(self, info):
        return Producto.objects.all()
    
    def resolve_producto(self, info, id):
        return Producto.objects.get(pk=id)

    def resolve_categorias(self, info):
        return Categoria.objects.all()
    
    def resolve_categoria(self, info, id):
        return Categoria.objects.get(pk=id)
