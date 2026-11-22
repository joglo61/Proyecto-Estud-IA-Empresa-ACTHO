create table if not exists public.perfiles(
user_id uuid primary key references auth.users(id) on delete cascade,
cargo text not null check (cargo in ('direccion','junta','comercial','eventos','contabilidad'))
);

create table if not exists public.cargos_tableros(
cargo text not null,
tablero text not null check (tablero in ('resumen','eventos','comunicaciones','finanzas')),
primary key (cargo,tablero)
);

insert into public.cargos_tableros(cargo,tablero) values
('direccion','resumen'),('direccion','eventos'),('direccion','comunicaciones'),('direccion','finanzas'),
('junta','resumen'),('junta','eventos'),('junta','comunicaciones'),('junta','finanzas'),
('comercial','resumen'),('comercial','comunicaciones'),
('eventos','eventos'),('eventos','comunicaciones'),
('contabilidad','finanzas')
on conflict do nothing;

alter table public.perfiles enable row level security;
alter table public.cargos_tableros enable row level security;
drop policy if exists ver_mi_perfil on public.perfiles;
create policy ver_mi_perfil on public.perfiles for select to authenticated using (user_id=auth.uid());
drop policy if exists ver_cargos on public.cargos_tableros;
create policy ver_cargos on public.cargos_tableros for select to authenticated using (true);

alter table public.tablero_datos add column if not exists tableros text[] not null default '{}';

create or replace function public.mis_tableros() returns text[]
language sql stable security definer set search_path=public as $$
select coalesce(array_agg(ct.tablero order by ct.tablero),'{}')
from public.perfiles p join public.cargos_tableros ct on ct.cargo=p.cargo
where p.user_id=auth.uid()
$$;
revoke all on function public.mis_tableros() from public,anon;
grant execute on function public.mis_tableros() to authenticated;

create or replace function public.asignar_cargo(correo text,nuevo_cargo text) returns void
language plpgsql security definer set search_path=public as $$
declare uid uuid;
begin
select id into uid from auth.users where lower(email)=lower(correo);
if uid is null then raise exception 'No existe un usuario con el correo %',correo; end if;
insert into public.perfiles(user_id,cargo) values (uid,nuevo_cargo)
on conflict (user_id) do update set cargo=excluded.cargo;
end $$;
revoke all on function public.asignar_cargo(text,text) from public,anon,authenticated;

do $$
begin
if exists (select 1 from public.tablero_datos where clave='X') then
insert into public.tablero_datos(clave,datos,tableros)
select 'X_ev',jsonb_build_object('ev',datos->'ev','lin',datos->'lin','mod',datos->'mod'),array['eventos'] from public.tablero_datos where clave='X'
on conflict (clave) do update set datos=excluded.datos,tableros=excluded.tableros,actualizado=now();
insert into public.tablero_datos(clave,datos,tableros)
select 'X_pe',jsonb_build_object('pe',datos->'pe'),array['eventos','comunicaciones'] from public.tablero_datos where clave='X'
on conflict (clave) do update set datos=excluded.datos,tableros=excluded.tableros,actualizado=now();
insert into public.tablero_datos(clave,datos,tableros)
select 'X_enc',jsonb_build_object('enc',datos->'enc'),array['comunicaciones'] from public.tablero_datos where clave='X'
on conflict (clave) do update set datos=excluded.datos,tableros=excluded.tableros,actualizado=now();
insert into public.tablero_datos(clave,datos,tableros)
select 'X_altas',jsonb_build_object('altas',datos->'altas'),array['comunicaciones','finanzas'] from public.tablero_datos where clave='X'
on conflict (clave) do update set datos=excluded.datos,tableros=excluded.tableros,actualizado=now();
insert into public.tablero_datos(clave,datos,tableros)
select 'X_fin',jsonb_build_object('venm',datos->'venm','reno',datos->'reno'),array['finanzas'] from public.tablero_datos where clave='X'
on conflict (clave) do update set datos=excluded.datos,tableros=excluded.tableros,actualizado=now();
delete from public.tablero_datos where clave='X';
end if;
end $$;

update public.tablero_datos set tableros=array['resumen','eventos','comunicaciones','finanzas'] where clave='D';
update public.tablero_datos set tableros=array['resumen'] where clave='C';

drop policy if exists leer_autenticados on public.tablero_datos;
drop policy if exists leer_por_cargo on public.tablero_datos;
create policy leer_por_cargo on public.tablero_datos for select to authenticated using (tableros && public.mis_tableros());
