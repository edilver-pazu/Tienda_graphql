from django.db import models
from decimal import Decimal
from apps.clientes.models import Cliente
from apps.productos.models import Producto

# Create your models here.

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_delivery', 'En entrega'),
        ('delivered', 'Entregado'),
        ('canceled', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    metodo_entrega = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'domicilio' / 'retiro'
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre} - {self.estado}"

    def recalcular_total(self):
        """Recalcula y actualiza el total según los detalles del pedido."""
        total = Decimal('0.00')
        for item in self.detalles.all():
            total += item.subtotal
        self.total = total
        self.save(update_fields=['total'])

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # precio al momento del pedido
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Pedido #{self.pedido.id})"

    def save(self, *args, **kwargs):
        # Mantener subtotal consistente
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
        # Actualizar total del pedido
        self.pedido.recalcular_total()

