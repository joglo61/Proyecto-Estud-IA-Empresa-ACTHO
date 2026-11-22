create table if not exists public.tablero_datos(
clave text primary key,
datos jsonb not null,
actualizado timestamptz not null default now()
);
alter table public.tablero_datos enable row level security;
drop policy if exists leer_autenticados on public.tablero_datos;
create policy leer_autenticados on public.tablero_datos for select to authenticated using (true);
