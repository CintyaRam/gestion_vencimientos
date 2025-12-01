from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect
from django.db.models import Min
from django.db import connection
from datetime import date, timedelta

from .models import Articulo, Lote, Departamento
from .forms import ArticuloForm, LoteForm


# ==========================================
#  PERMISOS
# ==========================================

def es_admin(user):
    """
    Un usuario será considerado administrador si:
    - Es superusuario, o
    - Pertenece al grupo 'Administradores'.
    """
    return user.is_superuser or user.groups.filter(name='Administradores').exists()


# ==========================================
#  CONSULTA SQL RESUMEN
# ==========================================

def obtener_resumen_lotes_por_departamento():
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d.numero_departamento,
                    COUNT(*) AS total_lotes_activos,
                    SUM(CASE WHEN l.fecha_vencimiento <= CURRENT_DATE THEN 1 ELSE 0 END) AS total_lotes_vencidos
                FROM inventario_lote l
                INNER JOIN inventario_articulo a ON l.articulo_id = a.id
                INNER JOIN inventario_departamento d ON a.departamento_id = d.numero_departamento
                WHERE l.activo = 1
                GROUP BY d.numero_departamento
                ORDER BY d.numero_departamento;
            """)
            columnas = [col[0] for col in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    except Exception:
        return []


# ==========================================
#  HOME
# ==========================================

class HomeView(ListView):
    model = Lote
    template_name = 'home.html'
    context_object_name = 'lotes_proximos'

    def get_queryset(self):
        return Lote.objects.filter(activo=True).order_by('fecha_vencimiento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoy = date.today()
        limite_amarillo = hoy + timedelta(days=7)

        context["lotes_vencidos"] = Lote.objects.filter(
            activo=True, fecha_vencimiento__lte=hoy
        ).order_by('fecha_vencimiento')

        context["lotes_alerta"] = Lote.objects.filter(
            activo=True,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite_amarillo
        ).order_by('fecha_vencimiento')

        context["resumen_sql_departamentos"] = obtener_resumen_lotes_por_departamento()

        context["es_administrador"] = es_admin(self.request.user)

        return context


# ==========================================
#  LISTA ARTÍCULOS
# ==========================================

class ListaArticulosView(LoginRequiredMixin, ListView):
    model = Articulo
    template_name = 'lista_articulos.html'
    context_object_name = 'articulos_ordenados'

    def get_queryset(self):
        qs = Articulo.objects.filter(activo=True).prefetch_related('lotes')

        # Filtro por departamento
        departamento_filtro = self.request.GET.get('departamento')
        if departamento_filtro:
            qs = qs.filter(departamento__numero_departamento=departamento_filtro)

        # Filtro por estado
        estado_filtro = self.request.GET.get('estado')
        if estado_filtro:
            articulos_filtrados = []
            for articulo in qs:
                for lote in articulo.lotes.filter(activo=True):
                    if lote.estado_vencimiento() == estado_filtro:
                        articulos_filtrados.append(articulo)
                        break
            qs = articulos_filtrados

        # Ordenar por fecha de vencimiento más próxima
        articulos_con_fecha = []
        for articulo in qs:
            fecha_min = articulo.lotes.filter(activo=True).aggregate(
                Min('fecha_vencimiento')
            )['fecha_vencimiento__min']
            articulos_con_fecha.append((articulo, fecha_min))

        articulos_con_fecha.sort(key=lambda x: x[1] if x[1] else date.max)

        return [a[0] for a in articulos_con_fecha]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["lotes_vencidos"] = Lote.objects.filter(
            activo=True,
            fecha_vencimiento__lte=date.today()
        ).order_by('fecha_vencimiento')

        context["es_administrador"] = es_admin(self.request.user)
        context["departamentos"] = Departamento.objects.all()
        context["departamento_seleccionado"] = self.request.GET.get('departamento', '')

        context["estados"] = [
            'Vencido - Quitar de Sala inmediatamente',
            'Por vencer (tomar acción correctiva)',
            'Cerca de vencimiento',
            'Buen estado',
        ]

        context["estado_seleccionado"] = self.request.GET.get('estado', '')

        return context


# ==========================================
#  CRUD LOTE
# ==========================================

class CrearLoteView(LoginRequiredMixin, CreateView):
    model = Lote
    form_class = LoteForm
    template_name = 'crear_lote.html'
    success_url = reverse_lazy('lista_articulos')

    def form_valid(self, form):
        form.instance.responsable_registro = self.request.user
        return super().form_valid(form)


class EditarLoteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Lote
    form_class = LoteForm
    template_name = 'editar_lote.html'
    success_url = reverse_lazy('lista_articulos')

    def test_func(self):
        lote = self.get_object()
        return es_admin(self.request.user) or lote.responsable_registro == self.request.user


class EliminarLoteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Lote
    template_name = 'eliminar_lote.html'
    success_url = reverse_lazy('lista_articulos')

    def test_func(self):
        lote = self.get_object()
        return es_admin(self.request.user) or lote.responsable_registro == self.request.user

    def delete(self, request, *args, **kwargs):
        lote = self.get_object()
        lote.activo = False
        lote.save()
        return HttpResponseRedirect(self.success_url)


# ==========================================
#  CRUD ARTÍCULO
# ==========================================

class CrearArticuloView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'crear_articulo.html'
    success_url = reverse_lazy('lista_articulos')

    def test_func(self):
        return es_admin(self.request.user)


class EditarArticuloView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'editar_articulo.html'
    success_url = reverse_lazy('lista_articulos')

    def test_func(self):
        return es_admin(self.request.user)


class EliminarArticuloView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Articulo
    template_name = 'eliminar_articulo.html'
    success_url = reverse_lazy('lista_articulos')

    def test_func(self):
        return es_admin(self.request.user)

    def delete(self, request, *args, **kwargs):
        articulo = self.get_object()
        articulo.activo = False
        articulo.save()
        articulo.lotes.update(activo=False)
        return HttpResponseRedirect(self.success_url)
