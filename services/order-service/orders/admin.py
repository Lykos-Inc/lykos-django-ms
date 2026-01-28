from django.contrib import admin
from .models import Order, Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'amount', 'client_id', 'freelancer_id', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'order', 'status', 'created_at')