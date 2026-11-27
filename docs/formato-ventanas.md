# Formato de las ventanas (ficha v0.3)

Responsable: Elizabeth. Consumen: Ariana (reproductor) y Joseph (modelo).
Estado: borrador. Lo marcado "confirmar" aún no está verificado.

## Resumen

| Fuente | Señales | Frecuencias | Hora real | Estado |
|---|---|---|---|---|
| Mayo (Zenodo 17380899) | ACC, EDA, BVP | 32, 4 y 64 Hz | Sí (UTC) | Procesada |
| SeizeIT2 (OpenNeuro ds005873) | Solo ACC | 25 Hz | No | Procesada |
| My Seizure Gauge en Seer | ACC, EDA, BVP (E4); ACC y PPG o EMG (Byteflies) | Confirmar | Confirmar | Sin descargar |
| UE4W (Zenodo 6898244) | ACC (confirmar EDA y BVP) | Confirmar | Confirmar | Sin descargar; solo prueba |

## Mayo: My Seizure Gauge en Zenodo (Empatica E4)
- Origen: Zenodo, DOI 10.5281/zenodo.17380899, licencia CC BY 4.0
- Autores: B. Brinkmann (curador) y M. Nasseri (recolectora), Mayo Clinic
- Datos originales: zips del E4 (ACC.csv, EDA.csv, BVP.csv); la fila 1 de cada csv trae la hora de inicio en UTC y la fila 2 la frecuencia
- Archivos: carpeta ventanas_completo con ventanas.npz (1,45 GB), meta.csv y tabla_dataset.csv. Viven fuera del repositorio
- Claves del .npz: acc (254744, 320, 3) float32, en g, filtro pasa banda 0,5–15 Hz; eda (254744, 40) float32, en µS, pasabajos 1 Hz; bvp (254744, 640) float32, filtro pasa banda 0,5–8 Hz; y (254744,) int64
- Frecuencias: ACC 32 Hz, EDA 4 Hz, BVP 64 Hz
- Ventana: 10 s (320, 40 y 640 muestras)
- Etiqueta y: 1 = ictal (69); 0 = interictal (254675). Las ictales vienen de intervalos_ictales.csv (marcado sobre las gráficas)
- Paso entre ventanas: ictales cada 5 s (solapadas al 50 %); interictales 1 de cada 12, es decir, cada 60 s (verificado en meta.csv y tabla_dataset.csv)
- Descartadas: 120 s antes y después de cada crisis, y las zonas probable, dudosa y excluir
- Hora real: sí. meta.csv trae t_ini_utc (tiempo Unix UTC) por ventana
- Columnas de meta.csv: sesion, t_ini_utc, y, id_evento, usar_acc, usar_eda, eda_cero_frac (fracción de EDA en cero)
- Columnas de tabla_dataset.csv: sesion, duracion_h, ventanas_0, ventanas_1
- Sesiones: el nombre es el tiempo Unix de inicio más el serial de la pulsera (A01EE3, A01EEC, A02294)
- Paciente: no viene en el archivo. Solo la sesión
- Eventos ictales presentes: 4, en 3 sesiones

| Evento | Sesión | Ventanas | Cubren | Inicio (UTC) |
|---|---|---|---|---|
| E01 | 1598624269_A01EE3 | 21 | 110 s | 2020-08-29 12:30:49 |
| E09 | 1604525961_A02294 | 14 | 75 s | 2020-11-05 11:09:06 |
| E10 | 1604525961_A02294 | 17 | 90 s | 2020-11-05 14:11:21 |
| E12 | 1617460460_A01EEC | 17 | 90 s | 2021-04-04 12:18:15 |

- Eventos sin ventanas ictales: E02 a E08 y E11 no aparecen. Confirmar con intervalos_ictales.csv si son zonas probable, dudosa o excluir
- Rango de valores: ACC de −3,10 a 3,05; EDA de −0,14 a 225,2; BVP de −3620 a 3362. Revisar: el ACC supera el ±2 g habitual del E4 y la EDA máxima parece un artefacto
- NaN: ninguno
- Correspondencia con meta.csv: verificada; la columna y coincide fila a fila en las 254744 ventanas
- Tipo de crisis: confirmar (la ficha del dataset no lo indica)
- Aviso: el ACC está filtrado (sin componente continua, media cerca de 0), así que no incluye la gravedad
- Aviso: con 4 eventos, la partición entre entrenamiento y prueba debe ser por evento o por sesión, nunca al azar. Cuántos pacientes distintos hay: confirmar

## SeizeIT2 (solo acelerómetro)
- Origen: OpenNeuro ds005873 v1.1.0 (CC0)
- Archivo: ventanas_seizeit2.npz, con meta.csv
- Claves: acc (142261 x 250, float32), y (int64), sujeto (texto), run (texto), t_ini_s (float64)
- Señal: magnitud del ACC del módulo EEG SD (espalda), filtro pasa banda 0,5–10 Hz (sin componente continua, media cerca de 0)
- Frecuencia: 25 Hz (el contrato pide 50 Hz: el convertidor remuestrea)
- Ventana: 10 s (250 muestras), paso 5 s
- Etiqueta y: 1 = ventana que se solapa con una crisis tónico-clónica (1621); 0 = normal (140640)
- Normales: solo de intervalos sin crisis, a más de 120 s de cualquier crisis, 1 de cada 12
- Sujetos: 35. Grabaciones (run): 843, nombre del archivo EDF
- Pre y post-ictal: no hay
- Hora real: no; solo t_ini_s relativo al inicio de cada grabación (hasta unas 24 h)
- Rango de valores: de −28,7 a +23,8 (unidad: confirmar en el encabezado del EDF)
- Canales EDA y PPG: no disponibles
- Sujetos excluidos: sub-054 (EDF truncado) y sub-121 (sin ventanas)

## My Seizure Gauge en Epilepsy Ecosystem (Seer)
- Origen: https://www.epilepsyecosystem.org/my-seizure-gauge-1
- Acceso: registro, aceptar términos y descargar con Seer-Py. Solo uso no comercial. No se redistribuye ni se sube al repositorio
- Dispositivos según la página: Empatica E4 (9 pacientes: ACC, BVP, EDA, FC y temperatura), Byteflies Sensor Dot (5 pacientes: ACC más EMG o PPG de 3 canales) y Epilog (1 paciente: EEG)
- Participantes: 10, con 3 a 5 días de registro cada uno
- Frecuencias de muestreo, número de crisis y tipo de crisis: confirmar con los metadatos al descargar
- Estado: sin descargar (el descargador dio el error NoSuchBucket)

## UE4W: Unlabeled Empatica E4 Wristband Data (solo prueba)
- Origen: Zenodo, DOI 10.5281/zenodo.6898244, licencia CC BY 4.0 (Hinkle y Metsis, Texas State University)
- Contenido: un solo adulto, unas 250 h, 30 zips de 2 a 12 MB; la página nombra solo la aceleración (confirmar EDA y BVP abriendo un zip)
- Sin crisis ni etiquetas; se asume sin crisis porque la página no indica epilepsia
- Uso: medir falsas alarmas por día y probar una noche completa en la app. Nunca para entrenar. En MANIFIESTO.csv: uso = prueba_falsas_alarmas

## Reglas del reproductor
- Si falta una señal, el canal queda vacío y su bit de calidad dice "no disponible". No se inventan datos.
- El convertidor deja ACC en cuentas del ADXL345 (≈3,9 mg por cuenta, a confirmar) y EDA en mV (R4 = R13 = 100 kΩ; 1 µS da 545,5 mV y 10 µS da 750 mV).
- Las ventanas de prueba que usa la demo no deben haber sido vistas por el modelo al entrenar.
- Los datos completos no se suben al repositorio. Solo MANIFIESTO.csv y 3 a 5 muestras pequeñas.

## Límites conocidos
- Las ventanas no permiten recortar el contexto de −3/+15 min de cada crisis: las interictales están muestreadas (1 por minuto en Mayo). Ese recorte se hace desde los datos originales (script recortar_crisis.py, todavía en prueba).
- Las ictales de Mayo sí se pueden unir en un tramo continuo de 75 a 110 s, por su paso de 5 s.

## Citas
- Brinkmann, B. y Nasseri, M. My Seizure Gauge Long-term Wearable Data. Zenodo. DOI 10.5281/zenodo.17380899 (CC BY 4.0).
- Hinkle, L. B. y Metsis, V. Unlabeled Empatica E4 Wristband Data (UE4W). Zenodo. DOI 10.5281/zenodo.6898244 (CC BY 4.0).
- SeizeIT2. OpenNeuro, ds005873, versión 1.1.0 (CC0).
