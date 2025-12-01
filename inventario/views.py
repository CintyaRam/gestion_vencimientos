from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import Group
from .models import Articulo, Lote, Departamento
from datetime import date, timedelta
from .forms import ArticuloForm, LoteForm
from django.db.models import Min
from django.db import connection


def es_admin(user):
    return user.groups.filter(name='Administradores').exists()


def obtener_resumen_lotes_por_departamento():
    """
    Consulta SQL compatible con SQLite y PostgreSQL
    """
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

        context['lotes_vencidos'] = Lote.objects.filter(
            activo=True, fecha_vencimiento__lte=hoy
        ).order_by('fecha_vencimiento')

        context['lotes_alerta'] = Lote.objects.filter(
            activo=True,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite_amarillo
        ).order_by('fecha_vencimiento')

        context['resumen_sql_departamentos'] = obtener_resumen_lotes_por_departamento()

        context['es_administrador'] = es_admin(self.request.user) if self.request.user.is_authenticated else False

        return context


class ListaArticulosView(LoginRequiredMixin, ListView):
    model = Articulo
    template_name = 'lista_articulos.html'
    context_object_name = 'articulos_ordenados'

    def get_queryset(self):
        qs = Articulo.objects.filter(activo=True).prefetch_related('lotes')

        departamento_filtro = self.request.GET.get('departamento')
        if departamento_filtro:
            qs = qs.filter(departamento__numero_departamento=departamento_filtro)

        estado_filtro = self.request.GET.get('estado')
        if estado_filtro:
            articulos_filtrados = []
            for articulo in qs:
                for lote in articulo.lotes.filter(activo=True):
                    if lote.estado_vencimiento() == estado_filtro:
                        articulos_filtrados.append(articulo)
                        break
            qs = articulos_filtrados

        articulos_con_fecha_proxima = []
        for articulo in qs:
            proximo_vto = articulo.lotes.filter(activo=True).aggregate(
                Min('fecha_vencimiento')
            )['fecha_vencimiento__min']
            articulos_con_fecha_proxima.append((articulo, proximo_vto))

        articulos_con_fecha_proxima.sort(
            key=lambda x: x[1] if x[1] else date.max
        )

        return [x[0] for x in articulos_con_fecha_proxima]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['lotes_vencidos'] = Lote.objects.filter(
            activo=True,
            fecha_vencimiento__lte=date.today()
        ).order_by('fecha_vencimiento')

        context['es_administrador'] = es_admin(self.request.user)
        context['departamentos'] = Departamento.objects.all()
        context['departamento_seleccionado'] = self.request.GET.get('departamento', '')

        context['estados'] = [
            'Vencido - Quitar de Sala inmediatamente',
            'Por vencer (tomar acción correctiva)',
            'Cerca de vencimiento',
            'Buen estado',
        ]
        context['estado_seleccionado'] = self.request.GET.get('estado', '')

        return context


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
