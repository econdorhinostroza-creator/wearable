# Esquema de datos

Versión: v0.1 (borrador)
Responsable: Elizabeth. Consumen: Ariana (app) y Joseph (web).
El detalle exacto está en backend/supabase/migrations/20261124150000_esquema_inicial.sql.

## Roles
paciente, enfermero, epileptologo, admin. El rol vive en la tabla perfiles.

## Tablas

| Tabla | Para qué sirve | Campos principales |
|---|---|---|
| perfiles | Un perfil por usuario con sesión | id, rol, nombre |
| pacientes | Un paciente (código tipo P-007) | id, codigo, usuario_id |
| asignaciones | Quién cuida o revisa a cada paciente | paciente_id, usuario_id, funcion (enfermero, segundo_contacto, epileptologo) |
| dispositivos | Pulsera real o simulador | id, paciente_id, tipo, bateria, ultimo_dato |
| resumenes | Métricas por minuto | dispositivo_id, boot_id, t_ms, momento, fc_lpm, eda_us, actividad, calidad_ppg, calidad_eda, calidad_acc |
| crisis | Una crisis detectada | id, paciente_id, dispositivo_id, boot_id, t_ms_inicio, inicio, fin, confianza, origen, revision, inicio_corregido, fin_corregido, revisada_por, revisada_en, nota |
| senales | Señal cruda de una crisis, guardada en Storage | crisis_id, ruta_storage, t_desde_ms, t_hasta_ms, frecuencia_hz, submuestreada |
| alertas | Avisos enviados por una crisis | crisis_id, destinatario_id, canal (push o sms), enviada_en, visto_en, escalada_en, falsa_alarma_en |

## Claves naturales (para no duplicar al reenviar)
- resumenes: (dispositivo_id, boot_id, t_ms)
- crisis: (dispositivo_id, boot_id, t_ms_inicio)
- senales: (crisis_id, t_desde_ms, t_hasta_ms, submuestreada)

Ariana: la app debe enviar boot_id y t_ms de la pulsera tal cual; así reenviar un lote no duplica filas.

## Estados de revisión de una crisis
sin_revisar (por defecto), confirmada, falso_positivo. Solo el epileptólogo asignado o el admin los cambia.

## Quién ve y escribe qué
- Paciente: ve y escribe lo suyo (dispositivo, resúmenes, crisis y señales nuevas). No puede crear crisis ya confirmadas.
- Enfermero: ve a sus pacientes y marca "visto" en sus alertas.
- Epileptólogo: ve a sus pacientes y revisa crisis (confirmar, falso positivo, corregir marcas, notas).
- Admin: ve y modifica todo.
- Sin sesión: no ve nada.

## Pendiente
- Tabla de contactos y mensajes de falsa alarma (Sprint 4).
- Políticas de Storage para las señales.
- Confirmar con Ariana y Joseph los campos que necesitan.