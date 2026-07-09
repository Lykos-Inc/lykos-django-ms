from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Pessoa, Endereco

class PessoaInline(admin.StackedInline):
    model = Pessoa
    can_delete = False
    verbose_name_plural = 'Pessoa (Dados Pessoais)'

class EnderecoInline(admin.StackedInline):
    model = Endereco
    extra = 0

class UsuarioAdmin(UserAdmin):
    # Configurações para usar o modelo de usuário personalizado
    model = Usuario
    list_display = ('email', 'nome_usuario', 'is_buyer', 'is_seller', 'status', 'is_staff')
    list_filter = ('is_buyer', 'is_seller', 'status', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'senha_hash')}),
        ('Informações Pessoais', {'fields': ('nome_usuario', 'avatar_url')}),
        ('Papéis', {'fields': ('is_buyer', 'is_seller')}),
        ('Status', {'fields': ('status', 'is_active', 'is_staff', 'is_superuser')}),
        ('Datas', {'fields': ('data_criacao', 'data_atualizacao')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome_usuario', 'senha_hash', 'is_buyer', 'is_seller'),
        }),
    )
    search_fields = ('email', 'nome_usuario')
    ordering = ('email',)
    inlines = [PessoaInline, EnderecoInline]

# Remove o filtro padrão de grupos se não for usar
admin.site.register(Usuario, UsuarioAdmin)
# Se quiser registrar separadamente:
# admin.site.register(Pessoa)
# admin.site.register(Endereco)