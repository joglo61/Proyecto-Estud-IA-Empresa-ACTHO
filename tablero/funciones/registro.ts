import { createClient } from 'npm:@supabase/supabase-js@2';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

const responder = (cuerpo: unknown, estado = 200) =>
  new Response(JSON.stringify(cuerpo), { status: estado, headers: { ...cors, 'Content-Type': 'application/json' } });

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return responder({ error: 'Método no permitido.' }, 405);

  let datos: { correo?: string; clave?: string; codigo?: string };
  try {
    datos = await req.json();
  } catch {
    return responder({ error: 'Solicitud no válida.' }, 400);
  }

  const correo = String(datos.correo ?? '').trim().toLowerCase();
  const clave = String(datos.clave ?? '');
  const codigo = String(datos.codigo ?? '').trim().toUpperCase();

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) return responder({ error: 'Escribe un correo válido.' }, 400);
  if (clave.length < 8) return responder({ error: 'La contraseña debe tener mínimo 8 caracteres.' }, 400);
  if (!codigo) return responder({ error: 'Escribe tu código de invitación.' }, 400);

  const admin = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  const { data: inv } = await admin.from('invitaciones').select('cargo').eq('codigo', codigo).eq('activo', true).maybeSingle();
  if (!inv) return responder({ error: 'El código de invitación no es válido.' }, 403);

  const { data: creado, error: errUsuario } = await admin.auth.admin.createUser({
    email: correo,
    password: clave,
    email_confirm: true,
  });
  if (errUsuario || !creado?.user) {
    const existe = /already|registered|exists/i.test(errUsuario?.message ?? '');
    return responder({ error: existe ? 'Ya existe una cuenta con ese correo.' : 'No se pudo crear la cuenta.' }, existe ? 409 : 500);
  }

  const { error: errPerfil } = await admin.from('perfiles').insert({ user_id: creado.user.id, cargo: inv.cargo });
  if (errPerfil) {
    await admin.auth.admin.deleteUser(creado.user.id);
    return responder({ error: 'No se pudo asignar el cargo.' }, 500);
  }

  return responder({ ok: true });
});
