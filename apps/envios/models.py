from django.db import models
from apps.pedidos.models import Pedido

class Envio(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_transit', 'En tránsito'),
        ('delivered', 'Entregado'),
        ('failed', 'Fallo entrega'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='envio')
    direccion_envio = models.CharField(max_length=300)
    estado_envio = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')
    transportador = models.CharField(max_length=200, blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Envio Pedido #{self.pedido.id} - {self.estado_envio}"
