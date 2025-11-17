from django.db import models
from decimal import Decimal

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)  # activo / inactivo
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    cantidad_disponible = models.IntegerField(default=0)
    estado = models.BooleanField(default=True)  # True = activo
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    imagen_url = models.URLField(blank=True, null=True)

    categorias = models.ManyToManyField(
        Categoria,
        through='ProductoCategoria',
        related_name='productos'
    )

    def __str__(self):
        return self.nombre

class ProductoCategoria(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'categoria')

    def __str__(self):
        return f"{self.producto} — {self.categoria}"
