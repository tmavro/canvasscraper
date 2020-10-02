from argparse import ArgumentParser
import re
import requests
from bs4 import BeautifulSoup
import platform
from shutil import which
import subprocess

# Oppgi session cookie, "kms_ctamuls":
cookie = 'caxaPh5ziet2ahYoolaeJ9oZee'
# Oppgi URL til emnets ID
galleryID = '12345'
# Oppgi hvor du vil lagre filene. Havner i samme mappe som scriptet hvis tomt, eller argument ikke gis.
dir = ''

#Arguments (krangler)
argpars = ArgumentParser()
argpars.add_argument('-c', '--cookie', help='set cookie value')
argpars.add_argument('-d', '--dir', help='choose dir to store files')
argpars.add_argument('-g', '--gallery', help='choose gallery to scrape')
args = argpars.parse_args()

#Sjekker at kranglingen ikke ender med tårer
if args.dir != None:
    if re.match(r'^(\\?/?[A-Za-z0-9. \"]+\\?/?)+$', str(args.dir)):
        dir = args.dir
        if dir[-1] != '/':
            dir += '/'
    else:
        print('Mappestrukturen matcher ikke programmets kriterier.')
        exit()
if args.cookie != None:
    if re.match(r'^[a-z\d]{26}$', str(args.cookie)):
        cookie = args.cookie
    else:
        print('Kakestrengen matcher ikke programmets kriterier (Kombinasjon av små bokstaver og tall, 26 tegn totalt)')
        exit()
if args.gallery != None:
    if re.match(r'^[0-9]+$', str(args.gallery)):
        galleryID = args.gallery
    else:
        print('Galleriets ID skal kun inneholde tall.')
        exit()

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

#Nedlasting
spm = ''
while (not spm.isdigit()):
    if (platform.system() == 'Linux' or platform.system() == 'Darwin') and which('youtube-dl') != None:
        spm = input('Vil du laste ned hele listen, eller en bestemt video? y/[0 - ' + str(len(m3u8)-1) + ']/N \n')
        if spm == 'y' or spm == 'Y': #youtube-dl skriver ikke over filer den allerede har lastet ned
            for i in range(len(m3u8)):
                subprocess.run(["youtube-dl", m3u8[i], "-o", dir + names[i] + ".mp4"])
            exit()
        elif spm.isdigit() and int(spm) < len(m3u8)-1 and int(spm) > -1:
            subprocess.run(["youtube-dl", m3u8[int(spm)], "-o", dir + names[int(spm)] + '.mp4'])
            print('Lastet ned til ' + dir + names[int(spm)] + '.mp4' + '\n')
            for i in range(len(names)):
                print('[' + str(i) + ']: ' + names[i] + '\n' + m3u8[i] + '\n')
            spm = ''
        else:
            exit()
