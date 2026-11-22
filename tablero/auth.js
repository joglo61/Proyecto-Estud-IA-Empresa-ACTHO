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
function contar(el,txt){if(!/^\d{1,3}(\.\d{3})*$/.test(txt)||matchMedia('(prefers-reduced-motion: reduce)').matches){el.textContent=txt;return}
const fin=+txt.replace(/\./g,''),t0=performance.now(),f=n=>String(n).replace(/\B(?=(\d{3})+(?!\d))/g,'.');
(function paso(t){const p=Math.min((t-t0)/800,1),e=1-Math.pow(1-p,3);el.textContent=f(Math.round(fin*e));if(p<1)requestAnimationFrame(paso);else el.textContent=txt})(t0)}
