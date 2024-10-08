#from django.http import HttpResponse
from django.shortcuts import render
from .models import Climatologia
from django.http import JsonResponse
from django.utils import timezone

import threading
import serial
import time



def datos_climatologicos_api(request):
    datos = Climatologia.objects.all().order_by('-fecha')[:10]
    fechas = [dato.fecha.strftime('%Y-%m-%d %H:%M:%S') for dato in datos]
    temperaturas = list(datos.values_list('temperatura', flat=True))
    humedades = list(datos.values_list('humedad', flat=True))
    presiones = list(datos.values_list('presion', flat=True))
    velocidades_viento = list(datos.values_list('velocidad_viento', flat=True))

    return JsonResponse({
        'fechas': fechas,
        'temperaturas': temperaturas,
        'humedades': humedades,
        'presiones': presiones,
        'velocidades_viento': velocidades_viento,
    })


def vista_climatologica(request):
    datos = Climatologia.objects.all().order_by('fecha')
    
    # Extrae los datos en listas y convierte las fechas a cadenas en formato ISO
    fechas = [dato.fecha.strftime('%Y-%m-%dT%H:%M:%SZ') for dato in datos]
    temperaturas = list(datos.values_list('temperatura', flat=True))
    humedades = list(datos.values_list('humedad', flat=True))
    presiones = list(datos.values_list('presion', flat=True))
    velocidades_viento = list(datos.values_list('velocidad_viento', flat=True))

    contexto = {
        'fechas': fechas,
        'temperaturas': temperaturas,
        'humedades': humedades,
        'presiones': presiones,
        'velocidades_viento': velocidades_viento,
    }
    
    return render(request, 'climatologia.html', contexto)


# Variable global para almacenar el hilo de lectura
hilo_lectura = None
continuar_lectura = False

def leer_datos_climatologicos():
    global continuar_lectura
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
    
    while continuar_lectura:
        datos = ser.readline().decode('utf-8').strip()
        if datos:
            try:
                temperatura, humedad, presion, velocidad_viento = map(float, datos.split(','))
                nueva_entrada = Climatologia(
                    temperatura=temperatura,
                    humedad=humedad,
                    presion=presion,
                    velocidad_viento=velocidad_viento,
                    #fecha=time.strftime('%Y-%m-%d %H:%M:%S')
                    fecha=timezone.now()
                )
                nueva_entrada.save()
                print(f"Datos guardados: {datos}")
            except ValueError:
                print(f"Error al procesar datos: {datos}")
        time.sleep(2)

def iniciar_lectura(request):
    global hilo_lectura, continuar_lectura

    if hilo_lectura is None or not hilo_lectura.is_alive():
        continuar_lectura = True
        hilo_lectura = threading.Thread(target=leer_datos_climatologicos)
        hilo_lectura.start()
        return JsonResponse({'status': 'Lectura iniciada'})
    else:
        return JsonResponse({'status': 'La lectura ya está en ejecución'})

def detener_lectura(request):
    global continuar_lectura

    continuar_lectura = False
    return JsonResponse({'status': 'Lectura detenida'})
