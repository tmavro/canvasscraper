# kalturascraper.py

Programmet genererer en liste med URL-er til alle videoene i et bestemt fag. Disse URL-ene kan kjøres i VLC, MPV, eller lignende program, som f.eks gir bedre kontroll over avspillingshastighet. Hvis du kjører programmet i Linux og har youtube-dl installert, så vil du også kunne laste ned individuelle eller samtlige videoer. 

## Konfigurasjon
Programmet konfigureres med session cookie og ID til faget/emnet. 

For å finne ID:
- Velg "Emne" fra menyen i Canvas
- Velg det aktuelle emnet
- ID-en er tallene i adresselinjen, etter "https://hvl.instructure.com/courses/" 

For å finne cookie: 
- Trykk på "Emnets mediefiler"
- I Firefox: Høyreklikk og velg "Inspiser element":
  - Velg "Storage", velg riktig nettside (https://354-1.kaltura.nordu.net/) og kopier verdien til "kms_ctamuls". 
<img src="cookies.jpg" width="600"></img>
- I andre nettlesere: Google it :-P 

Skriv verdiene inn i kalturascraper.py i de korresponderende variablene, "cookie" og "galleryID". 
