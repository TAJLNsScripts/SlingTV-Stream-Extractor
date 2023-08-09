import base64
import requests
import json
import jwt
import os
import m3u8
import signal
import sys
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
from pywidevine.license_protocol_pb2 import SignedMessage

#Config
WVD_PATH = './WVD.wvd'

def ascii_clear():
    os.system('cls||clear')
    print("""
                                                       ::      .YY7^                                
                                      :^:.      ~:     :5Y7.    :PPPJ:                              
                                    !5PPP5J.    !PJ:    !PP5:    ?PPP5.                             
                         .......   ^PPPPPPG?    .PG?    :PPP?    !PPPP~                             
                         ?JJJJJ7   .?PPPPP5^    !P5^    !PPP^    ?PPP5:                             
                         ?JJJJY7     :~!!^     .!~.    :55J:    :PPPY^                              
                         ?JJJJY7                       ^^.     :Y5J~                                
                         ?JJJJY7                               .:                                   
    .^~!777777!~^:.      ?JJJJY7    ~?????7    ^?????7. .^!77??7!~^.            :^!77??77~^. ^!!!!!~
  ^7JYYYYYYYYYYYYJJ7^    ?JJJJY7    7YJJJY?    ~YJJJYJ~7JYYYYYJJYYYJ!.       .~?JYYYJYYYYYJJ~7YYYYYY
 !YYJJJJ??777?JJYYYJ^    ?JJJJY7    7YJJJJ?    ~YJJJJJJYYJ???JJYJJJJYJ:     ^?YJJJJYJJ???JJYYJJJJJJJ
^YJJJJJ^      .:^7?:     ?JJJJY7    7YJJJJ?    ~YJJJJJJ7^.   .:7JJJJJY?    ^JJJJJJJ!:.   .:7JJJJJJJJ
:JJJJJJ?!^^:..           ?JJJJY7    7YJJJJ?    ~YJJJJJ!         7JJJJJJ.  .JJJJJJ?.         ~JJJJJJJ
 ^JYYJJJYYJJJJ?7!^:      ?JJJJY7    7YJJJJ?    ~YJJJJJ.         ~YJJJJJ.  ~YJJJJY^           7JJJJJJ
  .^7?JJJYYYYYJJYYJ?^    ?JJJJY7    7YJJJJ?    ~YJJJJJ.         !YJJJJJ.  ~YJJJJY^           7YJJJJJ
      .:^^~!7?JJJJJJY~   ?JJJJY7    7YJJJJ?    ~YJJJJJ.         !YJJJJJ.  ^YJJJJJ7          :JJJJJJJ
  ^^.         .!JJJJJ?   ?JJJJY7    7YJJJJ?    ~YJJJJJ.         !YJJJJJ.   7YJJJJJ?^.     .~JJJJJJJJ
.7YJJ7!~^:::::~?JJJJY!   ?JJJJY7    7YJJJJ?    ~YJJJJJ.         !YJJJJJ.   .7YJJJJJYJ?777?JYJJJJJJJJ
7JYYYYYYYJJJJJYJJJYJ!    ?JJJJY7    7YJJJJ?    ~YJJJJJ.         !YJJJJJ.     ~?YYJJJJJJYYYYY??JJJJJJ
 .^!?JJJJYYYYJJJ?7~.     ?JJJJJ7    !JJJJJ?    ~JJJJJJ.         ~JJJJJ?.      .^7?JJJYYJJJ7^ 7YJJJJJ
     ..::^^^^::.         .......    .......     ......           ......           .:^^^::.  .JJJJJJ?
                                                                             :7~:         .~JJJJJJJ:
                                                                            ~JYYJ?7!!~~!!7JYJJJJY?: 
                                                                           .!?JJJYYYYYYYYYJJJJJ7^   
                                                                              :~!7?JJJJJJJ?7!^.                                              
                                      Stream Extractor                                     
                                         TAJLN 2023       
                                         
""")

def signal_handler(sig, frame):
    print('\nBye :)')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def do_cdm(pssh, token):
    channel_id = jwt.decode(token, options={"verify_signature": False})['channel_guid']

    pssh = PSSH(pssh)

    device = Device.load(WVD_PATH)

    cdm = Cdm.from_device(device)

    session_id = cdm.open()

    challenge = cdm.get_license_challenge(session_id, pssh)

    c_array = []

    for c in challenge:
        c_array.append(c)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Env': 'production',
        'Channel-Id': channel_id,
        'Content-Type': 'application/json',
    }

    data = {
      "message": c_array
    }

    data = json.dumps(data)

    licence = requests.post("https://p-drmwv.movetv.com/widevine/proxy", headers=headers, data=data)
    licence.raise_for_status()

    cdm.parse_license(session_id, licence.content)

    for key in cdm.get_keys(session_id):
        if key.type != 'SIGNING':
            print(f"\nDRM key: {key.kid.hex}:{key.key.hex()}")

    cdm.close(session_id)

def process_channel(channel, token):

    subscriber_id = jwt.decode(token, options={"verify_signature": False})['prof']

    headers = {
        'authorization': 'Bearer ' + token,
    }

    json_data = {
        'os_version': '10',
        'device_name': 'browser',
        'os_name': 'Windows',
        'brand': 'sling',
        'subscriber_id': subscriber_id,
        'qvt': 'https://cbd46b77.cdn.cms.movetv.com/playermetadata/sling/v1/api/channels/' + channel + '/current/schedule.qvt',
        'drm': 'widevine',
        'account_status': 'active',
        'advertiser_id': None,
        'support_mode': 'false',
        'ssai_vod': 'true',
        'ssai_dvr': 'true',
    }

    response = json.loads(requests.post('https://p-streamauth.movetv.com/stream/auth', headers=headers, json=json_data).content)
    
    temp_token = response['jwt']
    m3u8_url = response['m3u8_url']
    ssai_manifest = response['ssai_manifest'].split('?')[0]
    
    m3u8_obj = m3u8.load(m3u8_url)
    for key in m3u8_obj.session_keys:
        pssh = key.uri.split(',')[-1]
    
    print('\nm3u8 URL: ' + ssai_manifest)
    do_cdm(pssh, temp_token)
 
def get_channels(token):
    headers = {
        'authorization': 'Bearer ' + token,
        'client-config': 'rn-client-config',
        'client-version': '4.32.20',
        'content-type': 'application/json; charset=UTF-8',
        'device-model': 'Chrome',
        'dma': '501',
        'features': 'use_ui_4=true,inplace_reno_invalidation=true,gzip_response=true,enable_extended_expiry=true,enable_home_channels=true,enable_iap=true,enable_trash_franchise_iview=false,browse-by-service-ribbon=true,subpack-hub-view=true,entitled_streaming_hub=false,add-premium-channels=false,enable_home_sports_scores=false,enable-basepack-ribbon=true',
        'page_size': 'large',
        'player-version': '7.6.2',
        'response-config': 'ar_browser_1_1',
        'sling-interaction-id': '596bd797-90f1-440f-bc02-e6f588dae8f6',
        'timezone': 'America/Los_Angeles',
    }

    response = json.loads(requests.get('https://p-cmwnext.movetv.com/pres/grid_guide_a_z', headers=headers).content)
    
    special_ribbons = response['special_ribbons']
    
    tiles = special_ribbons[0]['tiles']
    
    channels = []
    
    for t in tiles:
        r = {}
        r['title'] = t['title']
        r['code'] = t['href'].split('/')[-1]
        channels.append(r)
        
    return channels

def extract_token():
    f = open("user.txt", "r") 
    
    user = json.loads(json.loads(f.read())['user'])
    
    return user['userData']['jwt']
    
ascii_clear()

try:    
    token = extract_token()
except:
    print('Failed getting token')
    print('Did you copy "persist:root" local variable from browser to user.txt?')
    quit()

input('Press enter to fetch channel list')

ascii_clear()

channels = get_channels(token)
i = 1
for c in channels:
    print(str(i) + '. ' + c['title'])
    i+=1
 
choice = int(input('\nChoose channel: ')) - 1

ascii_clear()
print(channels[choice]['title'])
process_channel(channels[choice]['code'], token)