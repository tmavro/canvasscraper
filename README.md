# kalturascraper.py

*Få enkel adgang til dine emners videofiler i canvas*

**kalturascraper.py** genererer en liste med URL-er til alle videoer i et valgt emne. Disse URL-ene kan kjøres i VLC, MPV, eller lignende videoavspillingsprogram. Dette gir bl.a bedre kontroll over avspillingshastighet. Dersom du kjører programmet i Linux (eller macOS) og har youtube-dl installert vil du også kunne laste ned filene direkte. 

## Konfigurasjon
Du kan konfigurere programmet direkte i koden, eller gi argumet via kommandolinjen. Programmet trenger din session cookie og emnets ID. For nedlasting kan man også definere lokasjon.

    usage: kalturascraper.py [-h] [-c COOKIE] [-d DIR] [-g GALLERY]
  
    optional arguments:
    -h, --help                       show this help message and exit
    -c COOKIE, --cookie COOKIE       set cookie value
    -d DIR, --dir DIR                choose dir to store files
    -g GALLERY, --gallery GALLERY    choose gallery to scrape  

For å finne galleri-ID:
- Velg "Emne" fra menyen i Canvas
- Velg det aktuelle emnet
- ID-et er tallene i adresselinjen, etter "https://hvl.instructure.com/courses/" 

For å finne cookie: 
- Trykk på "Emnets mediefiler"
- I Firefox: Høyreklikk og velg "Inspiser element":
  - Velg "Storage", velg riktig nettside (https://354-1.kaltura.nordu.net/) og kopier verdien til "kms_ctamuls". 
<img src="cookies.jpg" width="600"></img>
- I andre nettlesere: Google it :-P 

Skriv verdiene inn i kalturascraper.py i de korresponderende variablene, "cookie" og "galleryID". Dersom du ikke definerer "dir" lastes filene ned i samme mappe som kalturascraper.py kjører i. 
