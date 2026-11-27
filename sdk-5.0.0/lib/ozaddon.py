#!/usr/bin/env python3
"""OZPanel v9.1.4 (OZV8-Fortress+ · OZV7-Fortress · OZV6-ZeroTrust · OZV5-Shield) Addon Runtime Helpers (Python); permissions are declarations, not a sandbox or panel entitlement."""
import json,os,re,struct,subprocess,sys,tempfile,time,urllib.request,urllib.parse
from pathlib import Path
try:
 import fcntl
except ImportError:
 fcntl=None

EDITION='apt'
SDK_VERSION='5.0.0'
PANEL_VERSION='9.1.4'
OZONFS_VERSION='9.1.4'
SHIELD_ENGINE='OZV8-Fortress+'
SHIELD_STACK=['OZV8-Fortress+','OZV7-Fortress','OZV6-ZeroTrust-CloudSplit','OZV5-Shield']
LEASE_BYTES=72
LEASE_TTL_SECONDS=21600

_GET_ACTIONS=frozenset((
 'list','status','read','get','metrics','services','domains','mailboxes','dkim_dns','dns_records',
 'deliverability_check','accounts','queue','audit','zones','records','policy','export','preview',
 'query','channels','logs','workflows','hostnames','detect','diagnose','users','roles','installed',
 'output','info','features','feature','websites','runtime','security','api_coverage','language',
 'inventory','history','version','versions','extensions','probe','runtimes','ports','sites','modules',
 'health','cluster','autoscale','diagnostics','catalog','jobs','schedule_list','capabilities','parity',
 'check','ping','collect','tokens','get_config','routes','rules','nodes','threats','sources','tail',
 'processes','disk','network','stats','report','me','permissions','effective_permissions','members',
 'certificates','vhost_get','preflight','backups','stacks','images','volumes','networks','search',
 'config','skills','watchdog_cursors','validate','trash_list','download_chunk',
 'groups','group_status','shift_report','advice','providers','selftest','cache_stats','config_inspect',
 'bootstrap','pulse','deliveries','packages','usage','tables_list','health_probe','inspect_cert',
 'aliases_list','zones_list','records_list','banned_list','ext_list','client_config','service_journal'
))

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None

def no_links(path):
 path=Path(path).absolute()
 if any(p.is_symlink() for p in (path,*path.parents)):raise ValueError('Symlink in addon state path')
 return path

def _unpack_lease_expiry(raw_slice,now_ts):
 """Read expires_at from 72-byte runtime.lease (native launcher writes <Q little-endian; fallback >Q for legacy fixtures)."""
 le_val=struct.unpack('<Q',raw_slice)[0]
 be_val=struct.unpack('>Q',raw_slice)[0]
 max_plausible=now_ts+86400*3650
 if 1_600_000_000<=le_val<=max_plausible:
  return le_val
 if 1_600_000_000<=be_val<=max_plausible:
  return be_val
 return le_val

class Context:
 def __init__(self):
  self.id=os.environ['OZ_ADDON_ID']
  if not self.id.isdigit() or not 1<=int(self.id)<=999999:raise ValueError('Bad addon ID')
  self.data=no_links(os.environ['OZ_ADDON_DATA']);self.data.mkdir(parents=True,exist_ok=True,mode=0o700)
  self.config=self.data/'config.json'
  self.root=Path(os.environ.get('OZON_ROOT_DIR','/etc/ozon'))
 def is_gui_form(self):
  return os.environ.get('OZ_GUI_FORM','0')=='1' or os.environ.get('OZ_GUI_INTERNAL','0')=='1'
 def lease_status(self,now=None):
  lease_path=self.root/'native'/'runtime.lease'
  now_ts=int(time.time() if now is None else now)
  if not lease_path.is_file():
   return {'present':False,'sealed':False,'valid_size':False,'expires_at':None,'ttl_remaining':0,'lease_ttl_policy_seconds':LEASE_TTL_SECONDS,'expired':True}
  raw=lease_path.read_bytes()
  if len(raw)!=LEASE_BYTES:
   return {'present':True,'sealed':False,'valid_size':False,'expires_at':None,'ttl_remaining':0,'lease_ttl_policy_seconds':LEASE_TTL_SECONDS,'expired':True}
  exp=_unpack_lease_expiry(raw[32:40],now_ts)
  return {
   'present':True,
   'sealed':now_ts<=exp,
   'valid_size':True,
   'expires_at':exp,
   'ttl_remaining':max(0,int(exp-now_ts)),
   'lease_ttl_policy_seconds':LEASE_TTL_SECONDS,
   'expired':now_ts>exp
  }
 def shield_status(self):
  oz_bin=Path(os.environ.get('OZ_LAUNCHER_EXE','/usr/bin/oz'))
  native_elf=False
  if oz_bin.is_file():
   try:native_elf=oz_bin.read_bytes()[:4]==b'\x7fELF'
   except OSError:pass
  ndir=self.root/'native'
  vdoc=json.loads((self.root/'version.json').read_text()) if (self.root/'version.json').is_file() else {}
  ls=self.lease_status()
  return {
   'shield_engine':SHIELD_ENGINE,
   'shield_stack':SHIELD_STACK,
   'panel_version':vdoc.get('version',PANEL_VERSION),
   'ozonfs_version':OZONFS_VERSION,
   'native_elf':native_elf,
   'enrolled':(ndir/'enrolled').is_file(),
   'revoked':(ndir/'revoked.lock').is_file(),
   'ram_only_helper':not Path('/opt/ozon-runtime/bin/oz-native').exists(),
   'lease_sealed':ls['sealed'],
   'lease_ttl_remaining':ls['ttl_remaining'],
   'lease_ttl_policy_seconds':LEASE_TTL_SECONDS
  }
 def health_json(self):
  oz_bin=Path(os.environ.get('OZ_LAUNCHER_EXE','/usr/bin/oz'))
  if oz_bin.is_file():
   try:
    r=subprocess.run([str(oz_bin),'--health-json'],capture_output=True,text=True,timeout=5)
    if r.returncode==0 and r.stdout.strip().startswith('{'):
     return json.loads(r.stdout)
   except (OSError,subprocess.SubprocessError,json.JSONDecodeError):
    pass
  ls=self.lease_status()
  vdoc=json.loads((self.root/'version.json').read_text()) if (self.root/'version.json').is_file() else {}
  return {
   'ok':ls['sealed'] and not (self.root/'native'/'revoked.lock').is_file(),
   'version':vdoc.get('version',PANEL_VERSION),
   'sdk_version':SDK_VERSION,
   'shield_engine':SHIELD_ENGINE,
   'lease_sealed':ls['sealed'],
   'ttl_remaining':ls['ttl_remaining'],
   'source':'sdk-fallback'
  }
 def get(self,key,default=None):
  p=no_links(self.config);doc=json.loads(p.read_text()) if p.exists() else {}
  if not isinstance(doc,dict):raise ValueError('Invalid addon config')
  return doc.get(key,default)
 def set(self,key,value):
  if not re.fullmatch('[a-zA-Z0-9_.-]{1,80}',key):raise ValueError('Invalid config key')
  no_links(self.config)
  fd=os.open(self.data/'.config.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'a') as lock:
   (fcntl.flock if fcntl else (lambda *a,**k:None))(lock,fcntl.LOCK_EX);data=json.loads(self.config.read_text()) if self.config.exists() else {}
   if not isinstance(data,dict):raise ValueError('Invalid addon config')
   data[key]=value;fd,tmp=tempfile.mkstemp(dir=self.data)
   try:
    with os.fdopen(fd,'w') as f:os.fchmod(f.fileno(),0o600);json.dump(data,f,ensure_ascii=False);f.flush();os.fsync(f.fileno())
    os.replace(tmp,self.config)
   finally:Path(tmp).unlink(missing_ok=True)
 def log(self,message):
  fd=os.open(self.data/'addon.log',os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'a') as f:
   os.fchmod(f.fileno(),0o600);(fcntl.flock if fcntl else (lambda *a,**k:None))(f,fcntl.LOCK_EX);f.write(str(message).replace('\n',' ').replace('\r',' ')+'\n')
 def license_path(self):return str(self.root/'addons'/('license_'+self.id+'.key'))
 def t(self,key,default=None):
  locale=os.environ.get('OZ_LOCALE','en')
  if not re.fullmatch(r'[a-z]{2,3}(?:[-_][A-Za-z0-9]{2,8})*',locale):raise ValueError('Invalid locale')
  root=Path(os.environ['OZ_SDK_RELEASE']);manifest=json.loads((root/'manifest.json').read_text());locales=manifest.get('locales',{})
  for candidate in dict.fromkeys([locale,locale.split('_')[0].split('-')[0],'en','vi']):
   name=locales.get(candidate)
   if name is None:continue
   p=root/name
   if not isinstance(name,str) or Path(name).is_absolute() or '..' in Path(name).parts or not p.resolve().is_relative_to(root.resolve()):raise ValueError('Invalid locale file path')
   if p.is_file():
    doc=json.loads(p.read_text())
    if key in doc:return doc[key]
  return default if default is not None else key
 def api(self,path,method='GET',payload=None):
  base=os.environ['OZ_API_BASE'].rstrip('/');u=urllib.parse.urlsplit(base);relative=urllib.parse.urlsplit(path)
  if u.scheme!='https' and not (u.scheme=='http' and u.hostname in ('127.0.0.1','::1','localhost')):raise ValueError('API requires HTTPS or loopback HTTP')
  if not u.hostname or u.username or u.password or u.query or u.fragment:raise ValueError('Invalid API base URL')
  if not path.startswith('/') or path.startswith('//') or relative.scheme or relative.netloc or relative.fragment or any(ord(c)<32 for c in path):raise ValueError('Expected relative API path')
  method=method.upper()
  if method not in ('GET','POST','PUT','PATCH','DELETE','HEAD'):raise ValueError('Invalid HTTP method')
  req=urllib.request.Request(base+path,data=None if payload is None else json.dumps(payload).encode(),method=method,headers={'Authorization':'Bearer '+os.environ['OZ_API_TOKEN'],'Content-Type':'application/json'})
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:
   data=response.read(1024*1024+1)
   if len(data)>1024*1024:raise ValueError('API response too large')
   return json.loads(data)
 def api_call(self,resource,action,payload=None,method=None,confirm=False):
  if not re.fullmatch(r'[a-z][a-z0-9_]{0,39}',resource) or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}',action):raise ValueError('Invalid API resource/action')
  if method is None:
   method='GET' if action in _GET_ACTIONS else 'POST'
  body=dict(payload or {})
  if confirm and method!='GET':body['confirm']=True
  path=f'/api/v1/{resource}/{action}'
  if method=='GET' and body:
   path=path+'?'+urllib.parse.urlencode({k:('true' if v is True else ('false' if v is False else str(v))) for k,v in body.items()})
   body=None
  return self.api(path,method=method,payload=body if method!='GET' else None)
 def mail_antispam_dns(self,domain):
  if not re.fullmatch(r'[a-z0-9.-]+\.[a-z]{2,24}',domain.lower()):raise ValueError('Invalid mail domain')
  return self.api_call('mail','dkim_dns',{'domain':domain.lower()},method='GET')
 def mail_deliverability_audit(self,domain=''):
  payload={'domain':domain.lower()} if domain else {}
  return self.api_call('mail','audit',payload,method='GET')
 def file_action(self,operation,path,destination=None,content=None,conflict='rename',confirm=True):
  if operation not in ('create','mkdir','write','rename','copy','move','delete','chmod','chown','zip','extract','trash'):raise ValueError('Invalid fileops operation')
  body={'operation':operation,'path':str(path),'conflict':conflict}
  if destination is not None:body['destination']=str(destination)
  if content is not None:body['content']=str(content)
  return self.api_call('fileops','action',body,method='POST',confirm=confirm)
 def ssl_issue(self,domain,provider='letsencrypt',confirm=True):
  if not re.fullmatch(r'[a-z0-9.-]+\.[a-z]{2,24}',domain.lower()):raise ValueError('Invalid domain')
  if provider not in ('letsencrypt','zerossl'):raise ValueError('Invalid SSL provider')
  return self.api_call('ssl','issue',{'domain':domain.lower(),'provider':provider},method='POST',confirm=confirm)
 def hosting_action(self,kind,action,payload=None,confirm=False):
  resource={'all':'hosting','hosting':'hosting','node':'node_apps','go':'go_apps','python':'python_apps'}.get(kind)
  if not resource:raise ValueError('Invalid hosting kind')
  return self.api_call(resource,action,payload=payload,confirm=confirm)
 def dns_record(self,action,zone,payload=None,confirm=False):
  if not re.fullmatch(r'[a-z0-9.-]+\.[a-z]{2,24}',zone.lower()):raise ValueError('Invalid DNS zone')
  body=dict(payload or {},zone=zone.lower())
  return self.api_call('dns',action,payload=body,confirm=confirm)
 def notify_event(self,event,message,confirm=True):
  if not event or not message or len(str(message))>1500:raise ValueError('Invalid notification event/message')
  return self.api_call('notifications','event',{'event':str(event),'message':str(message)},method='POST',confirm=confirm)
 def control_job(self,action,params=None,idempotency_key=None,confirm=True):
  body=dict(params=params or {})
  if idempotency_key:body['idempotency_key']=str(idempotency_key)
  return self.api_call('control',action,payload=body,confirm=confirm)
 def panel_feature(self,feature_id=None):
  if feature_id is None:return self.api_call('panel','features',method='GET')
  fid=int(feature_id)
  if not 1<=fid<=46:raise ValueError('Feature ID must be 1..46')
  return self.api_call('panel','feature',{'id':fid},method='GET')
 def webserver_action(self,action,payload=None,confirm=False):
  return self.api_call('webserver',action,payload=payload,confirm=confirm)
 def database_action(self,action,payload=None,confirm=False):
  return self.api_call('database',action,payload=payload,confirm=confirm)
 def db_tables_list(self,name,engine='mysql'):
  if not name or not re.fullmatch(r'[a-zA-Z0-9_.-]{1,64}',str(name)):raise ValueError('Invalid database name')
  if engine not in ('mysql','postgresql'):raise ValueError('Invalid database engine')
  return self.api_call('database','tables_list',{'name':str(name),'engine':engine},method='GET')
 def docker_action(self,action,payload=None,confirm=False):
  return self.api_call('docker',action,payload=payload,confirm=confirm)
 def swap_action(self,action,payload=None,confirm=False):
  return self.api_call('swap',action,payload=payload,confirm=confirm)
 def waf_action(self,action,payload=None,confirm=False):
  return self.api_call('waf',action,payload=payload,confirm=confirm)
 def backup_action(self,action,payload=None,confirm=False):
  return self.api_call('backup',action,payload=payload,confirm=confirm)
 def ai_action(self,action,payload=None,confirm=False):
  return self.api_call('ai',action,payload=payload,confirm=confirm)
 def ai_cache_stats(self,clear=False):
  return self.api_call('ai','cache_stats',{'clear':bool(clear)} if clear else None,method='GET')
 def ai_config_inspect(self,path):
  p=str(path or '').strip()
  if not p.startswith('/') or '..' in Path(p).parts:raise ValueError('Absolute safe config path required')
  return self.api_call('ai','config_inspect',{'path':p},method='GET')
 def ai_config_repair(self,path,old_text,new_text,confirm=True):
  p=str(path or '').strip()
  if not p.startswith('/') or '..' in Path(p).parts:raise ValueError('Absolute safe config path required')
  return self.api_call('ai','config_repair',{'path':p,'old_text':str(old_text),'new_text':str(new_text)},method='POST',confirm=confirm)
 def app_pulse(self):
  return self.api_call('app','pulse',method='GET')
 def app_bootstrap(self):
  return self.api_call('app','bootstrap',method='GET')
 def webhooks_action(self,action='list',payload=None,confirm=False):
  if action not in ('list','create','delete','test','deliveries'):raise ValueError('Invalid webhooks action')
  return self.api_call('webhooks',action,payload=payload,confirm=confirm)
 def iam_action(self,resource,action,payload=None,confirm=False):
  if resource not in ('iam','users','departments','groups','roles','policy','permissions','missions'):
   raise ValueError('Invalid IAM resource')
  return self.api_call(resource,action,payload=payload,confirm=confirm)
 def chatops_command(self,message,channel='sdk',actor='addon',confirm=True):
  msg=str(message or '').strip()
  if not msg:raise ValueError('ChatOps message required')
  return self.api_call('ai','chatops',payload={'message':msg,'channel':channel,'actor':actor},method='POST',confirm=confirm)
 def sso_link(self,target,name='',user='',confirm=True):
  if target not in ('database','ozonfs','webmail','gui'):raise ValueError('Invalid SSO target')
  return self.api_call('ai','sso_generate',payload={'target':target,'name':name,'user':user},method='POST',confirm=confirm)
 def cloudflare_delete_records(self,domain,record_type='',confirm=True):
  if not domain or '.' not in domain:raise ValueError('Valid domain required')
  return self.api_call('cloudflare','delete_records',payload={'domain':domain,'type':record_type},method='POST',confirm=confirm)
 def analytics_3d_report(self,domain='',confirm=True):
  return self.api_call('analytics','report_3d',payload={'domain':domain},method='POST',confirm=confirm)
 def ai_watchdog_status(self):
  st_dir=self.root/'ai_assistant'/'state'
  cursors=json.loads((st_dir/'log_cursors.json').read_text()) if (st_dir/'log_cursors.json').is_file() else {}
  reported=json.loads((st_dir/'reported_signatures.json').read_text()) if (st_dir/'reported_signatures.json').is_file() else {}
  return {'panel_version':PANEL_VERSION,'incremental_cursors':cursors,'suppressed_count':len(reported) if isinstance(reported,dict) else 0}
 def local_ops(self,subcommand,*args,payload=None):
  if not re.fullmatch(r'[a-z][a-z0-9_-]{0,39}',subcommand):raise ValueError('Invalid local-ops subcommand')
  oz_bin='/usr/bin/oz'
  if not Path(oz_bin).is_file():raise ValueError('/usr/bin/oz is not installed')
  inp=None if payload is None else (json.dumps(payload) if isinstance(payload,(dict,list)) else str(payload))
  r=subprocess.run([oz_bin,'--local-ops',subcommand,*map(str,args)],input=inp,capture_output=True,text=True,timeout=120)
  if r.returncode!=0:raise ValueError(r.stderr.strip() or f'local-ops {subcommand} failed with exit {r.returncode}')
  try:return json.loads(r.stdout)
  except json.JSONDecodeError:return {'ok':True,'output':r.stdout.strip()}
 def edit(self,file):
  editor=os.environ.get('EDITOR','vi')
  if '/' not in editor and not re.fullmatch('[a-zA-Z0-9_.-]+',editor):raise ValueError('EDITOR must be a command name or full path')
  return subprocess.run([editor,str(file)]).returncode
 def os(self):
  release={}
  for line in Path('/etc/os-release').read_text().splitlines():
   if '=' in line and not line.startswith('#'):
    k,v=line.split('=',1);release[k]=v.strip('"\'')
  name=release.get('ID');version=release.get('VERSION_ID','');major=version.split('.')[0]
  allowed=(name in ('almalinux','rocky') and major in ('8','9','10')) if EDITION=='el' else (name=='ubuntu' and version in ('18.04','20.04','22.04','24.04','24.10','25.04','25.10','26.04') or name=='debian' and major in ('10','11','12','13','14'))
  if not allowed:raise ValueError('Unsupported OS for helper edition '+EDITION)
  return release
 def install_packages(self,*names):
  self.os()
  if not names or any(not isinstance(x,str) or not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_+.-]*',x) for x in names):raise ValueError('Invalid native package name')
  command=['dnf','-y','install'] if EDITION=='el' else ['apt-get','install','-y','--no-install-recommends']
  return subprocess.run(command+list(names),check=True).returncode
 def service(self,action,unit):
  self.os()
  if action not in ('status','is-active','start','stop','restart','reload','enable','disable'):raise ValueError('Invalid service action')
  if not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_.@-]*',unit):raise ValueError('Invalid service unit')
  aliases={'apache2':'httpd','ssh':'sshd','cron':'crond'} if EDITION=='el' else {'httpd':'apache2','sshd':'ssh','crond':'cron'}
  suffix='.service' if unit.endswith('.service') else '';name=unit[:-8] if suffix else unit
  return subprocess.run(['systemctl',action,aliases.get(name,name)+suffix]).returncode
 def verify_license(self,document,signature,public,product):
  cli=os.environ.get('OZ_SDK_CLI')
  if not cli:raise ValueError('SDK runtime did not export OZ_SDK_CLI')
  subprocess.run([sys.executable,cli,'license-verify',str(document),str(signature),str(public),'--product',product],check=True)
  return True
 def check_core_entitlement(self):
  r=subprocess.run(['/usr/bin/oz','--addon-entitlement',str(self.id)],capture_output=True,text=True,timeout=15)
  return r.returncode==0

def main():
 c=Context();args=sys.argv[1:]
 if not args:raise ValueError('Expected helper operation')
 op=args[0]
 if op=='get':print(json.dumps(c.get(args[1])))
 elif op=='set':
  value=sys.stdin.read(1024*1024+1)
  if len(value)>1024*1024:raise ValueError('Config value too large')
  c.set(args[1],json.loads(value))
 elif op=='os':print(json.dumps(c.os()))
 elif op=='shield-status':print(json.dumps(c.shield_status(),ensure_ascii=False))
 elif op=='lease-status':print(json.dumps(c.lease_status(),ensure_ascii=False))
 elif op=='health-json':print(json.dumps(c.health_json(),ensure_ascii=False))
 elif op=='ai-watchdog-status':print(json.dumps(c.ai_watchdog_status(),ensure_ascii=False))
 elif op=='ai-cache':print(json.dumps(c.ai_cache_stats(clear=('--clear' in args[1:])),ensure_ascii=False))
 elif op=='config-inspect':print(json.dumps(c.ai_config_inspect(args[1]),ensure_ascii=False))
 elif op=='app-pulse':print(json.dumps(c.app_pulse(),ensure_ascii=False))
 elif op=='webhooks':
  act=args[1] if len(args)>1 else 'list'
  data=sys.stdin.read(1024*1024+1) if not sys.stdin.isatty() else ''
  payload=json.loads(data) if data.strip() else None
  print(json.dumps(c.webhooks_action(act,payload=payload,confirm=('--confirm' in args[2:])),ensure_ascii=False))
 elif op=='db-tables':
  eng=args[2] if len(args)>2 else 'mysql'
  print(json.dumps(c.db_tables_list(args[1],eng),ensure_ascii=False))
 elif op=='chatops':print(json.dumps(c.chatops_command(' '.join(args[1:])),ensure_ascii=False))
 elif op=='sso-link':print(json.dumps(c.sso_link(args[1],args[2] if len(args)>2 else '',args[3] if len(args)>3 else ''),ensure_ascii=False))
 elif op=='t':print(c.t(args[1],args[2] if len(args)>2 else None))
 elif op=='log':c.log(' '.join(args[1:]))
 elif op=='edit':return c.edit(args[1])
 elif op=='service':return c.service(args[1],args[2])
 elif op=='api':
  method=args[2] if len(args)>2 else 'GET';payload=None
  if method.upper() not in ('GET','HEAD'):
   data=sys.stdin.read(1024*1024+1)
   if len(data)>1024*1024:raise ValueError('API request too large')
   if data.strip():payload=json.loads(data)
  print(json.dumps(c.api(args[1],method,payload)))
 elif op=='api-call':
  resource=args[1];action=args[2];confirm=('--confirm' in args[3:])
  data=sys.stdin.read(1024*1024+1) if not sys.stdin.isatty() else ''
  payload=json.loads(data) if data.strip() else None
  print(json.dumps(c.api_call(resource,action,payload=payload,confirm=confirm),ensure_ascii=False))
 elif op=='local-ops':
  data=sys.stdin.read(1024*1024+1) if not sys.stdin.isatty() else None
  print(json.dumps(c.local_ops(args[1],*args[2:],payload=data),ensure_ascii=False))
 else:raise ValueError('Unknown helper operation')
 return 0

if __name__=='__main__':
 try:sys.exit(main())
 except (ValueError,KeyError,IndexError,OSError,subprocess.SubprocessError) as e:print('[OZ addon] '+str(e),file=sys.stderr);sys.exit(1)
