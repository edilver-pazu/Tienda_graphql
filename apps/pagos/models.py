from django.db import models
from decimal import Decimal
from apps.pedidos.models import Pedido

class Pago(models.Model):
    METODO_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('bank_transfer', 'Transferencia'),
        ('qr', 'QR'),
    ]

    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('succeeded', 'Exitoso'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    metodo_pago = models.CharField(max_length=30, choices=METODO_CHOICES, default='cash')
    estado_pago = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    transaccion_id = models.CharField(max_length=255, blank=True, null=True)  # id del proveedor si aplica
    nota = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago #{self.id} - Pedido #{self.pedido.id} - {self.monto} ({self.estado_pago})"