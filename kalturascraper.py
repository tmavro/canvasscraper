from argparse import ArgumentParser
import re
import requests
from bs4 import BeautifulSoup
from shutil import which
import subprocess
import os.path

class Galleri:
    def __init__(self, gallery, directory):
        self.gal = gallery
        self.dir = directory
        if self.dir[-1] != '/':
            self.dir += '/'
        self.names = []
        self.urls = []
        self.tomt = True #Sjekk for om det er noe i galleriet

    def nyttNavn(self, n):
        self.names.append(n)

    def nyUrl(self, u):
        self.urls.append(u)
        self.tomt = False #Ny url betyr at vi har funnet noe

#Laster ned dersom fil ikke allerede eksisterer
def ytdl(url, dir, name):
    PATH = dir + name + ".mp4"
    if not os.path.isfile(PATH):
        print("Laster ned: " + PATH)
        subprocess.run(["youtube-dl", "-q", url, "-o", PATH])
    else:
         print("Eksisterer allerede: " + PATH)

#Sjekker at argumentene ikke ender med tårer
def checkArguments(args):
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

    if len(args.gallery) < len(args.directory):
        print('Det kan ikke være flere mapper enn galleri.')
        exit()

def main():

    #Arguments
    parser = ArgumentParser()
    parser.add_argument('-c', '--cookie', required='true', help='set cookie value')
    parser.add_argument('-g', '--gallery', required='true', action='append', help='set gallery or galleries to scrape')
    parser.add_argument('-d', '--directory', required='true', action='append', help='set directory or directories to store files')
    parser.add_argument('-f', '--force', action='store_true', help='automatically start any available downloads')
    args = parser.parse_args()

    checkArguments(args)

    #Oppretter galleriobjekter med galleri-ID og mapper
    gallerier = []
    for i, gal in enumerate(args.gallery):
        if len(args.directory) > 1:
            gallerier.append(Galleri(gal, args.directory[i]))
        else:
            gallerier.append(Galleri(gal, args.directory[0]))

    #Setter opp for innlogging
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'}) #Ingen blokkering, men kanskje en ekstra sikkerhet?
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
        retrieved = session.get('https://354-1.kaltura.nordu.net/channel/' + galleri.gal + '//sort/recent/pageSize/1000')
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

        if galleri.tomt:
            print('Ingen videoer funnet i galleri ' + galleri.gal)
        else:
            print('Videoer funnet i galleri ' + galleri.gal)

    #Sjekker om vi fant noen urler til videoer
    if all(galleri.tomt for galleri in gallerier):
        print("Ingen videoer funnet med gitt input. Avslutter.")
        exit()

    #Nedlasting
    if which('youtube-dl') != None:
        if args.force:
            for galleri in gallerier:
                for i in range(len(galleri.urls)):
                    ytdl(galleri.urls[i], galleri.dir, galleri.names[i])
        else:
            spm = input('\nVil du laste ned alle videoer? y/N \n')
            if spm == 'y' or spm == 'Y':
                for galleri in gallerier:
                    for i in range(len(galleri.urls)):
                        ytdl(galleri.urls[i], galleri.dir, galleri.names[i])
            #Eller vis objektene en etter en først
            else:
                for galleri in gallerier:
                    spm = ''
                    while (not spm.isdigit()):
                        if which('youtube-dl') != None:
                            for i, gal in enumerate(args.gallery):
                                print('[' + str(i) + ']: ' + galleri.names[i] + '\n' + galleri.urls[i] + '\n')
                            spm = input('Vil du laste ned hele galleri ' + galleri.gal + ', eller en bestemt video? y/[0 - ' + str(len(galleri.urls)-1) + ']/N \n')
                            if spm == 'y' or spm == 'Y': #youtube-dl skriver ikke over filer den allerede har lastet ned
                                for i in range(len(galleri.names)):
                                    ytdl(galleri.urls[i], galleri.dir, galleri.names[i])
                                break
                            elif spm.isdigit() and int(spm) < len(m3u8)-1 and int(spm) > -1:
                                ytdl(galleri.urls[i], galleri.dir, galleri.names[i])
                                print('Lastet ned til ' + galleri.dir + galleri.names[int(spm)] + '.mp4' + '\n')
                                for i in galleri.names:
                                    print('[' + str(i) + ']: ' + galleri.names[i] + '\n' + galleri.urls[i] + '\n')
                                spm = ''
                            else:
                                break

if __name__ == '__main__':
    main()
