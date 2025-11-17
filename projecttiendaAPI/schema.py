import graphene
from apps.productos.schema import Query as ProductosQuery
from apps.pedidos.schema import Query as PedidosQuery
from apps.pagos.schema import Query as PagosQuery
from apps.envios.schema import Query as EnviosQuery
from apps.clientes.schema import Query as ClientesQuery

class Query(
    ProductosQuery,
    PedidosQuery,
    PagosQuery,
    EnviosQuery,
    ClientesQuery,
    graphene.ObjectType,
):
    pass

schema = graphene.Schema(query=Query)
