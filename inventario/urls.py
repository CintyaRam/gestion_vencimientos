from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('articulos/', views.ListaArticulosView.as_view(), name='lista_articulos'),
    path('articulo/crear/', views.CrearArticuloView.as_view(), name='crear_articulo'),
    path('articulo/<int:pk>/editar/', views.EditarArticuloView.as_view(), name='editar_articulo'),
    path('articulo/<int:pk>/eliminar/', views.EliminarArticuloView.as_view(), name='eliminar_articulo'),
    path('lote/crear/', views.CrearLoteView.as_view(), name='crear_lote'),
    path('lote/<int:pk>/editar/', views.EditarLoteView.as_view(), name='editar_lote'),
    path('lote/<int:pk>/eliminar/', views.EliminarLoteView.as_view(), name='eliminar_lote'),
]