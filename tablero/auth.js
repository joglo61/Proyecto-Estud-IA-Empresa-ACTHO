const sb=supabase.createClient(SUPABASE_URL,SUPABASE_KEY);
async function entrar(u,p){const{error}=await sb.auth.signInWithPassword({email:u.trim(),password:p});return !error}
async function salir(){await sb.auth.signOut();location.href='login.html'}
async function guardia(){const{data}=await sb.auth.getSession();if(!data.session)location.replace('login.html');return data.session}
async function cargarApp(){
const ses=await guardia();if(!ses)return;
const{data,error}=await sb.from('tablero_datos').select('clave,datos');
if(error||!data||!data.length){await salir();return}
data.forEach(r=>{window[r.clave]=r.datos});
document.getElementById('usr').textContent=ses.user.email;
const el=document.createElement('script');el.text=document.getElementById('app').textContent;document.body.appendChild(el)}
if(document.documentElement.dataset.protegida!==undefined&&!document.getElementById('app'))guardia().then(s=>{const u=document.getElementById('usr');if(s&&u)u.textContent=s.user.email});
