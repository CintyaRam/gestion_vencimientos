# 🛒 Sistema de Gestión de Vencimientos — Django

Aplicación web desarrollada en **Django 5**, diseñada para gestionar artículos y sus lotes, mostrando alertas sobre productos **vencidos**, **por vencer** o **en buen estado**, con control de acceso por usuarios y administración avanzada.

---

## 📂 Estructura del Proyecto

| Carpeta/Archivo | Descripción |
|------------------|-------------|
| **gestion_vencimientos/** | Configuración principal del proyecto Django |
| ├── `settings.py` | Configuración global: apps, BD, estáticos, templates |
| ├── `urls.py` | Rutas principales del proyecto |
| ├── `wsgi.py` / `asgi.py` | Configuración de despliegue |
| **inventario/** | Aplicación principal del sistema |
| ├── `models.py` | Modelos: Artículo, Lote, Departamento |
| ├── `views.py` | Vistas basadas en clases (ListView, CreateView, etc.) |
| ├── `forms.py` | Formularios de Lote y Artículo |
| ├── `urls.py` | Rutas específicas de la app |
| ├── `admin.py` | Configuración avanzada del panel de administración |
| ├── **templatetags/** | Filtro personalizado para permisos de grupo |
| ├── **templates/** | Plantillas HTML (base, home, CRUD, login, etc.) |
| **static/** | CSS y JavaScript |
| ├── `css/estilos.css` | Estilos personalizados |
| ├── `js/script.js` | Lógica del modal de vencidos |
| **requirements.txt** | Dependencias del proyecto |
| **.gitignore** | Archivos ignorados por Git |
| **manage.py** | Script de administración Django |

---

## 🚀 Funcionalidades del Sistema

### ✔️ Gestión de Artículos
- Crear, editar y eliminar artículos (solo administradores).
- Asignación de departamento.
- Borrado lógico (`activo = False`).

### ✔️ Gestión de Lotes
- Crear, editar y eliminar lotes.
- Control por permisos: dueño del lote o admin.
- Datos del lote:
  - Número de lote  
  - Fecha de vencimiento  
  - Estado calculado automáticamente  
  - Responsable del registro  
  - Borrado lógico  

### ✔️ Estados por semáforo
Clasificación automática:

| Estado | Condición |
|--------|-----------|
| **Vencido** | `fecha_vencimiento < hoy` |
| **Por vencer** | `<= 2 días` |
| **Cerca de vencimiento** | `<= 7 días` |
| **Buen estado** | Mayor a 7 días |

Colores en rojo, naranja y verde.

### ✔️ Modal Automático de Lotes Vencidos
- Se muestra en `home` y `lista_articulos`.
- Basado en Bootstrap 5.
- Solo aparece si realmente existen lotes vencidos.

### ✔️ Control de Acceso
- Sistema de login y logout.
- Grupo **Administradores**.
- Filtro personalizado `has_group` disponible en templates.

### ✔️ Panel de Administración Django Mejorado
Incluye:
- `list_display`
- `search_fields`
- `list_filter` (incluye estado del lote por vencimiento)
- Separación por modelos

---

## 🧠 Lógica de Vencimientos

```python
@property
def estado_vencimiento(self):
    hoy = date.today()
    if self.fecha_vencimiento < hoy:
        return "Vencido - Quitar de Sala inmediatamente"
    elif self.fecha_vencimiento <= hoy + timedelta(days=2):
        return "Por vencer (tomar acción correctiva)"
    elif self.fecha_vencimiento <= hoy + timedelta(days=7):
        return "Cerca de vencimiento"
    return "Buen estado"
```

## 🛠️ Instalación y Ejecución

### 1. Clonar repositorio

``` bash
git clone https://github.com/usuario/gestion_vencimientos.git
cd gestion_vencimientos
```


### 2. Crear entorno virtual

``` bash
python -m venv venv
```


### 3. Activar entorno virtual

Windows:
```bash
venv\Scripts\activate
```

Linux / MacOS:
``` bash
source venv/bin/activate
```


### 4. Instalar dependencias

``` bash
pip install -r requirements.txt
```


### 5. Aplicar migraciones

``` bash
python manage.py migrate
```


### 6. Crear superusuario (opcional)

``` bash
python manage.py createsuperuser
```


### 7. Ejecutar servidor

``` bash
python manage.py runserver
```

Luego abrir en el navegador:

```
http://127.0.0.1:8000/
```
## 🧪 Consultas SQL con `connection.cursor()` 

Este proyecto incluye consultas SQL directas usando `connection.cursor()`, cumpliendo el requisito de la rúbrica.

Ejemplo implementado para obtener lotes por departamento:

``` python
from django.db import connection

def lotes_por_departamento():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT d.numero_departamento, a.nombre, l.numero_lote, l.fecha_vencimiento
            FROM inventario_lote l
            JOIN inventario_articulo a ON l.articulo_id = a.id
            JOIN inventario_departamento d ON a.departamento_id = d.id
            WHERE l.activo = 1
            ORDER BY d.numero_departamento ASC;
        """)
        return cursor.fetchall()
```

---

## 🔍 Filtros dinámicos aplicados (Rúbrica Punto 2)

El sistema permite filtrar datos según distintos criterios:

### ✔ Filtro por Departamento  
El usuario puede ver los artículos agrupados o filtrados según el número de departamento al que pertenecen.

### ✔ Filtro por Estado del Lote  
Los artículos pueden clasificarse y mostrarse de acuerdo al estado del vencimiento:

- *Buen estado*
- *Cerca de vencimiento*
- *Por vencer*
- *Vencido*

Estos estados se generan dinámicamente desde el método `estado_vencimiento()` del modelo.

### ✔ Ordenamiento por fecha de vencimiento más cercana  
Cada artículo muestra primero el lote cuya fecha de vencimiento está más próxima.

---

## 🧠 Manejo de Datos Relacionados (Rúbrica Punto 3)

Este proyecto implementa relaciones entre múltiples modelos de manera eficiente:

### ✔ Relaciones principales
- **Departamento 1 → M Artículos**
- **Artículo 1 → M Lotes**
- **Usuario 1 → M Lotes (como responsable del registro)**

### ✔ Agregaciones y consultas avanzadas

Ejemplo de obtención de la fecha más próxima de vencimiento usando agregaciones:

``` python
from django.db.models import Min

proximo_vto = articulo.lotes.filter(activo=True).aggregate(
    Min('fecha_vencimiento')
)['fecha_vencimiento__min']
```

### ✔ Optimización con `prefetch_related`

``` python
Articulo.objects.filter(activo=True).prefetch_related('lotes')
```

Esto mejora el rendimiento evitando consultas repetitivas al cargar lotes asociados.

---

## ⚙️ Panel de Administración Personalizado (Rúbrica Punto 4)

El panel de administración de Django fue personalizado agregando filtros, búsquedas y columnas relevantes:

``` python
@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('numero_lote', 'articulo', 'fecha_vencimiento', 'responsable_registro', 'activo')
    list_filter = ('articulo__departamento', 'activo', 'fecha_vencimiento')
    search_fields = ('numero_lote', 'articulo__nombre')
```

Esto permite al administrador gestionar fácilmente artículos, departamentos y lotes desde el panel admin.

---

## 📘 Tecnologías utilizadas

- Python 3.12  
- Django 5.x  
- SQLite  
- HTML5 + CSS3  
- Bootstrap 5  
- JavaScript (con activación automática de modal)  
- Autenticación con Django Auth y permisos por grupos  
- Vistas basadas en clases (CBV)  
- Formularios con ModelForms

---

## 👤 Autora

**Cintya Ramírez**  
Analista Programadora - Fullstack Python  
Proyecto final: *Sistema de Gestión de Vencimientos para Supermercado*.