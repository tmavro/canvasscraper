import requests
import re
import platform
import subprocess
from bs4 import BeautifulSoup
from shutil import which

# Oppgi session cookie, "kms_ctamuls":
cookie = 'deim3choothoh2ooRo5ohjie8e'
# Oppgi URL til emnets ID
galleryID = '12345'

#Setter opp for innlogging
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}) #Ingen blokkering, men kanskje en ekstra sikkerhet?
cookiejar = requests.cookies.RequestsCookieJar()
cookiejar.set('kms_ctamuls', cookie)
session.cookies = cookiejar

#Henter fra galleri
retrieved = session.get('https://354-1.kaltura.nordu.net/channel/' + galleryID)
parsed = BeautifulSoup(retrieved.text, 'html.parser')

#Sjekker at vi får tilgang, eller avbryter
access = parsed.find('div', { 'id': 'content' })
if access.text.strip() == "Access Denied":
    print("Noe gikk galt ved innlogging! Problem med kjekset?",
    "\nTo server:", retrieved.request.headers)
    exit()

#Henter informasjon om samtlige forelesninger
names = [ name.text for name in parsed.find_all('p', {'class': 'thumb_name_content'}) ] #Forelesningers titler
urls = [ url.get('href') for url in parsed.find_all('a', { 'class': 'item_link'}) ] #Forelesningers url-er
urls = list(dict.fromkeys(urls)) #Fjerner duplikat fra listen
urls = [ re.findall('0_[\d\w]+', id)[0] for id in urls ] #Skiller ut url-enes id-er
m3u8 = [ 'https://dchsou11xk84p.cloudfront.net/p/354/playManifest/entryId/'
            + url + '/format/applehttp/a.m3u8' for url in urls] #Ressurslokasjoner
#Utsktrift av videoer (forhåpentligvis)
if not names or not m3u8:
    print('Noe gikk galt! Ingen videoer funnet. Feil URL til galleri?')
    exit()
else:
    print('Funnet videoer!')
    for i in range(len(names)):
        print('[' + str(i) + ']: ' + names[i] + '\n' + m3u8[i] + '\n')

if platform.system() == 'Linux' and which('youtube-dl') != None:
    spm = input('Vil du begynne nedlasting av hele listen, eller kun en video? y/[0 - ' + str(len(m3u8)-1) + ']/N \n')
    if spm == 'y' or spm == 'Y':
        for i in range(len(m3u8)):
            subprocess.run(["youtube-dl", m3u8[i], "-o", names[i] + ".mp4"])
    elif spm.isdigit() and int(spm) < len(m3u8)-1 and int(spm) > -1:
        subprocess.run(["youtube-dl", m3u8[int(spm)], "-o", names[int(spm)] + '.mp4'])
        print('Lastet ned som ' + names[int(spm)] + '.mp4')
    else:
        print('Avslutter programmet')
        exit()
