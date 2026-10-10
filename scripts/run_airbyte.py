"""Trigger both existing Airbyte connections and wait for completion; exit non-zero on failure."""
import os, sys, time
import requests
from dotenv import load_dotenv
load_dotenv()
TERMINAL_SUCCESS={'succeeded','success','completed'}
TERMINAL_FAIL={'failed','cancelled','canceled','incomplete','error'}

def required(key):
    val=os.environ.get(key,'').strip()
    if not val or val=='REPLACE_ME': raise RuntimeError(f'Missing {key}')
    return val

def response_json(r):
    r.raise_for_status(); return r.json()

def token(session, base):
    client_id=required('AIRBYTE_CLIENT_ID'); secret=required('AIRBYTE_CLIENT_SECRET')
    # Airbyte public API credentials (from abctl local credentials)
    url=base.rsplit('/api/public/v1',1)[0]+'/api/public/v1/applications/token' if '/api/public/v1' in base else base+'/applications/token'
    obj=response_json(session.post(url,json={'client_id':client_id,'client_secret':secret},timeout=30))
    return obj['access_token']

def get_status(payload):
    job=payload.get('job',payload)
    return str(job.get('status','')).lower()

def sync(session,base,connection_id,label):
    job=response_json(session.post(base+'/jobs',json={'connectionId':connection_id,'jobType':'sync'},timeout=30))
    job_id=job.get('jobId',job.get('id'))
    if not job_id: raise RuntimeError(f'No job ID returned for {label}: {job}')
    print(f'{label}: started job {job_id}',flush=True)
    deadline=time.monotonic()+50*60
    while time.monotonic()<deadline:
        data=response_json(session.get(base+f'/jobs/{job_id}',timeout=30))
        state=get_status(data)
        print(f'{label} job {job_id}: {state}',flush=True)
        if state in TERMINAL_SUCCESS: return
        if state in TERMINAL_FAIL: raise RuntimeError(f'{label} failed: {data}')
        time.sleep(20)
    raise TimeoutError(f'{label}: job {job_id} timed out')

if __name__=='__main__':
    base=required('AIRBYTE_API_URL').rstrip('/')
    s=requests.Session()
    # Request a short-lived token for current API and authenticate both syncs.
    s.headers['Authorization']='Bearer '+token(s,base)
    s.headers['Content-Type']='application/json'
    sync(s,base,required('AIRBYTE_TRADES_CONNECTION_ID'),'Google Sheets trade log')
    sync(s,base,required('AIRBYTE_FX_CONNECTION_ID'),'USD/NGN exchange rate')
