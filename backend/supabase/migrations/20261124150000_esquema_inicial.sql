-- Esquema inicial del sistema de seguimiento de crisis FBTCS (v0.1)
-- Responsable: Elizabeth. Consumen: Ariana (app) y Joseph (web).

-- ========== Tipos ==========
create type rol_usuario as enum ('paciente', 'enfermero', 'epileptologo', 'admin');
create type estado_revision as enum ('sin_revisar', 'confirmada', 'falso_positivo');
create type funcion_asignada as enum ('enfermero', 'segundo_contacto', 'epileptologo');

-- ========== Tablas ==========
create table perfiles (
  id uuid primary key references auth.users (id) on delete cascade,
  rol rol_usuario not null,
  nombre text not null,
  creado_en timestamptz not null default now()
);

create table pacientes (
  id uuid primary key default gen_random_uuid(),
  codigo text not null unique,                       -- ej. P-007
  usuario_id uuid unique references perfiles (id),   -- cuenta del paciente en la app
  creado_en timestamptz not null default now()
);

create table asignaciones (
  paciente_id uuid not null references pacientes (id) on delete cascade,
  usuario_id uuid not null references perfiles (id) on delete cascade,
  funcion funcion_asignada not null,
  primary key (paciente_id, usuario_id, funcion)
);

create table dispositivos (
  id uuid primary key default gen_random_uuid(),
  paciente_id uuid not null references pacientes (id) on delete cascade,
  tipo text not null check (tipo in ('pulsera', 'simulador')),
  bateria smallint check (bateria between 0 and 100),
  ultimo_dato timestamptz
);

-- Clave natural (dispositivo_id, boot_id, t_ms): reenviar un lote no duplica filas
create table resumenes (
  dispositivo_id uuid not null references dispositivos (id) on delete cascade,
  boot_id integer not null,
  t_ms bigint not null,
  momento timestamptz not null,
  fc_lpm smallint,
  eda_us real,
  actividad real,
  calidad_ppg boolean,
  calidad_eda boolean,
  calidad_acc boolean,
  primary key (dispositivo_id, boot_id, t_ms)
);
create index resumenes_momento_idx on resumenes (dispositivo_id, momento);

create table crisis (
  id uuid primary key default gen_random_uuid(),
  paciente_id uuid not null references pacientes (id) on delete cascade,
  dispositivo_id uuid not null references dispositivos (id),
  boot_id integer not null,
  t_ms_inicio bigint not null,
  inicio timestamptz not null,
  fin timestamptz,
  confianza smallint check (confianza between 0 and 100),
  origen text not null default 'real' check (origen in ('real', 'simulada')),
  revision estado_revision not null default 'sin_revisar',
  inicio_corregido timestamptz,
  fin_corregido timestamptz,
  revisada_por uuid references perfiles (id),
  revisada_en timestamptz,
  nota text,
  creado_en timestamptz not null default now(),
  unique (dispositivo_id, boot_id, t_ms_inicio)
);
create index crisis_paciente_idx on crisis (paciente_id, inicio desc);

create table senales (
  id uuid primary key default gen_random_uuid(),
  crisis_id uuid not null references crisis (id) on delete cascade,
  ruta_storage text not null,
  t_desde_ms bigint not null,
  t_hasta_ms bigint not null,
  frecuencia_hz real not null,
  submuestreada boolean not null default false,
  unique (crisis_id, t_desde_ms, t_hasta_ms, submuestreada)
);

create table alertas (
  id uuid primary key default gen_random_uuid(),
  crisis_id uuid not null references crisis (id) on delete cascade,
  destinatario_id uuid references perfiles (id),
  canal text not null check (canal in ('push', 'sms')),
  enviada_en timestamptz not null default now(),
  visto_en timestamptz,
  escalada_en timestamptz,
  falsa_alarma_en timestamptz
);
create index alertas_pendientes_idx on alertas (enviada_en) where visto_en is null;

-- ========== Funciones auxiliares para RLS ==========
create function rol_actual() returns rol_usuario
language sql stable security definer set search_path = public as $$
  select rol from perfiles where id = auth.uid()
$$;

create function ve_paciente(pid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(rol_actual() = 'admin', false)
      or exists (select 1 from pacientes p where p.id = pid and p.usuario_id = auth.uid())
      or exists (select 1 from asignaciones a where a.paciente_id = pid and a.usuario_id = auth.uid())
$$;

create function revisa_paciente(pid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(rol_actual() = 'admin', false)
      or exists (select 1 from asignaciones a
                 where a.paciente_id = pid and a.usuario_id = auth.uid() and a.funcion = 'epileptologo')
$$;

create function es_su_paciente(pid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from pacientes p where p.id = pid and p.usuario_id = auth.uid())
$$;

-- ========== RLS ==========
alter table perfiles enable row level security;
alter table pacientes enable row level security;
alter table asignaciones enable row level security;
alter table dispositivos enable row level security;
alter table resumenes enable row level security;
alter table crisis enable row level security;
alter table senales enable row level security;
alter table alertas enable row level security;

create policy perfiles_ver on perfiles for select
  using (id = auth.uid() or rol_actual() = 'admin');
create policy perfiles_admin on perfiles for all
  using (rol_actual() = 'admin') with check (rol_actual() = 'admin');

create policy pacientes_ver on pacientes for select using (ve_paciente(id));
create policy pacientes_admin on pacientes for all
  using (rol_actual() = 'admin') with check (rol_actual() = 'admin');

create policy asignaciones_ver on asignaciones for select
  using (usuario_id = auth.uid() or ve_paciente(paciente_id));
create policy asignaciones_admin on asignaciones for all
  using (rol_actual() = 'admin') with check (rol_actual() = 'admin');

create policy dispositivos_ver on dispositivos for select using (ve_paciente(paciente_id));
create policy dispositivos_escribir on dispositivos for all
  using (es_su_paciente(paciente_id) or rol_actual() = 'admin')
  with check (es_su_paciente(paciente_id) or rol_actual() = 'admin');

-- La app del paciente escribe; los demás solo leen
create policy resumenes_ver on resumenes for select
  using (ve_paciente((select d.paciente_id from dispositivos d where d.id = dispositivo_id)));
create policy resumenes_insertar on resumenes for insert
  with check (es_su_paciente((select d.paciente_id from dispositivos d where d.id = dispositivo_id)));

create policy crisis_ver on crisis for select using (ve_paciente(paciente_id));
create policy crisis_insertar on crisis for insert
  with check (es_su_paciente(paciente_id) and revision = 'sin_revisar' and revisada_por is null);
create policy crisis_revisar on crisis for update
  using (revisa_paciente(paciente_id)) with check (revisa_paciente(paciente_id));

create policy senales_ver on senales for select
  using (ve_paciente((select c.paciente_id from crisis c where c.id = crisis_id)));
create policy senales_insertar on senales for insert
  with check (es_su_paciente((select c.paciente_id from crisis c where c.id = crisis_id)));

create policy alertas_ver on alertas for select
  using (destinatario_id = auth.uid()
         or ve_paciente((select c.paciente_id from crisis c where c.id = crisis_id)));
create policy alertas_visto on alertas for update
  using (destinatario_id = auth.uid()) with check (destinatario_id = auth.uid());
