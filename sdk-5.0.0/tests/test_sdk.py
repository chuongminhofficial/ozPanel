import contextlib,hashlib,importlib.util,io,json,os,struct,subprocess,sys,tarfile,tempfile,time,types,unittest,urllib.error,threading
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('sdk_under_test',HERE/'ozsdk.py');sdk=importlib.util.module_from_spec(spec);spec.loader.exec_module(sdk)
spec=importlib.util.spec_from_file_location('helper_under_test',HERE/'lib/ozaddon.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
class SDKTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.keys=tempfile.TemporaryDirectory();cls.private=Path(cls.keys.name)/'private.pem';cls.public=Path(cls.keys.name)/'public.pem'
  cls.private.write_bytes(sdk.openssl(['genpkey','-algorithm','ED25519']));cls.public.write_bytes(sdk.openssl(['pkey','-pubout','-in',str(cls.private)]))
 @classmethod
 def tearDownClass(cls):cls.keys.cleanup()
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.root=self.base/'panel';self.root.mkdir();(self.root/'version.json').write_text('{"version":"9.1.2"}')
  self.project=self.base/'project';self.output=self.base/'release.ozaddon'
  self.os_patch=patch.object(sdk,'os_release',return_value={'ID':'rocky','VERSION_ID':'9.6'} if sdk.EDITION=='el' else {'ID':'debian','VERSION_ID':'12'});self.os_patch.start()
  with contextlib.redirect_stdout(io.StringIO()):sdk.init(types.SimpleNamespace(path=str(self.project),id='9002',publisher='test-studio'))
  (self.project/'bin/main.sh').write_text('#!/bin/bash\nexit 0\n')
 def tearDown(self):self.os_patch.stop();self.temp.cleanup()
 def cli(self,*args):
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),*map(str,args)]),contextlib.redirect_stdout(io.StringIO()):return sdk.main()
 def manifest(self,**changes):
  m=json.loads((self.project/'manifest.json').read_text());m.update(changes);(self.project/'manifest.json').write_text(json.dumps(m));return m
 def package(self,signed=True):
  m,files=sdk.project(self.project);self.output.write_bytes(sdk.archive_bytes(m,files,self.private if signed else None));return self.output
 def trust(self,publisher='test-studio'):
  sdk.write(self.root/'sdk-trust'/publisher/'public.pem',self.public.read_bytes(),0o644)
 def install(self):self.trust();self.package();self.cli('install',self.output,'--confirm')
 def test_example_project_is_valid(self):sdk.project(HERE/'examples/native')
 def test_schema_boolean_rejected(self):
  m=self.manifest(schema=True)
  with self.assertRaises(ValueError):sdk.check_manifest(m)
 def test_bad_id_rejected(self):
  for value in (True,0,1000000,'9002'):
   with self.subTest(value=value),self.assertRaises(ValueError):sdk.check_manifest(self.manifest(id=value))
 def test_bad_hook_and_locale_rejected(self):
  for changes in [dict(hooks=[]),dict(hooks={'install':'../bad'}),dict(locales={'../../etc':'bad.json'})]:
   with self.subTest(changes=changes),self.assertRaises(ValueError):sdk.check_manifest(self.manifest(**changes))
 def test_secret_not_packed(self):
  (self.project/'.env').write_text('SECRET=private')
  with self.assertRaises(ValueError):sdk.project(self.project)
 def test_symlink_not_packed(self):
  (self.project/'escape').symlink_to('/etc/passwd')
  with self.assertRaises(ValueError):sdk.project(self.project)
 def test_package_is_reproducible(self):
  m,files=sdk.project(self.project);self.assertEqual(sdk.archive_bytes(m,files,self.private),sdk.archive_bytes(m,files,self.private))
 def malicious_archive(self,members):
  with tarfile.open(self.output,'w:gz') as t:
   for name,link in members:
    member=tarfile.TarInfo(name)
    if link:member.type=tarfile.SYMTYPE;member.linkname=link;t.addfile(member)
    else:member.size=2;t.addfile(member,io.BytesIO(b'{}'))
 def test_path_traversal_archive_rejected(self):
  self.malicious_archive([('../manifest.json',None)])
  with self.assertRaises(ValueError):sdk.unpack(self.output)
 def test_link_archive_rejected(self):
  self.malicious_archive([('manifest.json','/etc/passwd')])
  with self.assertRaises(ValueError):sdk.unpack(self.output)
 def test_duplicate_archive_rejected(self):
  self.malicious_archive([('manifest.json',None),('manifest.json',None)])
  with self.assertRaises(ValueError):sdk.unpack(self.output)
 def test_checksum_tamper_rejected(self):
  m,files=sdk.project(self.project);files['bin/main.sh']=b'changed';self.output.write_bytes(sdk.archive_bytes(m,files,self.private))
  with self.assertRaises(ValueError):sdk.unpack(self.output)
 def test_trusted_publisher_cannot_bypass_signature(self):
  self.trust();m,data=sdk.unpack(self.package(False))
  with self.assertRaises(ValueError):sdk.check_trust(m,data,self.root,True)
 def test_unsigned_development_is_explicit(self):
  m,data=sdk.unpack(self.package(False))
  with self.assertRaises(ValueError):sdk.check_trust(m,data,self.root,False)
  sdk.check_trust(m,data,self.root,True)
 def test_invalid_signature_rejected(self):
  self.trust();m,data=sdk.unpack(self.package());data['manifest.sig']=b'x'*64
  with self.assertRaises(ValueError):sdk.check_trust(m,data,self.root)
 def test_platform_matrix(self):
  m=sdk.project(self.project)[0]
  allowed=[('rocky','9.6'),('rocky','10'),('almalinux','9'),('almalinux','10.1')] if sdk.EDITION=='el' else [('ubuntu','22.04'),('ubuntu','24.04'),('debian','11'),('debian','12'),('debian','13')]
  for name,version in allowed:
   with self.subTest(name=name,version=version),patch.object(sdk,'os_release',return_value={'ID':name,'VERSION_ID':version}):sdk.platform_check(m,self.root)
  with patch.object(sdk,'os_release',return_value={'ID':'centos','VERSION_ID':'9'}),self.assertRaises(ValueError):sdk.platform_check(m,self.root)
 def test_target_panel_version_checked_at_install(self):
  self.manifest(min_panel_version='9.0.0');self.package();self.trust()
  with self.assertRaises(ValueError):self.cli('install',self.output,'--confirm')
 def test_signature_install_run_health(self):
  self.install();self.assertEqual(self.cli('run','9002'),0);self.assertEqual(self.cli('health','9002'),0)
 def test_install_requires_confirmation(self):
  self.package();self.trust()
  with self.assertRaises(ValueError):self.cli('install',self.output)
 def test_failed_initial_hook_does_not_register(self):
  (self.project/'hooks/install.sh').write_text('#!/bin/bash\nexit 3\n');self.trust();self.package()
  with self.assertRaises(ValueError):self.cli('install',self.output,'--confirm')
  self.assertNotIn('9002',sdk.registry(self.root))
 def test_failed_upgrade_keeps_previous(self):
  self.install();self.manifest(version='1.0.1');(self.project/'hooks/health.sh').write_text('#!/bin/bash\nexit 4\n');self.package()
  with self.assertRaises(ValueError):self.cli('install',self.output,'--confirm')
  self.assertEqual(sdk.registry(self.root)['9002']['version'],'1.0.0')
 def test_upgrade_rollback_remove_preserves_data(self):
  self.install();data=self.root/'addon-data/9002/note';data.write_text('preserve');self.manifest(version='1.0.1');self.package();self.cli('install',self.output,'--confirm');self.cli('rollback','9002','--confirm')
  self.assertEqual(sdk.registry(self.root)['9002']['version'],'1.0.0');self.cli('remove','9002','--confirm');self.assertTrue(data.exists());self.assertNotIn('9002',sdk.registry(self.root))
 def test_remove_can_explicitly_purge_data(self):
  self.install();data=self.root/'addon-data/9002';(data/'note').write_text('remove');self.cli('remove','9002','--confirm','--purge-data');self.assertFalse(data.exists())
 def test_modified_installed_file_rejected(self):
  self.install();(self.root/'sdk-releases/9002/1.0.0/bin/main.sh').write_text('changed')
  with self.assertRaises(ValueError):self.cli('run','9002')
 def test_hook_cannot_silently_change_payload(self):
  (self.project/'hooks/install.sh').write_text('#!/bin/bash\nprintf changed > "$OZ_SDK_RELEASE/bin/main.sh"\n');self.trust();self.package()
  with self.assertRaises(ValueError):self.cli('install',self.output,'--confirm')
  self.assertNotIn('9002',sdk.registry(self.root))
 def test_registration_failure_restores_previous_release(self):
  self.install();self.manifest(version='1.0.1');self.package()
  with patch.object(sdk,'commit_row',side_effect=OSError('disk full')),self.assertRaises(OSError):self.cli('install',self.output,'--confirm')
  self.assertEqual(sdk.registry(self.root)['9002']['version'],'1.0.0');self.assertFalse((self.root/'sdk-releases/9002/1.0.1').exists())
 def test_publisher_mismatch_rejected(self):
  self.install();self.manifest(publisher='other-studio',version='1.0.1');self.trust('other-studio');self.package()
  with self.assertRaises(ValueError):self.cli('install',self.output,'--confirm')
 def test_legacy_launcher_preserves_core_contract(self):
  self.install();runtime=self.base/'runtime';runtime.mkdir();(runtime/'ozsdk.py').write_text('# fixture')
  with patch.object(sdk,'runtime_path',return_value=runtime):sdk.legacy_launcher(self.root,'9002','1.0.0')
  path=self.root/'addons/addon_9002.sh';subprocess.run(['bash','-n',str(path)],check=True);self.assertIn(sdk.marker('9002'),path.read_text());self.assertEqual((self.root/'addons/addon_9002.version').read_text(),'1.0.0\n')
 def test_legacy_bundle_signed_and_valid_bash(self):
  self.cli('pack',self.project,'--out',self.base/'addon.sh','--private',self.private,'--legacy');out=self.base/'addon.sh';subprocess.run(['bash','-n',str(out)],check=True);text=out.read_text();self.assertIn(' verify ',text);self.assertNotIn(' trust ',text);self.assertTrue(Path(str(out)+'.sha256').exists())
 def test_catalog_has_ten_fields_and_rejects_native_package_url(self):
  out=self.base/'catalog.txt';self.cli('catalog',self.project,'--url','https://example.com/addon.sh','--out',out);self.assertEqual(len(out.read_text().strip().split('|')),10)
  with self.assertRaises(ValueError):self.cli('catalog',self.project,'--url','https://example.com/addon.ozaddon')
 def test_license_valid_wrong_product_and_expiry(self):
  out=self.base/'license.json';self.cli('license-sign','--private',self.private,'--product','demo','--expires-at',str(int(time.time())+3600),'--out',out)
  sdk.verify_offline_license(out,str(out)+'.sig',self.public,'demo')
  with self.assertRaises(ValueError):sdk.verify_offline_license(out,str(out)+'.sig',self.public,'wrong')
  with self.assertRaises(ValueError):sdk.verify_offline_license(out,str(out)+'.sig',self.public,'demo',now=time.time()+7200)
 def test_cryptography_backend_compatible(self):
  try:import cryptography
  except ImportError:self.skipTest('Optional cryptography backend not installed')
  data=b'Ed25519 interop fixture';signature=sdk.sign(data,self.private)
  with patch.object(sdk,'crypto_backend',return_value='cryptography'):
   sdk.verify_signature(data,signature,self.public);other=sdk.sign(data,self.private)
  sdk.verify_signature(data,other,self.public)
 def context(self):
  env=dict(OZ_ADDON_ID='9002',OZ_ADDON_DATA=str(self.base/'data'),OZ_SDK_RELEASE=str(self.project),OZON_ROOT_DIR=str(self.root))
  with patch.dict(os.environ,env):return helper.Context()
 def test_config_is_private_atomic_and_not_symlinked(self):
  ctx=self.context();ctx.set('note',{'value':1});self.assertEqual(ctx.get('note'),{'value':1});self.assertEqual(ctx.config.stat().st_mode&0o777,0o600)
  ctx.config.unlink();ctx.config.symlink_to(self.base/'outside')
  with self.assertRaises(ValueError):ctx.set('note','bad')
 def test_locale_mapping_and_fallback(self):
  (self.project/'translations').mkdir();(self.project/'translations/en.json').write_text('{"greet":"Hello"}');self.manifest(locales={'en':'translations/en.json'});ctx=self.context()
  with patch.dict(os.environ,dict(OZ_SDK_RELEASE=str(self.project),OZ_LOCALE='fr_FR')):self.assertEqual(ctx.t('greet'),'Hello')
  with patch.dict(os.environ,dict(OZ_SDK_RELEASE=str(self.project),OZ_LOCALE='../../etc')):
   with self.assertRaises(ValueError):ctx.t('greet')
 def test_native_package_helpers_and_option_rejection(self):
  ctx=self.context()
  with patch.object(ctx,'os',return_value={}),patch.object(helper.subprocess,'run') as call:
   call.return_value.returncode=0;ctx.install_packages('jq');self.assertEqual(call.call_args.args[0][0],'dnf' if sdk.EDITION=='el' else 'apt-get')
   with self.assertRaises(ValueError):ctx.install_packages('--nogpgcheck')
 def test_api_rejects_remote_http_and_external_path(self):
  ctx=self.context()
  with patch.dict(os.environ,dict(OZ_API_BASE='http://remote.example',OZ_API_TOKEN='secret')):
   with self.assertRaises(ValueError):ctx.api('/api/v1/status')
  with patch.dict(os.environ,dict(OZ_API_BASE='https://api.example',OZ_API_TOKEN='secret')):
   for path in ('//evil.example/','https://evil.example/','/path#fragment'):
    with self.assertRaises(ValueError):ctx.api(path)
 def test_api_does_not_follow_redirect_with_token(self):
  from http.server import BaseHTTPRequestHandler,HTTPServer
  hits=[]
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):
    hits.append(self.path);self.send_response(302);self.send_header('Location','/target');self.end_headers()
  server=HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with patch.dict(os.environ,dict(OZ_API_BASE='http://127.0.0.1:'+str(server.server_port),OZ_API_TOKEN='fixture-token')):
    with self.assertRaises(urllib.error.HTTPError):self.context().api('/redirect')
   self.assertEqual(hits,['/redirect'])
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
 def test_addon_locks_are_independent(self):
  code='import importlib.util,sys,time;from pathlib import Path;s=importlib.util.spec_from_file_location("sdk",sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nwith m.lock(Path(sys.argv[2]),"9002"):\n print("READY",flush=True);time.sleep(10)\n'
  proc=subprocess.Popen([sys.executable,'-c',code,str(HERE/'ozsdk.py'),str(self.root)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   self.assertEqual(proc.stdout.readline().strip(),'READY');start=time.monotonic()
   with sdk.lock(self.root,'9003'):pass
   self.assertLess(time.monotonic()-start,1)
  finally:proc.terminate();proc.communicate(timeout=3)
 def test_v723_api_catalog_and_resource_filter(self):
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'api-catalog']),contextlib.redirect_stdout(buf):sdk.main()
  cat=json.loads(buf.getvalue());self.assertEqual(cat['version'],'9.1.4');self.assertEqual(cat['shield_engine'],'OZV8-Fortress+');self.assertIn('mail',cat['resources']);self.assertIn('fileops',cat['resources']);self.assertIn('ssl',cat['resources'])
  buf2=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'api-catalog','--resource','mail']),contextlib.redirect_stdout(buf2):sdk.main()
  mcat=json.loads(buf2.getvalue());self.assertIn('dkim_dns',mcat['mail']);self.assertIn('audit',mcat['mail'])
 def test_v723_core_status_and_trust_commands(self):
  (self.root/'mail').mkdir(parents=True,exist_ok=True);(self.root/'mail/domains.list').write_text('example.com|ACTIVE\n')
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'core-status']),contextlib.redirect_stdout(buf):sdk.main()
  st=json.loads(buf.getvalue());self.assertEqual(st['installed_version'],'9.1.4');self.assertEqual(st['shield_engine'],'OZV8-Fortress+');self.assertEqual(st['mail_domains'],['example.com'])
  buf2=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'core-trust-cmd','--id','9002','--public',str(self.public),'--product','pro-suite']),contextlib.redirect_stdout(buf2):sdk.main()
  tc=json.loads(buf2.getvalue());self.assertEqual(tc['addon_id'],9002);self.assertIn('--addon-license-trust 9002',tc['commands']['core_trust'])
 def test_v723_manifest_category_and_gui_workbench(self):
  m=self.manifest(category='mail',gui_workbench={'actions':[{'key':'1','label':'Kiểm tra SPF/DKIM'}]})
  sdk.check_manifest(m)
  with self.assertRaises(ValueError):sdk.check_manifest(self.manifest(category='invalid-cat'))
  with self.assertRaises(ValueError):sdk.check_manifest(self.manifest(gui_workbench={'actions':['bad']}))
 def test_v723_typed_api_call_and_mail_file_helpers(self):
  from http.server import BaseHTTPRequestHandler,HTTPServer
  calls=[]
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):
    calls.append(('GET',self.path,None));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true,"records":["SPF","DKIM","DMARC"]}')
   def do_POST(self):
    length=int(self.headers.get('Content-Length','0'));body=json.loads(self.rfile.read(length)) if length else {}
    calls.append(('POST',self.path,body));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
  server=HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with patch.dict(os.environ,dict(OZ_API_BASE='http://127.0.0.1:'+str(server.server_port),OZ_API_TOKEN='tok-732')):
    ctx=self.context()
    r1=ctx.mail_antispam_dns('example.com');self.assertTrue(r1['ok'])
    r2=ctx.file_action('copy','/var/www/a.txt','/var/www/b.txt',conflict='rename',confirm=True);self.assertTrue(r2['ok'])
    r3=ctx.ssl_issue('example.com',provider='letsencrypt',confirm=True);self.assertTrue(r3['ok'])
   self.assertEqual(calls[0][0],'GET');self.assertIn('/api/v1/mail/dkim_dns?domain=example.com',calls[0][1])
   self.assertEqual(calls[1][0],'POST');self.assertTrue(calls[1][2]['confirm']);self.assertEqual(calls[1][2]['operation'],'copy')
   self.assertEqual(calls[2][0],'POST');self.assertEqual(calls[2][2]['provider'],'letsencrypt')
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
 def test_v723_bash_shimmer_and_gui_form_detection(self):
  cmd=f'source "{HERE}/lib/ozaddon.sh"; OZ_GUI_FORM=1 oz_is_gui_form && OZ_NO_ANIM=1 oz_shimmer_banner "Hello 7.3.2"'
  r=subprocess.run(['bash','-c',cmd],capture_output=True,text=True,timeout=10)
  self.assertEqual(r.returncode,0,r.stderr);self.assertIn('Hello 7.3.2',r.stdout)
 def test_v728_expanded_api_catalog_35_resources(self):
  cat=sdk.API_V732_CATALOG
  self.assertGreaterEqual(len(cat['resources']),112)
  for rname in ('node_apps','go_apps','python_apps','automation','panel','updates','licensing','preferences','operations','control'):
   self.assertIn(rname,cat['resources'])
 def test_v728_shield_status_and_enrollment_detection(self):
  ndir=self.root/'native';ndir.mkdir(parents=True,exist_ok=True)
  (ndir/'enrolled').write_text('1\n')
  (ndir/'device.json').write_text('{"device_id":"dev-ozv7-test"}')
  fake_oz=self.base/'fake_oz';fake_oz.write_bytes(b'\x7fELF\x02\x01\x01\x00')
  with patch.dict(os.environ,{'OZ_LAUNCHER_EXE':str(fake_oz)}):
   st=sdk.inspect_shield_status(self.root)
   self.assertTrue(st['native_elf_launcher'])
   self.assertTrue(st['device_enrolled'])
   self.assertEqual(st['device_id'],'dev-ozv7-test')
   self.assertFalse(st['device_revoked'])
   self.assertEqual(st['shield_engine'],'OZV8-Fortress+')
   (ndir/'revoked.lock').write_text('revoked\n')
   st2=sdk.inspect_shield_status(self.root)
   self.assertTrue(st2['device_revoked'])
 def test_v728_ozv5_shield_compliance_auditor(self):
  rep=sdk.audit_project(self.project)
  self.assertTrue(rep['compatible'])
  (self.project/'bin/main.sh').write_text('#!/bin/bash\n/usr/bin/oz --native-source\n')
  rep_bad=sdk.audit_project(self.project)
  self.assertFalse(rep_bad['compatible'])
  self.assertEqual(rep_bad['issues'][0]['rule'],'ozv5-shield-boundary')
  with self.assertRaises(ValueError):self.cli('audit',self.project)
 def test_v728_audit_detects_keyless_module_direct_import_and_preload(self):
  (self.project/'bin/main.sh').write_text('#!/bin/bash\nLD_PRELOAD=/tmp/x.so python3 /etc/ozon/gui/server.py\n')
  rep=sdk.audit_project(self.project)
  self.assertFalse(rep['compatible'])
  self.assertGreaterEqual(len(rep['issues']),2)
 def test_v728_37_os_platform_manifest_support(self):
  m=self.manifest(platforms=['ubuntu:24.04','debian:12','almalinux:9','rocky:9','centos-stream:9','rhel:9','ol:9','cloudlinux:9'])
  sdk.check_manifest(m)
  with patch.object(sdk,'EDITION','universal'):
   for distro,ver,_,_ in sdk.PLATFORM_ROWS:
    with patch.object(sdk,'os_release',return_value={'ID':distro,'VERSION_ID':ver}):
     sdk.platform_check(self.manifest(platforms=[f'{distro}:{ver}']),self.root)
 def test_v728_internal_and_quarantined_addons_in_core_status(self):
  rec_dir=self.root/'addons/.internal/records';rec_dir.mkdir(parents=True,exist_ok=True)
  (rec_dir/'900001.json').write_text(json.dumps({'id':900001,'name':'Local1','version':'1.0.0','status':'active'}))
  (rec_dir/'900002.json').write_text(json.dumps({'id':900002,'name':'Local2','version':'1.0.0','status':'quarantined'}))
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'core-status']),contextlib.redirect_stdout(buf):sdk.main()
  st=json.loads(buf.getvalue())
  self.assertEqual(st['internal_addons'],[900001,900002])
  self.assertEqual(st['quarantined_addons'],[900002])
 def test_v728_typed_hosting_dns_notify_control_helpers(self):
  from http.server import BaseHTTPRequestHandler,HTTPServer
  calls=[]
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):
    calls.append(('GET',self.path,None));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
   def do_POST(self):
    length=int(self.headers.get('Content-Length','0'));body=json.loads(self.rfile.read(length)) if length else {}
    calls.append(('POST',self.path,body));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
  server=HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with patch.dict(os.environ,dict(OZ_API_BASE='http://127.0.0.1:'+str(server.server_port),OZ_API_TOKEN='tok-732')):
    ctx=self.context()
    self.assertTrue(ctx.hosting_action('go','list')['ok'])
    self.assertTrue(ctx.dns_record('records','example.com')['ok'])
    self.assertTrue(ctx.notify_event('addon.deploy','Deployed v3.0.0')['ok'])
    self.assertTrue(ctx.control_job('cache_tune',{'service':'redis'},idempotency_key='idem-12345678')['ok'])
    self.assertTrue(ctx.panel_feature(15)['ok'])
   self.assertEqual(calls[0][1],'/api/v1/go_apps/list')
   self.assertIn('/api/v1/dns/records?zone=example.com',calls[1][1])
   self.assertEqual(calls[2][1],'/api/v1/notifications/event')
   self.assertEqual(calls[3][1],'/api/v1/control/cache_tune')
   self.assertIn('/api/v1/panel/feature?id=15',calls[4][1])
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
 def test_v728_helper_shield_status_cli(self):
  ctx=self.context()
  st=ctx.shield_status()
  self.assertEqual(st['shield_engine'],'OZV8-Fortress+')
  self.assertEqual(st['panel_version'],'9.1.4')
 def test_v732_full_112_resources_and_745_operations_catalog(self):
  cat=sdk.API_V732_CATALOG
  self.assertEqual(cat['version'],'9.1.4')
  self.assertEqual(cat['ozonfs_version'],'9.1.4')
  self.assertEqual(cat['sdk_version'],'5.0.0')
  self.assertGreaterEqual(cat['total_resources'],112)
  self.assertGreaterEqual(cat['total_operations'],745)
  for i in range(1,47):
   self.assertIn(f'feature_{i:02d}',cat['resources'])
  for r in ('webserver','database','docker','swap','malware','monitor','analytics','gateway','ai','loadbalancer','securefolder','ddos','missions','departments','groups','roles','auth','acl'):
   self.assertIn(r,cat['resources'])
 def test_v732_api_catalog_summary_and_group_filter(self):
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'api-catalog','--summary']),contextlib.redirect_stdout(buf):sdk.main()
  s=json.loads(buf.getvalue())
  self.assertGreaterEqual(s['total_resources'],112)
  buf2=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'api-catalog','--group','cli_bridge']),contextlib.redirect_stdout(buf2):sdk.main()
  g=json.loads(buf2.getvalue())
  self.assertEqual(g['count'],46)
 def test_v732_ozv7_fortress_72byte_boot_bound_lease_inspection(self):
  ndir=self.root/'native';ndir.mkdir(parents=True,exist_ok=True)
  st_missing=sdk.inspect_lease_status(self.root)
  self.assertFalse(st_missing['present'])
  self.assertFalse(st_missing['sealed'])
  now=int(time.time())
  exp=now+600
  lease_bytes=(b'A'*32)+struct.pack('>Q',exp)+(b'M'*32)
  (ndir/'runtime.lease').write_bytes(lease_bytes)
  st_valid=sdk.inspect_lease_status(self.root,now=now)
  self.assertTrue(st_valid['present'])
  self.assertTrue(st_valid['valid_size'])
  self.assertTrue(st_valid['sealed'])
  self.assertEqual(st_valid['expires_at'],exp)
  self.assertEqual(st_valid['ttl_remaining'],600)
  st_expired=sdk.inspect_lease_status(self.root,now=exp+10)
  self.assertTrue(st_expired['expired'])
  self.assertFalse(st_expired['sealed'])
 def test_v732_audit_blocks_ozv7_ipc_and_ram_helper_and_lease_tamper(self):
  (self.project/'bin/main.sh').write_text('#!/bin/bash\n/usr/bin/oz --ozv7-helper\n/opt/ozon-runtime/bin/oz-native lease-status\ncat /etc/ozon/native/runtime.lease\n')
  rep=sdk.audit_project(self.project)
  self.assertFalse(rep['compatible'])
  cats={x['category'] for x in rep['issues']}
  self.assertIn('ozv7-ipc-boundary',cats)
  self.assertIn('ozv7-ram-only-helper',cats)
  self.assertIn('ozv7-lease-tamper',cats)
 def test_v732_audit_blocks_ld_audit_and_frida_and_bad_python_syntax(self):
  (self.project/'bin/main.sh').write_text('#!/bin/bash\nLD_AUDIT=/tmp/hook.so frida-agent\n')
  (self.project/'bin/helper.py').write_text('def broken(\n')
  rep=sdk.audit_project(self.project)
  self.assertFalse(rep['compatible'])
  cats={x['category'] for x in rep['issues']}
  self.assertIn('ozv7-preload-guard',cats)
  self.assertIn('ozv7-maps-guard',cats)
  self.assertIn('python-syntax',cats)
 def test_v732_store_payload_generates_admin_json_and_postgres_sql(self):
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'store-payload',str(self.project),'--download-url','https://usercontent.chgm.in/ozpanel/sdk-1.0.2/addon_9002.sh','--cdn-url','https://cdnv1.cm.io.vn/addon/addon_9002.sh','--author','Chương Minh Studio','--distributor','Ozon Store']),contextlib.redirect_stdout(buf):
   sdk.main()
  out=json.loads(buf.getvalue())
  self.assertEqual(out['redis_cache_key'],'oz:store:v10')
  self.assertEqual(out['admin_payload']['id'],9002)
  self.assertEqual(len(out['catalog_row_10_fields'].split('|')),10)
  self.assertIn('INSERT INTO "addons"',out['postgres_upsert_sql'])
  self.assertIn('ON CONFLICT ("id") DO UPDATE',out['postgres_upsert_sql'])
 def test_v732_telemetry_payload_and_shard_calculation(self):
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'telemetry-payload','--id','9002','--action','install','--addon-version','3.0.0']),contextlib.redirect_stdout(buf):
   sdk.main()
  out=json.loads(buf.getvalue())
  self.assertEqual(out['endpoint'],'POST /api/client/addons/event')
  self.assertTrue(0<=out['shard_index']<=63)
  self.assertEqual(out['payload']['addon_id'],9002)
 def test_v732_sbom_generator(self):
  sbom_file=self.base/'sbom.json'
  self.cli('sbom',self.project,'--out',sbom_file)
  doc=json.loads(sbom_file.read_text())
  self.assertEqual(doc['sbom_schema'],'ozpanel.sdk.sbom/1')
  self.assertEqual(doc['panel_baseline'],'9.1.4')
  self.assertEqual(doc['shield_engine'],'OZV8-Fortress+')
  self.assertTrue(doc['audit']['compatible'])
 def test_v732_new_typed_context_wrappers(self):
  from http.server import BaseHTTPRequestHandler,HTTPServer
  calls=[]
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):
    calls.append(('GET',self.path,None));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
   def do_POST(self):
    length=int(self.headers.get('Content-Length','0'));body=json.loads(self.rfile.read(length)) if length else {}
    calls.append(('POST',self.path,body));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
  server=HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with patch.dict(os.environ,dict(OZ_API_BASE='http://127.0.0.1:'+str(server.server_port),OZ_API_TOKEN='tok-732')):
    ctx=self.context()
    self.assertTrue(ctx.webserver_action('status')['ok'])
    self.assertTrue(ctx.database_action('list')['ok'])
    self.assertTrue(ctx.docker_action('containers')['ok'])
    self.assertTrue(ctx.swap_action('status')['ok'])
    self.assertTrue(ctx.waf_action('threats')['ok'])
    self.assertTrue(ctx.backup_action('list')['ok'])
    self.assertTrue(ctx.ai_action('status')['ok'])
    self.assertTrue(ctx.iam_action('missions','list')['ok'])
   self.assertEqual(calls[0][1],'/api/v1/webserver/status')
   self.assertEqual(calls[1][1],'/api/v1/database/list')
   self.assertEqual(calls[2][1],'/api/v1/docker/containers')
   self.assertEqual(calls[3][1],'/api/v1/swap/status')
   self.assertEqual(calls[4][1],'/api/v1/waf/threats')
   self.assertEqual(calls[5][1],'/api/v1/backup/list')
   self.assertEqual(calls[6][1],'/api/v1/ai/status')
   self.assertEqual(calls[7][1],'/api/v1/missions/list')
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
 def test_v732_context_lease_status_and_client_py_sig_detection(self):
  ndir=self.root/'native';ndir.mkdir(parents=True,exist_ok=True)
  cdir=self.root/'core-api';cdir.mkdir(parents=True,exist_ok=True)
  (cdir/'client.py').write_text('# OZV5-Shield Protected\n# OZV5-SIG:abcdef0123456789\n')
  exp=int(time.time())+800
  (ndir/'runtime.lease').write_bytes((b'X'*32)+struct.pack('>Q',exp)+(b'Y'*32))
  ctx=self.context()
  ls=ctx.lease_status()
  self.assertTrue(ls['sealed'])
  st=sdk.inspect_shield_status(self.root)
  self.assertTrue(st['client_py_ozv5_signed'])
  self.assertTrue(st['lease']['sealed'])
 def test_v732_bash_lease_status_and_wrappers_syntax(self):
  r=subprocess.run(['bash','-n',str(HERE/'lib/ozaddon.sh')],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,r.stderr)
 def test_v732_doctor_includes_ozonfs_and_api_operations(self):
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'doctor']),contextlib.redirect_stdout(buf):sdk.main()
  doc=json.loads(buf.getvalue())
  self.assertEqual(doc['version'],'5.0.0')
  self.assertEqual(doc['panel_compatibility'],'9.1.4')
  self.assertEqual(doc['ozonfs_version'],'9.1.4')
  self.assertEqual(doc['shield_engine'],'OZV8-Fortress+')
  self.assertGreaterEqual(doc['api_resources'],112)
  self.assertGreaterEqual(doc['api_operations'],745)

 def test_v860_panel_baseline_and_932_operations_catalog(self):
  self.assertEqual(sdk.VERSION,'5.0.0')
  self.assertEqual(sdk.PANEL,'9.1.4')
  self.assertEqual(sdk.OZONFS_VERSION,'9.1.4')
  self.assertEqual(sdk.API_V860_CATALOG['version'],'9.1.4')
  self.assertEqual(sdk.API_V914_CATALOG['total_resources'],125)
  self.assertEqual(sdk.API_V914_CATALOG['total_operations'],932)
  self.assertIn('chatops',sdk.API_V860_CATALOG['resources']['ai'])
  self.assertIn('sso_generate',sdk.API_V860_CATALOG['resources']['ai'])
  self.assertIn('delete_records',sdk.API_V860_CATALOG['resources']['cloudflare'])
  self.assertIn('report_3d',sdk.API_V860_CATALOG['resources']['analytics'])
 def test_v860_chatops_cloudflare_dns_only_vs_full_domain_delete(self):
  r=sdk.simulate_chatops_command('em ơi xóa bản ghi tên miền tester.chgm.in trên cloudflare giúp anh')
  self.assertTrue(r['handled'])
  self.assertEqual(r['intent'],'CLOUDFLARE_DNS_ONLY_DELETE')
  self.assertEqual(r['domain'],'tester.chgm.in')
  self.assertTrue(r['preserves_local_vhost'])
 def test_v860_chatops_uninstall_3step_confirmation_protocol(self):
  r0=sdk.simulate_chatops_command('gỡ cài đặt panel')
  self.assertEqual(r0['intent'],'UNINSTALL_MULTI_STEP_GUARD')
  self.assertEqual(r0['confirmation_step'],0)
  self.assertEqual(r0['required_steps'],3)
  r1=sdk.simulate_chatops_command('xác nhận gỡ bước 1')
  self.assertEqual(r1['confirmation_step'],1)
  r2=sdk.simulate_chatops_command('xác nhận gỡ bước 2 hoàn tất')
  self.assertEqual(r2['confirmation_step'],2)
 def test_v860_chatops_directory_file_backup_and_cron_routing(self):
  d1=sdk.simulate_chatops_command('tạo thêm thư mục uploads, cache trong tester.chgm.in')
  self.assertEqual(d1['intent'],'CREATE_DIRECTORY')
  self.assertTrue(d1['preserves_index'])
  d2=sdk.simulate_chatops_command('xóa tất cả tệp trong thư mục uploads của tester.chgm.in')
  self.assertEqual(d2['intent'],'EMPTY_DIRECTORY_FILES')
  d3=sdk.simulate_chatops_command('backup website tester.chgm.in')
  self.assertEqual(d3['intent'],'OZONBACKUP_ENTERPRISE')
  d4=sdk.simulate_chatops_command('đặt lệnh cron 3 ngày 1 lần truy cập vào link https://tester.chgm.in/cron.php')
  self.assertEqual(d4['intent'],'NATURAL_CRONJOB')
  d5=sdk.simulate_chatops_command('chạy hàm 1 mục 9')
  self.assertEqual(d5['intent'],'DIRECT_FUNCTION_SUBOPTION')
  self.assertEqual(d5['function_ids'],[1])
  self.assertEqual(d5['sub_option'],'9')
 def test_v860_chatops_sso_and_3d_analytics_routing(self):
  s1=sdk.simulate_chatops_command('tạo link sso dẫn đến database vuive')
  self.assertEqual(s1['intent'],'ONE_CLICK_SSO_LINK')
  self.assertEqual(s1['sso_target'],'database')
  s2=sdk.simulate_chatops_command('xuất báo cáo thống kê truy cập 3d cho tester.chgm.in')
  self.assertEqual(s2['intent'],'TRAFFIC_ANALYTICS_3D')
 def test_v860_ai_watchdog_status_cursors_and_deduplication(self):
  st_dir=self.root/'ai_assistant'/'state';st_dir.mkdir(parents=True,exist_ok=True)
  (st_dir/'log_cursors.json').write_text('{"/var/log/nginx/error.log":{"inode":123,"offset":4560}}')
  (st_dir/'reported_signatures.json').write_text('{"SECURITY_IP_BAN_HEAL:1.2.3.4":1794730000}')
  st=sdk.inspect_ai_watchdog_status(self.root)
  self.assertEqual(st['panel_version'],'9.1.4')
  self.assertTrue(st['incremental_log_cursor_enabled'])
  self.assertTrue(st['htaccess_ols_surgery_enabled'])
  self.assertEqual(st['active_suppressed_signatures'],1)
 def test_v860_cli_chatops_simulate_and_ai_watchdog_status(self):
  import io,contextlib
  from unittest.mock import patch
  buf=io.StringIO()
  with patch.object(sys,'argv',['ozsdk.py','--root',str(self.root),'chatops-simulate','backup toàn bộ hệ thống']),contextlib.redirect_stdout(buf):
   sdk.main()
  out=json.loads(buf.getvalue())
  self.assertEqual(out['intent'],'OZONBACKUP_ENTERPRISE')
 def test_v860_context_sso_and_chatops_and_cloudflare_and_3d_wrappers(self):
  from http.server import BaseHTTPRequestHandler,HTTPServer
  from unittest.mock import patch
  calls=[]
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_POST(self):
    length=int(self.headers.get('Content-Length','0'));body=json.loads(self.rfile.read(length)) if length else {}
    calls.append(('POST',self.path,body));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
  server=HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with patch.dict(os.environ,dict(OZ_API_BASE='http://127.0.0.1:'+str(server.server_port),OZ_API_TOKEN='tok-860')):
    ctx=self.context()
    self.assertTrue(ctx.chatops_command('backup toàn bộ')['ok'])
    self.assertTrue(ctx.sso_link('database','vuive','vuive_usr')['ok'])
    self.assertTrue(ctx.cloudflare_delete_records('tester.chgm.in','A')['ok'])
    self.assertTrue(ctx.analytics_3d_report('tester.chgm.in')['ok'])
   self.assertEqual(calls[0][1],'/api/v1/ai/chatops')
   self.assertEqual(calls[1][1],'/api/v1/ai/sso_generate')
   self.assertEqual(calls[2][1],'/api/v1/cloudflare/delete_records')
   self.assertEqual(calls[3][1],'/api/v1/analytics/report_3d')
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
 def test_v860_context_ai_watchdog_status_helper(self):
  st_dir=self.root/'ai_assistant'/'state';st_dir.mkdir(parents=True,exist_ok=True)
  (st_dir/'log_cursors.json').write_text('{"/usr/local/lsws/logs/error.log":{"inode":99,"offset":1024}}')
  ctx=self.context()
  ws=ctx.ai_watchdog_status()
  self.assertEqual(ws['panel_version'],'9.1.4')
  self.assertIn('/usr/local/lsws/logs/error.log',ws['incremental_cursors'])
 def test_v860_bash_v860_helpers_syntax(self):
  r=subprocess.run(['bash','-n',str(HERE/'lib/ozaddon.sh')],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,r.stderr)
  sh_body=(HERE/'lib/ozaddon.sh').read_text()
  self.assertIn('oz_chatops()',sh_body)
  self.assertIn('oz_sso_link()',sh_body)
  self.assertIn('oz_ai_watchdog_status()',sh_body)

 def test_v914_lease_little_endian_and_6h_policy(self):
  ndir=self.root/'native';ndir.mkdir(parents=True,exist_ok=True)
  now=int(time.time());exp=now+21600
  (ndir/'runtime.lease').write_bytes((b'L'*32)+struct.pack('<Q',exp)+(b'E'*32))
  st=sdk.inspect_lease_status(self.root,now=now)
  self.assertTrue(st['sealed'])
  self.assertEqual(st['expires_at'],exp)
  self.assertEqual(st['ttl_remaining'],21600)
  self.assertEqual(st['lease_ttl_policy_seconds'],21600)
  self.assertEqual(st['protocol'],'ozv8-fortress/1')
  ctx_st=self.context().lease_status(now=now)
  self.assertTrue(ctx_st['sealed'])
  self.assertEqual(ctx_st['expires_at'],exp)
 def test_v914_cli_ergonomic_flags_keygen_init_pack_verify_trust(self):
  p_dir=self.base/'ergo-proj';k_dir=self.base/'ergo-keys';out_pkg=self.base/'ergo.ozaddon'
  self.cli('init',p_dir,'--id','9015','--publisher','ergo-pub','--name','Ergo Addon','--category','automation')
  m=json.loads((p_dir/'manifest.json').read_text());self.assertEqual(m['category'],'automation')
  self.cli('keygen','--out',k_dir)
  self.assertTrue((k_dir/'publisher-private.pem').is_file());self.assertTrue((k_dir/'publisher-public.pem').is_file())
  self.cli('pack',p_dir,'--out',out_pkg,'--sign-key',k_dir/'publisher-private.pem')
  self.cli('verify',out_pkg,'--pub-key',k_dir/'publisher-public.pem')
  self.cli('trust','--publisher','ergo-pub','--pub-key',k_dir/'publisher-public.pem','--confirm')
  self.cli('verify',out_pkg)
 def test_v914_audit_blocks_bg_lease_refresh_and_allows_clean_example(self):
  self.assertTrue(sdk.audit_project(HERE/'examples/native')['compatible'])
  (self.project/'bin/main.sh').write_text('#!/bin/bash\n/usr/bin/oz --ozv7-bg-lease-refresh\n')
  rep=sdk.audit_project(self.project)
  self.assertFalse(rep['compatible'])
  self.assertIn('ozv7-ipc-boundary',{x['category'] for x in rep['issues']})
 def test_v914_api_catalog_and_helpers_get_routing(self):
  from http.server import BaseHTTPRequestHandler,HTTPServer
  calls=[]
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):
    calls.append(('GET',self.path,None));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
   def do_POST(self):
    length=int(self.headers.get('Content-Length','0'));body=json.loads(self.rfile.read(length)) if length else {}
    calls.append(('POST',self.path,body));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"ok":true}')
  server=HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with patch.dict(os.environ,dict(OZ_API_BASE='http://127.0.0.1:'+str(server.server_port),OZ_API_TOKEN='tok-914')):
    ctx=self.context()
    self.assertTrue(ctx.api_call('ai','shift_report')['ok'])
    self.assertTrue(ctx.api_call('panel','groups')['ok'])
    self.assertTrue(ctx.ai_cache_stats()['ok'])
    self.assertTrue(ctx.ai_config_inspect('/etc/nginx/nginx.conf')['ok'])
    self.assertTrue(ctx.app_pulse()['ok'])
    self.assertTrue(ctx.webhooks_action('list')['ok'])
    self.assertTrue(ctx.db_tables_list('app_db','mysql')['ok'])
   self.assertEqual([c[0] for c in calls],['GET']*7)
   self.assertEqual(calls[0][1],'/api/v1/ai/shift_report')
   self.assertEqual(calls[1][1],'/api/v1/panel/groups')
   self.assertEqual(calls[2][1],'/api/v1/ai/cache_stats')
   self.assertIn('/api/v1/ai/config_inspect?path=',calls[3][1])
   self.assertEqual(calls[4][1],'/api/v1/app/pulse')
   self.assertEqual(calls[5][1],'/api/v1/webhooks/list')
   self.assertIn('/api/v1/database/tables_list?name=app_db',calls[6][1])
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
 def test_v914_bash_extended_helpers_and_health_json(self):
  sh_body=(HERE/'lib/ozaddon.sh').read_text()
  for fn in ('oz_health_json()','oz_ai_cache_stats()','oz_config_inspect()','oz_app_pulse()','oz_webhooks()','oz_db_tables()'):
   self.assertIn(fn,sh_body)
  hj=self.context().health_json()
  self.assertEqual(hj['version'],'9.1.4')
  self.assertEqual(hj['shield_engine'],'OZV8-Fortress+')

if __name__=='__main__':unittest.main()

