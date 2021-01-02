from argparse import ArgumentParser
import re
import requests
from bs4 import BeautifulSoup
import platform
from shutil import which
import subprocess

class galleri:
    def __init__(self, gallery, directory):
        self.gal = gallery
        self.dir = directory
        if self.dir[-1] != '/':
            self.dir += '/'
        self.names = []
        self.urls = []

    def nyttNavn(self, n):
        self.names.append(n)

    def nyUrl(self, u):
        self.urls.append(u)

#Arguments
parser = ArgumentParser()
parser.add_argument('-c', '--cookie', required='true', help='set cookie value')
parser.add_argument('-g', '--gallery', required='true', action='append', help='set gallery or galleries to scrape')
parser.add_argument('-d', '--directory', required='true', action='append', help='set directory or directories to store files')
args = parser.parse_args()

#Sjekker at argumentene ikke ender med tårer
if not re.match(r'^[a-z\d]{26}$', str(args.cookie)):
    print('Kakestrengen matcher ikke programmets kriterier (Kombinasjon av små bokstaver og tall, 26 tegn totalt)')
    exit()

for dir in args.directory:
    if not re.match(r'^(\\?/?[A-Za-z0-9. \"]+\\?/?)+$', str(dir)):
        print(dir + ' Mappestrukturen matcher ikke programmets kriterier.')
        exit()

for gal in args.gallery:
    if not re.match(r'^[0-9]+$', str(gal)):
        print(gal + ' Galleriers ID skal kun inneholde tall.')
        exit()

if len(args.gallery) != len(args.directory):
    print('Det må være like mange galleri og mapper.')
    exit()

#Oppretter galleriobjekter med galleri-ID og mapper
gallerier = []
for idx, gal in enumerate(args.gallery):
    gallerier.append(galleri(gal, args.directory[idx]))

#Setter opp for innlogging
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}) #Ingen blokkering, men kanskje en ekstra sikkerhet?
cookiejar = requests.cookies.RequestsCookieJar()
cookiejar.set('kms_ctamuls', args.cookie)
session.cookies = cookiejar

#Sjekker at vi får tilgang, eller avbryter
retrieved = session.get('https://354-1.kaltura.nordu.net/channel/' + args.gallery[0])
parsed = BeautifulSoup(retrieved.text, 'html.parser')
if parsed.find('div', { 'id': 'content' }).text.strip() == "Access Denied":
    print("Noe gikk galt ved innlogging! Problem med kjekset eller galleriet?",
    "\nSendt til server:", retrieved.request.headers)
    exit()

#Henter informasjon om samtlige forelesninger
for galleri in gallerier:
    retrieved = session.get('https://354-1.kaltura.nordu.net/channel/' + galleri.gal)
    parsed = BeautifulSoup(retrieved.text, 'html.parser')
    if parsed.find('div', { 'id': 'content' }).text.strip() == "Access Denied":
        print("Noe gikk galt med galleri" + galleri.gal + "! Ingen adgang!")
        continue
    names = [ name.get('title', 'Ingen tittel funnet') for name in parsed.find_all('div', { 'class': 'photo-group thumb_wrapper' }) ]
    for name in names:
        galleri.nyttNavn(name)
    urls = [ url.get('href') for url in parsed.find_all('a', { 'class': 'item_link'}) ] #Forelesningers url-er
    urls = list(dict.fromkeys(urls)) #Fjerner duplikat fra listen
    urls = [ re.findall('0_[\d\w]+', id)[0] for id in urls ] #Skiller ut url-enes id-er
    m3u8 = [ 'https://dchsou11xk84p.cloudfront.net/p/354/playManifest/entryId/' + url + '/format/applehttp/a.m3u8' for url in urls] #Ressurslokasjoner
    for url in m3u8:
        galleri.nyUrl(url)

    if not names or not m3u8:
        print('Noe gikk galt! Ingen videoer funnet. Feil URL til galleri?')
        for i, data in galleri.names:
            print('[' + str(i) + ']: ' + galleri[i].names + '\n' + galleri[i].urls + '\n')


#Nedlasting
if (platform.system() == 'Linux' or platform.system() == 'Darwin') and which('youtube-dl') != None:
    spm = input('Vil du laste ned alle videoer? y/N \n')
    if spm == 'y' or spm == 'Y':
        for galleri in gallerier:
            for i in range(len(galleri.urls)):
                subprocess.run(["youtube-dl", galleri.urls[i], "-o", galleri.dir + galleri.names[i] + ".mp4"])
    else: #Vis objektene en etter en først
        for galleri in gallerier:
            for i, data in enumerate(galleri.names):
                print('[' + str(i) + ']: ' + galleri.names[i] + '\n' + galleri.urls[i] + '\n')
            spm = ''
            while (not spm.isdigit()):
                if (platform.system() == 'Linux' or platform.system() == 'Darwin') and which('youtube-dl') != None:
                    spm = input('Vil du laste ned hele listen, eller en bestemt video? y/[0 - ' + str(len(m3u8)-1) + ']/N \n')
                    if spm == 'y' or spm == 'Y': #youtube-dl skriver ikke over filer den allerede har lastet ned
                        for i in range(len(galleri.names)):
                            subprocess.run(["youtube-dl", galleri.urls[i], "-o", galleri.dir + galleri.names[i] + ".mp4"])
                        continue
                    elif spm.isdigit() and int(spm) < len(m3u8)-1 and int(spm) > -1:
                        subprocess.run(["youtube-dl", galleri.urls[i], "-o", galleri.dir + galleri.names[i] + ".mp4"])
                        print('Lastet ned til ' + galleri.dir + galleri.names[int(spm)] + '.mp4' + '\n')
                        for i in range(len(names)):
                            print('[' + str(i) + ']: ' + names[i] + '\n' + m3u8[i] + '\n')
                        spm = ''
                    else:
                        break
