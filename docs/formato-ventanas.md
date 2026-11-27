Formato de las ventanas (ficha v0.2)

Responsable: Elizabeth. Consumen: Ariana (reproductor) y Joseph (modelo). Estado: borrador. Los campos marcados "confirmar" se completan con meta.csv y con los resultados de los scripts de verificación.

Resumen
Fuente	Señales	Frecuencias	Hora real	Estado
Mayo (Zenodo 17380899)	ACC, EDA, BVP	32, 4 y 64 Hz	Sí (UTC)	Procesada
SeizeIT2 (OpenNeuro ds005873)	Solo ACC	25 Hz	No	Procesada
My Seizure Gauge en Seer	ACC, EDA, BVP (E4); ACC y PPG o EMG (Byteflies)	Confirmar	Confirmar	Sin descargar
UE4W (Zenodo 6898244)	ACC (confirmar EDA y BVP)	Confirmar	Confirmar	Sin descargar; solo prueba
Mayo: My Seizure Gauge en Zenodo (Empatica E4)
Origen: Zenodo, DOI 10.5281/zenodo.17380899, licencia CC BY 4.0
Datos originales: zips del E4 (ACC.csv, EDA.csv, BVP.csv); la fila 1 de cada csv trae la hora de inicio en UTC y la fila 2 la frecuencia
Archivo de ventanas: ventanas.npz con meta.csv y tabla_dataset.csv
Claves: acc (N x 320 x 3, float32, en g, filtro 0,5–15 Hz), eda (N x 40, float32, µS, pasabajos 1 Hz), bvp (N x 640, float32, filtro 0,5–8 Hz), y (int)
Frecuencias: ACC 32 Hz, EDA 4 Hz, BVP 64 Hz
Ventana: 10 s, paso 5 s
Etiqueta y: 1 = ictal, 0 = interictal. Las ictales vienen de intervalos_ictales.csv (marcados sobre las gráficas)
Descartadas: 120 s antes y después de cada crisis, y zonas probable, dudosa y excluir
Interictales: 1 de cada 12 ventanas
Hora real: sí, t_ini_utc en meta.csv
Total de ventanas: 254744 (69 ictales). Pacientes y número de crisis: confirmar con meta.csv
Tipo de crisis: confirmar (la ficha del dataset no lo indica)
Aviso: el ACC está filtrado (sin componente continua, media cerca de 0), así que no incluye la gravedad
Aviso: las crisis etiquetadas podrían ser de un solo paciente (confirmar); la partición entre entrenamiento y prueba debe ser por crisis o por sesión, nunca al azar
SeizeIT2 (solo acelerómetro)
Origen: OpenNeuro ds005873 v1.1.0 (CC0)
Archivo: ventanas_seizeit2.npz, con meta.csv
Claves: acc (142261 x 250, float32), y (int64), sujeto (texto), run (texto), t_ini_s (float64)
Señal: magnitud del ACC del módulo EEG SD (espalda), filtro pasa banda 0,5–10 Hz (sin componente continua, media cerca de 0)
Frecuencia: 25 Hz (el contrato pide 50 Hz: el convertidor remuestrea)
Ventana: 10 s (250 muestras), paso 5 s
Etiqueta y: 1 = ventana que se solapa con una crisis tónico-clónica (1621); 0 = normal (140640)
Normales: solo de intervalos sin crisis, a más de 120 s de cualquier crisis, 1 de cada 12
Sujetos: 35. Grabaciones (run): 843, nombre del archivo EDF
Pre y post-ictal: no hay
Hora real: no; solo t_ini_s relativo al inicio de cada grabación (hasta unas 24 h)
Rango de valores: de -28,7 a +23,8 (unidad: confirmar en el encabezado del EDF)
Canales EDA y PPG: no disponibles
Sujetos excluidos: sub-054 (EDF truncado) y sub-121 (sin ventanas)
My Seizure Gauge en Epilepsy Ecosystem (Seer)
Origen: https://www.epilepsyecosystem.org/my-seizure-gauge-1
Acceso: registro, aceptar términos y descargar con Seer-Py. Solo uso no comercial. No se redistribuye ni se sube al repositorio.
Dispositivos según la página: Empatica E4 (9 pacientes: ACC, BVP, EDA, FC y temperatura), Byteflies Sensor Dot (5 pacientes: ACC más EMG o PPG de 3 canales) y Epilog (1 paciente: EEG)
Participantes: 10, con 3 a 5 días de registro cada uno
Frecuencias de muestreo, número de crisis y tipo de crisis: confirmar con los metadatos al descargar
Estado: sin descargar (el descargador dio el error NoSuchBucket)
UE4W: Unlabeled Empatica E4 Wristband Data (solo prueba)
Origen: Zenodo, DOI 10.5281/zenodo.6898244, licencia CC BY 4.0 (Hinkle y Metsis, Texas State University)
Contenido: un solo adulto, unas 250 h, 30 zips de 2 a 12 MB; la página nombra solo la aceleración (confirmar EDA y BVP abriendo un zip)
Sin crisis ni etiquetas; se asume sin crisis porque la página no indica epilepsia
Uso: medir falsas alarmas por día y probar una noche completa en la app. Nunca para entrenar. En MANIFIESTO.csv: uso = prueba_falsas_alarmas
Reglas del reproductor
Si falta una señal, el canal queda vacío y su bit de calidad dice "no disponible". No se inventan datos.
El convertidor deja ACC en cuentas del ADXL345 (≈3,9 mg por cuenta, a confirmar) y EDA en mV (R4 = R13 = 100 kΩ; 1 µS da 545,5 mV y 10 µS da 750 mV).
Los recortes de crisis (−3/+15 min, y −10/+30 min opcional) se hacen desde los datos originales con recortar_crisis.py, no desde las ventanas.
Las ventanas de prueba que usa la demo no deben haber sido vistas por el modelo al entrenar.
Los datos completos no se suben al repositorio. Solo MANIFIESTO.csv y 3 a 5 muestras pequeñas.
Citas
Brinkmann, B. y Nasseri, M. My Seizure Gauge Long-term Wearable Data. Zenodo. DOI 10.5281/zenodo.17380899 (CC BY 4.0).
Hinkle, L. B. y Metsis, V. Unlabeled Empatica E4 Wristband Data (UE4W). Zenodo. DOI 10.5281/zenodo.6898244 (CC BY 4.0).
SeizeIT2. OpenNeuro, ds005873, versión 1.1.0 (CC0).