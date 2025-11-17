import graphene
from decimal import Decimal
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


# ----------------------------
# Mutations: CRUD Producto
# ----------------------------
class CrearProducto(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        descripcion = graphene.String()
        precio = graphene.Float(required=True)
        cantidad_disponible = graphene.Int(required=True)
        estado = graphene.Boolean()
        imagen_url = graphene.String()
        categorias = graphene.List(graphene.ID)  # lista de IDs de categoria

    producto = graphene.Field(ProductoType)

    def mutate(self, info, nombre, precio, cantidad_disponible, descripcion=None,
               estado=True, imagen_url=None, categorias=None):

        # convertir precio a Decimal para el campo DecimalField
        precio_dec = Decimal(str(precio))

        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio_dec,
            cantidad_disponible=cantidad_disponible,
            estado=estado,
            imagen_url=imagen_url
        )

        # asociar categorias (si se pasan)
        if categorias:
            for cat_id in categorias:
                # crea la relación; si ya existe unique_together evita duplicados
                ProductoCategoria.objects.get_or_create(
                    producto=producto,
                    categoria_id=cat_id
                )

        return CrearProducto(producto=producto)

# ---- Actualizar Producto ----
class ActualizarProducto(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        nombre = graphene.String()
        descripcion = graphene.String()
        precio = graphene.Float()
        cantidad_disponible = graphene.Int()
        estado = graphene.Boolean()
        imagen_url = graphene.String()
        categorias = graphene.List(graphene.ID)  # si se entrega, reemplaza las categorías

    producto = graphene.Field(ProductoType)

    def mutate(self, info, id, categorias=None, **datos):
        try:
            producto = Producto.objects.get(pk=id)
        except Producto.DoesNotExist:
            raise Exception("Producto no encontrado")

        # Si viene precio convertir a Decimal
        if "precio" in datos and datos["precio"] is not None:
            datos["precio"] = Decimal(str(datos["precio"]))

        # Actualizar campos dinámicamente
        for key, value in datos.items():
            setattr(producto, key, value)
        producto.save()

        # Si se pasaron categorias, reemplazamos las relaciones
        if categorias is not None:
            # eliminar relaciones anteriores
            ProductoCategoria.objects.filter(producto=producto).delete()
            for cat_id in categorias:
                ProductoCategoria.objects.create(producto=producto, categoria_id=cat_id)

        return ActualizarProducto(producto=producto)


# ---- Eliminar Producto ----
class EliminarProducto(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    producto_id = graphene.ID()

    def mutate(self, info, id):
        try:
            producto = Producto.objects.get(pk=id)
        except Producto.DoesNotExist:
            raise Exception("Producto no encontrado")

        producto_id = producto.id
        producto.delete()
        return EliminarProducto(ok=True, producto_id=producto_id)
    
# ----------------------------
# Mutations: CRUD Categoria
# ----------------------------
class CrearCategoria(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        descripcion = graphene.String()
        estado = graphene.Boolean()

    categoria = graphene.Field(CategoriaType)

    def mutate(self, info, nombre, descripcion=None, estado=True):
        # Validar nombre único
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise Exception("Ya existe una categoría con ese nombre")

        categoria = Categoria.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            estado=estado
        )
        return CrearCategoria(categoria=categoria)

class ActualizarCategoria(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        nombre = graphene.String()
        descripcion = graphene.String()
        estado = graphene.Boolean()

    categoria = graphene.Field(CategoriaType)

    def mutate(self, info, id, **datos):
        try:
            categoria = Categoria.objects.get(pk=id)
        except Categoria.DoesNotExist:
            raise Exception("Categoría no encontrada")

        # Validar nombre único si viene nombre nuevo
        if "nombre" in datos and datos["nombre"]:
            nuevo_nombre = datos["nombre"]
            if Categoria.objects.filter(nombre__iexact=nuevo_nombre).exclude(pk=id).exists():
                raise Exception("Ya existe otra categoría con ese nombre")

        # Actualizar valores dinámicamente
        for key, value in datos.items():
            setattr(categoria, key, value)

        categoria.save()
        return ActualizarCategoria(categoria=categoria)

class EliminarCategoria(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    categoria_id = graphene.ID()

    def mutate(self, info, id):
        try:
            categoria = Categoria.objects.get(pk=id)
        except Categoria.DoesNotExist:
            raise Exception("Categoría no encontrada")

        categoria_id = categoria.id
        categoria.delete()
        return EliminarCategoria(ok=True, categoria_id=categoria_id)
    
# ----------------------------
# Registrar Mutations
# ----------------------------
class Mutation(graphene.ObjectType):
    # producto
    crear_producto = CrearProducto.Field()
    actualizar_producto = ActualizarProducto.Field()
    eliminar_producto = EliminarProducto.Field()

    # Categoria
    crear_categoria = CrearCategoria.Field()
    actualizar_categoria = ActualizarCategoria.Field()
    eliminar_categoria = EliminarCategoria.Field()
