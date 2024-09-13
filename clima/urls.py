from django.urls import path
from . import views

urlpatterns = [
    path('climatologia/', views.vista_climatologica, name='vista_climatologica'),
    path('iniciarlectura/', views.iniciar_lectura, name='iniciar_lectura_arduino'),
    path('detenerlectura/', views.detener_lectura, name='detener_lectura_arduino'),
    path('api/datos-climatologicos/', views.datos_climatologicos_api, name='datos_climatologicos_api'),
]
