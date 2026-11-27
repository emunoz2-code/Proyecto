# Control del vehículo · Parcial 3

Interfaz de escritorio en Flet para probar las órdenes del vehículo con datos locales. En PyCharm, abre esta carpeta y selecciona el intérprete del proyecto flet que usaste en clase. Ejecuta main.py. Para un entorno nuevo, instala las dependencias con 'python -m pip install -r requirements.txt'.

Con el sensor a 100 cm, pulsa Avanzar y ajusta la potencia. Cambia la distancia a 20 cm y pulsa Aplicar distancia. El movimiento pasa a Detenido y el PWM aplicado baja a cero. Al despejar el sensor se requiere una nueva orden. También puedes simular una lectura perdida desde la lista Sensor. La gráfica toma una muestra cada segundo y el historial registra hasta 30 eventos durante la sesión.

main.py organiza los controles, vehiculo.py aplica las reglas y paneles.py adapta la gráfica y la tabla del ejemplo trabajado en clase. El montaje usa el mismo umbral de parada del firmware publicado. La comunicación con la ESP32 queda para la etapa de integración.
