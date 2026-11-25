# Formato de las ventanas (ficha v0.1)

Responsable: Elizabeth. Consumen: Ariana (reproductor) y Joseph (modelo).
Estado: borrador. Lo marcado "confirmar" aún no está verificado.

## SeizeIT2 (solo acelerómetro)
- Archivo: ventanas_seizeit2.npz, con meta.csv
- Claves: acc (142261 x 250, float32), y (int64), sujeto (texto), run (texto), t_ini_s (float64)
- Señal: magnitud del ACC del módulo EEG SD (espalda), filtro pasa banda 0,5–10 Hz (sin componente continua, media ≈ 0)
- Frecuencia: 25 Hz (el contrato pide 50 Hz: el convertidor remuestrea)
- Ventana: 10 s (250 muestras), paso 5 s
- Etiqueta y: 1 = ventana que se solapa con una crisis tónico-clónica (1621); 0 = normal (140640)
- Normales: solo de intervalos sin crisis, a más de 120 s de cualquier crisis, 1 de cada 12
- Sujetos: 35. Grabaciones (run): 843, nombre del archivo EDF
- Pre y post-ictal: no hay (solo ictal y normal)
- Hora real: no; solo t_ini_s relativo al inicio de cada grabación (hasta ~24 h)
- Rango de valores: −28,7 a +23,8 (unidad: confirmar en el encabezado del EDF)
- Canales EDA y PPG: no disponibles
- Sujetos excluidos: sub-054 (EDF truncado) y sub-121 (sin ventanas)
- Origen: OpenNeuro ds005873 v1.1.0 (CC0)

## Mayo: My Seizure Gauge en Zenodo (ACC, EDA y BVP)
- Origen: Zenodo, DOI 10.5281/zenodo.17380899 (v1, 17-oct-2025)
- Autores: B. Brinkmann (curador) y M. Nasseri (recolectora), Mayo Clinic
- Licencia: CC BY 4.0 (hay que citar la fuente en cualquier trabajo que use los datos)
- Pulseras: Empatica E4 y Fitbit Charge HR
- Archivos: carpeta ventanas_completo con ventanas.npz (1,45 GB), meta.csv (11,7 MB) y tabla_dataset.csv (4 KB). Viven fuera del repositorio (datos/local o carpeta compartida)
- Claves del .npz: acc (254744, 320, 3) float32; eda (254744, 40) float32; bvp (254744, 640) float32; y (254744,) int64
- Ventana: 320, 40 y 640 muestras, equivalente a 10 s a 32, 4 y 64 Hz (confirmar la duración en el código de extracción)
- Etiqueta y: 1 = ictal (69); 0 = normal (254675). Criterio de la etiqueta: confirmar
- Paso entre ventanas: ictales cada 5 s (solapadas al 50 %); normales cada 60 s (verificado en meta.csv y tabla_dataset.csv). Las normales cubren solo parte de cada grabación
- Hora real: sí. meta.csv trae t_ini_utc (tiempo Unix UTC) por ventana
- Columnas de meta.csv: sesion, t_ini_utc, y, id_evento, usar_acc, usar_eda, eda_cero_frac. Significado de las tres últimas: confirmar
- Columnas de tabla_dataset.csv: sesion, duracion_h, ventanas_0, ventanas_1
- Sesiones: el nombre es el tiempo Unix de inicio más el serial de la pulsera (A01EE3, A01EEC, A02294)
- Paciente: no viene. Solo la sesión. No se asume que un serial sea un paciente
- Eventos ictales presentes: 4, en 3 sesiones (ventanas y tiempo que cubren, suponiendo 10 s por ventana)

| Evento | Sesión | Ventanas | Cubren | Inicio (UTC) |
|---|---|---|---|---|
| E01 | 1598624269_A01EE3 | 21 | 110 s | 2020-08-29 12:30:49 |
| E09 | 1604525961_A02294 | 14 | 75 s | 2020-11-05 11:09:06 |
| E10 | 1604525961_A02294 | 17 | 90 s | 2020-11-05 14:11:21 |
| E12 | 1617460460_A01EEC | 17 | 90 s | 2021-04-04 12:18:15 |

- Eventos sin ventanas ictales: los demás id_evento posibles (E02 a E08 y E11) no aparecen. Confirmar si pertenecen a otras sesiones o se excluyeron
- Valores: ACC −3,10 a 3,05 (media ≈ 0, sin componente continua; unidad: confirmar). EDA −0,14 a 225,2 (media 0,31; no parece EDA cruda en µS; unidad y procesamiento: confirmar). BVP −3620 a 3362 (media ≈ 0; unidad: confirmar)
- NaN: ninguno
- Tipo de crisis: confirmar. La página de Zenodo no dice si son tónico-clónicas
- Correspondencia con meta.csv: ambos tienen 254744 filas; el orden se comprueba comparando la columna y del .npz con la de meta.csv (pendiente)

## My Seizure Gauge en Epilepsy Ecosystem (Seer)
- Origen: https://www.epilepsyecosystem.org/my-seizure-gauge-1
- Acceso: registro, aceptar términos y descarga con Seer-Py. Solo uso no comercial. No se redistribuye ni se sube al repositorio
- Dispositivos según la página: Empatica E4 (9 pacientes: ACC, BVP, EDA, FC y temperatura), Byteflies Sensor Dot (5 pacientes: ACC más EMG o PPG de 3 canales) y Epilog (1 paciente: EEG)
- Participantes: 10, con 3 a 5 días de registro cada uno
- Frecuencias de muestreo, número de crisis y tipo de crisis: no las indica la página; confirmar en los metadatos al descargar
- Estado: sin descargar todavía (el descargador dio error NoSuchBucket)

## Reglas del reproductor
- Si falta una señal, el canal queda vacío y su bit de calidad dice "no disponible". No se inventan datos.
- El convertidor deja ACC en cuentas del ADXL345 (≈3,9 mg por cuenta, a confirmar) y EDA en mV.
- Las ventanas de prueba que usa la demo no deben haber sido vistas por el modelo al entrenar.
- Mayo trae solo 4 eventos ictales en 3 sesiones. La separación entrenamiento/prueba se hace por evento o por sesión, nunca por ventana, porque las ictales se solapan al 50 %.

## Límites conocidos
- Las ventanas no permiten recortar el contexto de −3/+15 min de cada crisis: las normales están muestreadas (1 por minuto en Mayo). Ese recorte se hace desde los registros originales.
- Las ictales de Mayo sí se pueden unir en un tramo continuo de 75 a 110 s, por su paso de 5 s.