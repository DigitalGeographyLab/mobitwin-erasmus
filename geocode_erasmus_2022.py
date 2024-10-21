#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 11:46:26 2023

@author: tuomvais
"""

import pandas as pd
from geopy.geocoders import Photon, Nominatim
from geopy.extra.rate_limiter import RateLimiter
import glob
import geopandas as gpd
import time
import random

# Dictionary to fix words
umlaut_dict = {'?Bo':'Turku', 'Jyv?Skyl?':'Jyväskylä', '??D?':'Lodz', '?Da?I':'Adazi',
               '?Ehitkamil/Gaziantep':'Gaziantep', '?Esk? T??N':'Cesky Tesin',
               '?Eský T?Ín':'Cesky Tesin', '?Hringen':'Öhringen','?Ilina':'Zilina',
               '?Lenurme Vald, Tartumaa': 'Ülenurme vald, Tartumaa', '?Lkad?M':'Ilkadim',
               '?M?L':'Åmål','?Orum':'Corum', '?Rnomelj':'Crnomelj', '?Stanbul':'Istanbul',
               '?Stersund':'Östersund','?Vila':'Avila','?>mir':'Izmir','?Áslav':'Caslav',
               '?Ód?':'Lodz', 'K?Ln':'Köln', 'K?Benhavn': 'Copenhagen', 'Malm?':'Malmö',
               'G?Ttingen':'Göttingen','D?Sseldorf':'Düsseldorf', 'Val?Ncia':'Valencia',
               'Wroc?Aw':'Wroclaw', 'M?Nchen':'München','Troms?':'Tromsø', '??Cosia':'Nicosia',
               '??Rebro':'Örebro', '??Nekoski':'Äänekoski', '?Al?Inink?':'Salcininkai',
               '?Ankaya':'Cankaya', '?Anakkale':'Canakkele', '?Berlingen':'Überlingen',
               '?Brah?Mhegy':'Abrahamhegy', '?Eské':'Ceské', '?Eh?Tkam?L':'Sehitkamil',
               '?I?Li':'Sisli', '?Lborg':'Ålborg','?Od?':'Lodz','?Odz':'Lodz',
               '?Ndalsnes':'Åndalsnes','?Ngelholm':'Ängelholm','?Rhus':'Århus',
               '?Zmir':'Izmir','?Zm?R':'Izmir','A?Ores':'Azores', 'A?Rhus':'Århus',
               'Br?Ssels':'Brussels','Br?Ssel':'Brussels', 'Budape?Te':'Budapest',
               'Budapes?':'Budapest', 'Budape?':'Budapest', 'Bucure?T':'Bucurest',
               'C??Rdoba':'Cordoba','C?Rdoba':'Cordoba','C??Diz':'Cadiz','C?Diz':'Cadiz',
               'C?Ceres':'Caceres','M?Laga':'Malaga', 'Ch?Teau':'Chateau','Chi?In?U':'Chisinau',
               'Chi?Inau':'Chisinau', 'Coru?A':'Coruna', 'Cr?Teil':'Creteil',
               'Creteil?':'Creteil', 'D?Browa':'Dabrowa', 'D??Ín':'Decín',
               'D?Ssedorf':'Düsseldorf','D?Sseldorf':'Düsseldorf', 'F?S':'Fez',
               'Ey?P':'Eyüp', 'D?Ren':'Düren', 'D?Rpen':'Dörpen', 'Forc?':'Force',
               'Forl?':'Forli', 'Frankf?Rt':'Frankfurt', 'Frankfurt?Am Main':'Frankfurt Am Main',
               'G??Ttingen':'Göttingen','G??Teborg':'Gothenburg','G??Vle':'Gävle',
               'G?Teberg':'Gothenburg', 'G?Teborg':'Gothenburg', 'G?Teborgs':'Gothenburg',
               'G?Teburg':'Gothenburg','G?Tenborg':'Gothenburg','G?Tenborg':'Gothenburg',
               'G?Theburg':'Gothenburg', 'G?Tingen':'Göttingen', 'Gand?A':'Gandia',
               'Gij?N':'Gijon','Gr?Ningen':'Groningen','Gu?A':'Guia','H?Meenkoski':'Hämeenkoski',
               'H?Meenlinna':'Hämeenlinna','H?Nefoss':'Hønefoss','Hels?Nquia':'Helsinki',
               'Hyvink??':'Hyvinkää','I?-?Ejtun':'Iz-Zejtun','I?Awa':'Ilawa','Ia?I':'Iasi',
               'R?Union':'Reunion','Innsbr?Ck':'Innsbrück','Is-Si??Iewi':'Is-Swieqi',
               'Istambu?':'Istanbul','J?Nk?Ping':'Jönköping','J?Nkoping':'Jönköpinh',
               'J?Rmala':'Jurmala','J?Hvi':'Jöhvi','J?Lov?':'Jilove','J?Rf?Lla':'Järfälla',
               'J?RvenP??':'Järvenpää', 'J?Ri':'Jüri', 'J?Rna':'Järna','J?Vea':'Javea, Xabia',
               'J?Zef?W':'Jozefow','Ja?I?N?':'Jasiunai','Ja?N':'Jaén','Jo?Nko?Ping':'Jönköping',
               'Jyv??Skyl??':'Jyväskylä','Jyv?Skyla':'Jyväskylä','K??Benhavn':'København',
               'K??Ln':'Köln','K?C?Kcekmec':'Kücükcemece',
               'K?Daini?':'Kedainiu','K?Ditz':'Köditz','K?Dzierzyn-Ko?Le':'Kedzierzyn-Kozle',
               'K?Flach':'Köflach','K?Fstein':'Kufstein','K?Ge':'Køge', 'K?Hbach':'Kuhbach',
               'K?Lvi?':'Kälviä','K?Mes':'Kumes','K?Ngen':'Köngen','K?Nzell':'Künzell',
               'K?Odzko':'Klodzko','K?Penhamn':'Copenhagen','K?Pingsvik':'Köpingsvik',
               'K?R?Ehir':'Kirsehir','K?Rdla':'Kärdla','K?Rklareli':'Kirklareli',
               'K?Rs?M?Ki':'Kärsämäki','K?Rten':'Kürten','K?Tahya':'Kütahyatr','K?Tekli':'Kötekli',
               'K?Then':'Köthen','K?Zdiv?S?Rhely':'Kezdivasarhely','Kad?K?Y':'Kadiköy',
               'Kad?Köy':'Kadliköy', 'Ath?Nes':'Athens', 'Karlsr?He':'Karlsruhe',
               'Kl?Tze':'Klötze','Kr?Beln':'Kröbeln','Kr?Ko':'Krsko','Kr?L?V Dv?R':'Kraluv Dvur',
               'Kr?Luv':'Kraluv','Kr?N':'Krün','Kr?Ovsk?':'Kralovsky','Kr?Slava':'Kraslava',
               'Krak??W':'Kraków','Krak?W':'Kraków','Dv?R':'Dvur','Král?V':'Králuv',
               'Ku?Adas?':'Kusadasi','Ku?Çular':'KusÇular','Kun?T?T':'Kunstat',
               'Kyrksl?Tt':'Kirkkonummi',"L'?Le-Rousse":"L'ile-Rousse",'L?Aquila':"L'Aquila",
               'L?Bbecke':'Lübbecke','L?Beck':'Lübeck', 'L?Denscheid':'Lüdenscheid',
               'L?Dinghausen':'Lüdinghausen','L?Dz':'Lodz','L?Dzkiz':'Lodz',"L?Estartit":"L'Estartit",
               'L?Ffingen':'Löffingen','L?Ganuse':'Lüganuse','L?Ge-Cap-Ferret':'LéGe-Cap-Ferret',
               'L?Gst?R':'Løgstør','L?Hne':'Löhne','L?Hospitalet':"L'Hospitalet",
               'L?Neburg':'Lüneburg','L?Nen':'Lünen','L?On':'Leon','L?Renskog':'Lørenskog',
               'L?Rida':'Lérida','L?Rrach':'Lörrach','L?Signy':'Lésigny','L?Ttich':'Liege',
               'L?Tzebuerg':'Lëtzebuerg','L?Uila':"L'Aquila",'L?Vignac':'Lévignac',
               'L?Wen':'Löwen','L?Wenstein':'Löwenstein','L?Yli?Inen':'Läyliäinen',
               'L?Zarea':'Lazarea','L?Ze?Sk?':'Lazenska','Ca?Ada':'Cañada','Almer?A':'Almeria',
               'Coru??A':'Coruna','Coru?A':'Coruna','La Ch?Tre':'La Chatre','K?Nigshofen':'Königshofen',
               'Li?Ge':'Liege','La Vall?E':'La Vallée','Lab?Ge':'Labege','Lab?Jan':'Labejan',
               'Labeuvri?Re':'Labeuvriere','Le?N':'Leon','Le?A Da Palmeira':'Leca Da Palmeira',
               'Lehtim?Ki':'Lehtimäki','Lemf?Rde':'Lemförde','Li?Vin':'Liévin',
               'Liding?':'Lidingö','Liep?Ja':'Liepaja','Lillestr?M':'Lilleström',
               'Link?Pin':'Linköpin','Lle?Da':'Lleida','Logro?O':'Logroño','Londr?S':'London',
               'Lule?':'Luleå','Lun?Ville':'Lunéville','Lw?W':'Lviv','Lw?Wek':'Lwowek',
               'M ?Nchen':'München','M??Laga':'Malaga','M??Nchen':'München','M?Chela':'Michela',
               'M?Chen':'München','M?Con':'Macon','M?Dena':'Modena','M?Der':'Mäder',
               'M?Driku':'Mõdriku','M?Ga':'Muga','M?Gurele':'Magurele','M?Heim':'Mülheim',
               'M?Lheim':'Mülheim','M?Hlacker':'Mühlacker','M?Hlbachl':'Mühlbachl',
               'M?Hlhausen':'Mühlhausen','M?Hltal':'Mühltal','M?Isak?La':'Mõisaküla',
               'M?L?V':'Måløv','M?Lardalens':'Mälardalens','M?Ln?K':'Melnik','M?Lndal':'Mölndal',
               'M?Lnlycke':'Mölnlycke','M?Lník':'Melník','M?Ncheberg':'Müncheberg',
               'M?Nich':'Munich','M?Nih':'Munich','M?Nschen':'München','M?Nsheim':'Münsheim',
               'M?Nster':'Münster','M?Nter':'Münster','M?Ribel':'Méribel','M?Rida':'Merida',
               'M?Rignac':'Merignac','M?Rjamaa':'Märjamaa','M?Rrums':'Mörrum','M?Rsta':'Märsta',
               'M?Ru':'Méru','M?Rupe':'Marupe','Mac?Donie':'Macedonie','Malt?Zsk? N?M?St?':'Maltezske namesti',
               'Mar?N':'Marín','Mi?Os?Aw':'Miloslaw','Mi?Sk':'Minsk','Mil?N':'Milan',
               'Mil?Na':'Milan','Mil?O':'Milan','Mj?Vatn':'Myvatn','Mlad?':'Mladá',
               'Mod?Ice':'Modrice','Mod?Ne':'Modena','Mog?N':'Mogán','Moj?Car':'Mojácar',
               'Montr?Al':'Montréal','Moor?A':'Moura','Mor?E':'Moura','Msid?':'Msida',
               'Mu?':'Mus','Mu?La':'Mugla','Mu?Nchen':'München','N??Rnberg':'Nürnberg',
               'N?Ca':'Nica','N?Chod':'Nachod', 'N?Jera':'Nájera','N?Mes':'Nimes',
               'N?O':'Nõo','N?Poles':'Naples','N?Rnberg':'Nürnberg','N?Rager':'Nørager',
               'N?Rdlingen':'Nördlingen','N?Rresundby':'Nørresundby','N?Rtingen':'Nürtingen',
               'N?Stved':'Næstved','N?Tsch':'Nötsch','N?Ux':'Nœux','?esk? Bud?jovice':'Ceske Budejovice',
               'N?Vs?':'Navsi','Na??Czów':'Naleczów', 'P?Cs':'Pécs','P?Dova':'Padova',
               'M?Sto':'Mesto','P?Erov':'Prerov', 'P?Rnu':'Pärnu', 'Pyh?Salmi':'Pyhäsalmi',
               "P?Le De L'?Toile- Technop?Le De Ch?Teau-Gomber":"Pôle de l'Étoile Site de Château-Gomber",
               'R??Ga':'Riga','R?Ga':'Riga','R?Ma':'Roma','R?M?':'Rømø','R?Nde':'Rønde',
               'R?Nne':'Rønne','R?Ros':'Røros','R?Thymno':'Rethymno','Rh?Ne':'Rhone',
               'Ruda ?L?Ska':'Ruda Slaska','S?O Jo?O':'Sao Joao','S?O Juli?O':'Sao Juliao',
               'S?O Paio':'Sao Paio','S?O Paulo':'Sao Paulo','S?O Pedro':'Sao Pedro',
               'S?Omniki':'Slomniki','S?P?Lno Kraje?Skie':'Sepolno Krajenskie',
               'S?Pólno':'Sepólno','S?Villa':'Sevilla','S?Ville':'Sevilla','S?Vres':'Sévres',
               'S?Vrier':'Sévrier','Sain?Joki':'Seinäjoki','Sar?Yer':'Sariyer',
               'Sch?Bisch Gm?Nd':'Schwäbisch Gmünd','Set??Bal':'Setubal','Sevill?':'Sevilla',
               'Sey?Isfj?R?Ur':'Seyðisfjörður','Si?Na':'Siena','Sk??Vde':'Skövde','Sk?De':'Skövde',
               'Sk?Lsk?R':'Skælskør','Sk?Vde':'Skövde','St??Varfj?R?Ur':'Stoðvarfjordur',
               'St?Szew':'Staszow','Str?E':'Strée','Stor?S':'Storås','Str?Ngn?S':'Strängnäs',
               'T?Bingen':'Tübingen','T?Ebo?':'Treboc','T?Ebí?':'Treboc','T?EmoNice':'Tremosnice',
               'Tri?St':'Triest','Tur?N':'Turin','Ume?':'Umeå',
               'V?Lizy':'Vélizy','V?Ster?S':'Västerås','V?Steras':'Västerås', 'V?Xj?':'Växjö',
               'Val?Ia':'Valencia','Val?Ncia':'Valencia','Var?Ova':'Warsaw','Vaxj?':'Växjö',
               'Ven?Cija':'Venice','Veneti?':'Venice','Vi??A':'Vilna','Vi??Nu':'Villna',
               'W?En':'Vienna','W?Rzburg':'Würzburg','W?Zburg':'Würzburg','Wroc?Aw':'Wroclaw',
               'Wrz?Sowice':'Warsaw','Yl?J?Rvi':'Ylöjärvi','Z?Rich':'Zürich','Zapre?I?':'Zapresic',
               'Zl?N':'Zlin','T??Bingen':'Tübingen','Osnabr?Ck':'Osnabrück','TãBingen':'Tübingen',
               'Breslavia':'Warsaw','TNsberg':'Tønsberg','Dsseldorf':'Düsseldorf',
               'Mnchen':'München', 'c�dex':'Cedex','Pozna�':'Poznan','A Coru�A':'A Coruna',
               'Orl�Ans':'Orleans','Jyv�Skyl�':'Jyväskylä','Almer�A':'Almería',
               'Osnabr�Ck':'Osnabrück', 'T�?Bingen':'Tübingen','M�Nchen':'Munich',
               '�Rhus':'Århus',"Saint Barth�Lemy D'Anjou":"Saint Barthélemy D'Anjou",
               'W�Rzburg':'Würzburg', 'Eichst�Tt':'Eichstätt', 'D�Sseldorf':'Düsseldorf',
               'T�Bingen':'Tübingen', 'Gda�Sk':'Gdansk','M�Nster':'Münster',
               'L�Neburg':'Lüneburg', 'K�Ln':'Köln', 'Cz�Stochowa':'Czestochowa',
               'Almeri�A':'Almería','Marne-La-Vall�E':'Marne-La-Vallée','Gj�Vik':'Gjøvik',
               'Krak�W':'Kraków','C�Ceres':'Cáceres','Cr�Teil':'Créteil','Darn�Tal Cedex':'Darnétal',
               'Besan�On':'Besançon','S�Vres':'Sévres','S�Borg':'Søborg','Compi�Gne':'Compiégne',
               'P�Cs':'Pecs','Sant Cugat Del Vall�S':'Sant Cugat Del Vallés','Randers S�':'Randers Sø',
               'K�Ge':'Køge','Les Ponts-De-C�':'Les Ponts-De-Cé','Erlangen / N�Rnberg':'Erlangen',
               'N�Mes':'Nîmes','Saarbr�Cken':'Saarbrücken','Vilanova I La Geltr�':'Vilanova I La Geltrú',
               'Pi�A':'Pila','Elbl�G':'Elblag','Jaros�Aw':'Jaroslaw','Przemy�L':'Przemyśl',
               'G�D':'Göd','Sor�':'Sorø','�Rebro':'Örebro','K�Benhavn':'Copenhagen',
               'Avelar - Ansi�O':'Avelar','Eski�Ehir':'Eskişehir','Wroc�Aw':'Wroclaw',
               'Bia�A Podlaska':'Biala Podlaska','W�Oc�Awek':'Włocławek','Jelenia G�Ra':'Jelenia Góra',
               'Chamb�Ry':'Chambry','Matar�':'Mataró','Gij�N':'Gijón','N�Rnberg':'Nürnberg',
               'Diyarbak�R':'Diyarbakir','H�Meenlinna':'Hämeenlinna',
               'Eskilstuna And V�Ster�S (Twin Campus)':'Eskilstuna','Aubi�Re':'Aubiere',
               'T�Nsberg':'Tønsberg','J�Zef�W':'Jozefow','�Stanbul':'Istanbul',
               'Angoul�Me':'Angoulême','Karab�K':'Karabük','F�S':'Fes','Bing�L':'Bingöl',
               'M�Laga':'Malaga','K�Benhavn K':'Copenhagen','�Ahinbey':'Sahinbey',
               "St Jean D'Ardi�Res":"St Jean D'Ardiéres",'D�Zce':'Düzce','�Orum':'Corum',
               'Wa�Brzych':'Walbrzych','Sel�Uklu / Konya':'Selcuklu','R�Ga':'Riga',
               'Che�M':'Chelm','Forl�':'Forli','Zamo��':'Zamość','K�Rklareli':'Kırklareli',
               'P�Ock':'Plock','Toru�':'Torun','Gie�En':'Giessen','N�Rtingen':'Nürtingen',
               'Veszpr�M':'Veszprém','K�Benhavn V':'Copenhagen','Oliveira De Azem�Is':'Oliveira De Azeméis',
               'La Almunia De Do�A Godina':'La Almunia De Dona Godina','G�Ttingen':'Göttingen',
               'Pa�O De Arcos':'Paco De Arcos','��D�':'Lodz','Santa Br�Gida':'Santa Brigida',
               '�Anakkale':'Çanakkale','Lesparre M�Doc Cedex':'Lesparre-Médoc',
               'Avil�S':'Avilés','Wola (Gmina Mied�Na)':'Wola (Gmina Miedzna)',
               'Sz�Kesfeh�Rv�R':'Székesfehérvár','Guimar�Es':'Guimaraes','Noum�A':'Nouméa',
               'Castell�N':'Castellón','Bielsko-Bia�A':'Bielsko-Biala','G�Rlitz':'Görlitz',
               'Ke�I�Ren':'Keçiören','Donostia San Sebasti�N':'Donostia San Sebastián',
               '�Vila':'Ávila','G�Og�W':'Głogów','G�Teborg':'Göteborg',
               'Porri�O':'Porrino','Covilh�':'Covilha','Rzesz�W':'Rzeszow','St. P�Lten':'St. Pölten',
               '?�D?':'Lodz','V�Cklabruck':'Vöcklabruck','Racib�Rz':'Raciborz','Vit�Ria - Es':'Vitória',
               'Bal�Kesir':'Balikesir','B�K�Scsaba':'Békéscsaba','�Stersund':'Östernsund',
               'M�Rida':'Mérida','M�Stoles':'Móstoles','Romans-Sur-Is�Re':'Romans-Sur-Isere',
               'Kecskem�T':'Kecskemét','T�Rrega':'Tarrega','Saint-Leu-La-For�T':'Saint-Leu-La-Forêt',
               'Kri�Evci':'Krizevci','Alcal� De Guada�Ra':'Alcalá De Guadaíra',
               'H�Rouville-Saint-Clair':'Hérouville-Saint-Clair','Logro�O':'Logrono',
               'Lom�':'Lomé','Kaposv�R':'Kaposvar','Zapre�I�':'Zapresic','Gorz�W Wielkopolski':'Gorzow Wielkopolski',
               '�Akovec':'Cakovec','Les Ponts De C�':'Les Ponts De Cé','Ansi�O':'Ansião',
               'Bia�Ystok':'Bialystok','P�Rnu':'Pärnu','S�O Paulo':'Sao Paulo','Szeksz�Rd':'Szekszard',
               'V�Ru':'Võru','San Sebasti�N':'San Sebastián','Almunia De Do�A Godina (La)':'La Almunia De Doña Godina',
               'Svolv�R':'Svolvær','Yaound�':'Yaoundé','Ciudad De M�Xico':'Ciudad De Mexico',
               'Hradec Kr�Lov�':'Hradec Králové','Bansk� Bystrica':'Banská Bystrica',
               '�Bo':'Turku','Kij�W':'Kyiv','�Om�A':'Łomża','St-L�':'Saint-Lô','V�Nn�S':'Vännäs',
               'Artigues Pr�S Bordeaux':'Artigues Prés Bordeaux','V�Xj�':'Växjö','Bod�':'Bodø',
               '��Rnak':'Sirnak','Pouanc�':'Pouancé','V.N. Famalic�O':'Vila Nova de Famalicão',
               'Fat�H':'Fatih','Ciudad Aut�Noma De Buenos Aires':'Buenos Aires',
               'M�Isak�La':'Mõisaküla','Alcal� De Henares':'Alcalá De Henares',
               'Bogot� D.C.':'Bogota','�Hringen':'Öhringen','Donostia-San Sebasti�N':'Donostia San Sebastián',
               'B�Tera (Valencia)':'Bétera (Valencia)','Prishtin�':'Pristina',
               'Villaviciosa De Od�N':'Villaviciosa De Odon','Ja�N':'Jaén',
               'Saint Laurent Sur S�Vre':'Saint Laurent Sur Sévre','Goleni�W':'Goleniow',
               '�Esk� T��N':'Ceská Tesin','Reykjav�K':'Reykjavik','Alcorc�N':'Alcorcón',
               'Po�Ega':'Pozega','Argel�S Sur Mer':'Argeles Sur Mer','F�Rstenwalde':'Fürstenwalde',
               'M�Driku':'Mõdriku','T�Rnitz':'Ternitz','M?Ln�K':'Melnik','T�Rkeve':'Túrkeve',
               '�Ankaya':'Cankaya','Legan�S':'Leganes','Vi�Osa':'Vicosa','Amb�Rieu En Bugey':'Ambérieu En Bugey',
               'K�Benhavn V':'Copenhagen','Mi�Sk Mazowiecki':'Minsk Mazowiecki','Veresegyh�Z':'Veresegyház',
               'Pu�Tusk':'Pultusk','�Ehitkamil/Gaziantep':'Sehitkamil, Gaziantep',
               'Montr�Al, Qu�Bec':'Montréal, Québec','N�Tsch':'Nötsch im Gailtal',
               'Bogot�':'Bogotá','C�Rdoba':'Cordoba','Livron Sur Dr�Me':'Livron Sur Drôme',
               'Magyaralm�S':'Magyaralmás','Le�N':'León',"La Vall D'Uix�":"La Vall D'Uixó",
               'La Ca�Ada De San Urbano De Almer�A':'La Canada De San Urbano De Almería',
               'Fr�Jus':'Fréjus','Karagandy�':'Karaganda','Fez�':'Fez','Sal�':'Salé',
               'Skrzysz�W':'Skrzyszów','M?Isak�La':'Mõisaküla','Micha�Owo':'Michalowo',
               'Lw�W':'Lviv','Bel�M':'Belém','Izm�R':'Izmir','Ziguinchor�':'Ziguinchor',
               'Rychnov Nad Kn?�Nou':'Rychnov Nad Kneznou','�M�L':'Åmål','Mosc�':'Moscow',
               'Vila Real De Santo Ant�Nio':'Vila Real De Santo Antonio','Praia Da Vit�Ria':'Praia Da Vitória',
               'Lous�':'Lousa','Fund�O':'Fundao','C�Mara De Lobos':'Camara De Lobos',
               'L�Beck':'Lübeck','Schw�Bisch Gm�Nd':'Schwäbisch Gmünd','Sch�Nebeck':'Schönebeck',
               'Wa�Cz':'Walcz','Nyk�Bing F.':'Nykøbing Falster','Se�L':'Seoul',
               'Dammarie-L�S-Lys':'Dammarie-Lés-Lys','Balatongy�R�K':'Balatongyörök',
               'Santa Eul�Ria Des Riu':'Santa EulaRia Des Riu','Belin-B�Liet':'Belin-Béliet',
               'Ch�Teauroux':'Chateauroux','P�Rigueux':'Périgueux','Nagyv�Zsony':'Nagyvázsony',
               'Pary�':'Paris','Link�Ping':'Linköping','Sp�Nga Stockholm':'Spånga, Stockholm',
               'Ume�':'Umeå','�St� Nad Labem':'Ústí Nad Labem','Charbonni�Res Les Bains':'Charbonniéres Les Bains',
               'Burgst�Dt':'Burgstädt','�Esk� L�Pa':'Ceska Lipa','�S':'Ås','�Rnomelj':'Crnomelj',
               'N�Chod':'Náchod','Dunajsk� Streda':'Dunajská Streda','G�Vle':'Gävle',
               'Belv�':'Belví','Pir� Sur Seiche':'Pire Sur Seiche','Partiz�Nske':'Partizánske',
               'Sz�Kelyudvarhely':'Székelyudvarhely','Encarnaci�N':'Encarnacion',
               'Vila Nova De Famalic�O':'Vila Nova De Famalicao','F�Rth (Odenwald)':'Fürth (Odenwald)',
               'Sacav�M':'Sacavem',"Castelnau D�Estretefonds":"Castelnau D'Estretefonds",
               'Hamb�Hren':'Hambühren','Kr�Beln':'Kröbeln','Castelnau De M�Doc':'Castelnau De Medoc',
               'Lourinh�':'Lourinha','K�Ditz':'Köditz','Saint Nicolas Du P�Lem':'Saint Nicolas Du Pélem',
               'Cerb�Re':'Cerbere','Star� �Ubov�A':'Stará Lubovna','St Denis R�Union':'Saint-Denis Réunion',
               'Mu�':'Muş','F�Camp':'Fécamp','Krzywy R�G':'Kryvyi Rih',
               'Cours De Mons�Gur':'Cours De Monségur','Chark�W':'Kharkiv',
               'La Fert� Sous Jouarre':'La Ferté-Sous-Jouarre','Targovi�Te':'Targovishte',
               'Lab�Ge':'Labége','Lab�Jan':'Labéjan','Le Port (La R�Union)':'Le Port (La Réunion)',
               'Cort�':'Corté','Gasp�':'Gaspé','Clohars-Carno�T':'Clohars-Carnoët',
               'Sel�Uk':'Selcuk','Trois-Rivi�Res (Qu�Bec)':'Trois-Riviéres (Québec)',
               'To�Nic':'Tocnica','Concepci�N':'Concepcion',"Clermont L'H�Rault":"Clermont L'Hérault",
               'L�Vignac':'Lévignac','Ch�Tellerault':'Châtellerault','Medell�N':'Medellin',
               'Kamenick� �Enov':'Kamenický Senov','Krom??�':'Kromeriz','Kun�T�T':'Kunstat',
               'M�Rignac':'Mérignac','M�Ln�K':'Melnik','Naintr�':'Naintré',
               'Zempl�Nske H�Mre (Slovakia)':'Zemplínske Hámre','Tren?�N':'Trencín',
               'B�Ziers':'Beziers','Mei�Ner Weidenhausen':'Meißner Weidenhausen',
               'L�Nen':'Lünen','Kisv�Rda':'Kisvárda','D�Ms�D':'Domsod','Niska-Pietil�':'Niska-Pietilä',
               'Hradec Kr�Lov� ':'Hradec Kralové','Benalm�Dena':'Benalmádena','E�K':'Ełk',
               'Hyvink��':'Hyvinkää','Cabra C�Rdoba':'Cabra Córdoba','Chorz�W':'Chorzów',
               'Calvi�':'Calvia','Boles�Aw':'Boleslaw','Can�Rias Island':'Canary Islands',
               'Cerdanyola Del Vall�S':'Cerdanyola Del Vallés','Kiskunf�Legyh�Za':'Kiskunfélegyháza',
               '�Lesund':'Ålesund','��Nekoski':'Äänekoski','El Roc�O':'El Rocío',
               'Troms�':'Tromså','Fr�Mista (Palencia)':'Frómista','Ny�Regyh�Za':'Nyíregyháza',
               'P�Pa':'Pápa','R�Ckereszt�R':'Ráckeresztúr','San Crist�Bal De La Laguna':'San Cristóbal De La Laguna',
               'Santa Br�Gida, Gran Canaria, Las Palmas':'Santa Brígida, Gran Canaria, Las Palmas',
               '?Da�I':'Adazi','Panev?�Ys':'Panevezys','Kai�Iadori? Rajonas':'Kaisiadoriu Rajonas',
               'Oca�A':'Ocaña','Maharashtra�':'Maharashtra','G�Ra Kalwaria':'Góra Kalwaria',
               'Balatonf�Red':'Balatonfüred','L�Rrach':'Lörrach','S�Upsk':'Slupsk','Mar�N':'Marín',
               '�Ory':'Zory','Nesse-Apfelst�Dt Ot Neudietendorf':'Nesse-Apfelstädt Ot Neudietendorf',
               '�Agiewniki':'Lagiewniki','Zielona G�Ra':'Zielona Góra','Pl�N':'Plön',
               'Schwabm�Nchen':'Schwabmünchen','B�Gles':'Bégles','St-Andr� De Cubezac':'Saint-André-De-Cubezac',
               'Wodzis�Aw �L�Ski':'Wodzislaw Slaski','Boissy Saint L�Ger':'Boissy Saint Léger',
               'Sch�Nwalde-Glien':'Schönwalde-Glien','Silcherstra�E':'Silcherstrasse',
               'Surg�Res':'Surgéres','Klimont�W':'Klimontów','Tr�Glitz':'Tröglitz',
               'Unterschlei�Heim':'Unterschleissheim','Billi�Re (Via Toulouse)':'Billiére',
               'Trang�':'Trangé','Villefranche Sur Sa�Ne':'Villefranche Sur Saône',
               'R�Nne':'Rønne','S�Nderborg':'Sønderborg','O�Awa':'Olawa','O�?Awa':'Olawa',
               'Vitry-Le-Fran�Ois':'Vitry-Le-Francois','�Gly':'Égly','L�Dz':'Lodz',
               'Krosno Odrza�Skie':'Krosno Odrzańskie','S�Borg':'Søborg',
               'La Ca�Ada De San Urbano De Almería':'La Cañada De San Urbano De Almería',
               'Wodzis�Aw �LÅski':'Wodzislaw Slaski', '������ �������': 'Veliko Tarnovo',
               'Li�Ge':'Liége','C�Diz':'Cádiz','Ath�Na':'Athens','Villanueva De La Ca�Ada':'Villanueva De La Cañada',
               'Malm�':'Malmö','J�Nk�Ping':'Jönköping','Lule�':'Luleå','Falun And Borl�Nge (Twin Campus)':'Falun',
               'Ath�Nes':'Athens','Val�Ncia':'Valencia','Trollh�Ttan':'Trollhättan',
               'S�Ville':'Sevilla','Sk�Vde':'Skövde','Bragan�A':'Braganca','Duna�Jv�Ros':'Dunaújváros',
               'Sein�Joki':'Seinäjoki','Br�Hl':'Brühl','Pointe � Pitre':'Pointe á Pitre',
               'Ru�Omberok':'RuzOmberok','Saint-Denis De La R�Union':'Saint-Denis De La Réunion',
               'Set�Bal':'Setubal','Jerez De La Frontera (C�Diz)':'Jerez De La Frontera (Cádiz)',
               'Göd�Ll�':'Gödöllö','Ko�Ice':'Kosice','�Ilina':'Zilina','Mlad� Boleslav':'Mlada Boleslav',
               'Wiede�':'Wiedeń','Donauw�Rth':'Donauwörth','�Lenurme Vald, Tartumaa':'Ülenurme Vald, Tartumaa',
               'Dubl�N':'Dublin','Mil�O':'Milano','�Vora':'Èvora','M�Lndal':'Mölndal',
               'Algeciras, C�Diz':'Algeciras, Cádiz','Orosh�Za':'Orosháza','Br�Nderslev':'Brønderslev',
               '�Lborg':'Aalborg','G�Nova':'Genoa','Nyk�Bing F':'Nykøbing Falster',
               "Saint-Martin-D'H�Res":"Saint-Martin-D'Héres",'?Esk� Bud?Jovice':'Ceska Budejovice',
               "Ta� Xbiex":"Ta' Xbiex","Santar�M":"Santarem","Cornell� De Llobregat":"Cornella De Llobregat",
               'N�Rresundby':'Nørresundby','Gy�R':'Gyor','Pozuelo De Alarc�N':'Pozuelo De Alarcón',
               'N�Poles':'Naples','Gy�NgyÅs':'Gyöngyös','L�Gst�R':'Løgstør',
               'Castell� De La Plana':'Castellón De La Plana','Berl�N':'Berlin','Coru�A':'A Coruña',
               'Gr�Ningen':'Groningen','�Aglin':'Ogulin','R�Nde':'Rønde','B�Blingen':'Böblingen',
               'Pointe-�-Pitre':'Pointe-a-Pitre','Kr�Ko':'Krsko','T�Rgu Mure?':'Târgu Mures',
               '������':'Burgas','Odense S�':'Odense','Stra�Burg':'Strasburg',
               'P�Voa De Lanhoso':'Póvoa De Lanhoso','H�Meenkoski':'Hämeenkoski','K�?Benhavn C':'Copenhagen',
               'Czerwony B�R':'Czerwony Bór','P�Dua':'Padua','Rheda-Wiedenbr�Ck':'Rheda-Wiedenbrück',
               'Bucure�Ti':'Bucharest','Kad?K�Y - Istanbul':'Istanbul','We�Ling':'Wessling',
               "Saint Martin D'H�Res":"Saint Martin D'Héres",'A�Ores':'Azores','La Coru�A':'La Coruña',
               'M�Dena':'Modena','Klagenfurt Am W�Rthersee':'Klagenfurt Am Wörthersee',
               'K�Mes':'Kémes','Steinh�Fel':'Steinhöfel','J�Rvenp��':'Järvenpää',
               'Stryn�, Rudk�Bing':'Strynø, Rudkøbing','Wettin-L�Bej�N':'Wettin-Löbejün',
               'Chambry C�Dex':'Chambry','J�Nkoping':'Jönkoping','Kitzb�Hel':'Kitzbühel',
               'Lehtim�Ki':'Lehtimäki','Beyaz��T, �Istanbul':'Istanbul','�Gueda':'Àgueda',
               'Sau��Rkr�Kur':'Sauðárkrókur','Veneti�':'Venice','Jarosz�W':'Jaroszów',
               'Tatab�Nya':'Tatabánya','R�Yken':'Røyken','K�Pavogur':'Kópavogur',
               'Lyon C�Dex 08':'Lyon','Evry C�Dex':'Evry','Ut�':'Utö','Pre�Ov':'Presov',
               'La Louvi�Re':'La Louviére','Gren�':'Grenø','Vars�Via':'Warsaw',
               'S�Dert�Lje':'Södertälje','B�Kara':'Birkirkara','Mil�N':'Milan',
               'La Ca�Ada De San Urbano':'La Cañada De San Urbano','Le������N':'Leon',
               'K�Rs�M�Ki':'Kärsämäki','Unterf�Hring':'Unterföhring','H�RnÅsand':'Härnösand',
               'Bratys�Awa':'Bratislava','M�Lheim An Der Ruhr':'Mũlheim An Der Ruhr',
               'B�Y�Kcakmece Istanbul':'Büyükçekmece','Aubi���??Re':'Aubiére',
               'Domaszk�W':'Domaszków','Istambu�':'Istanbul','Amesterd�O':'Amsterdam',
               'M�Nich':'Munich','Nova Gradi�Ka':'Nova Gradiska','Soko�Owsko':'Sokolowsko',
               'Carthag�Ne':'Cartagena','Saint-�Tienne':'Saint-Étienne','Paris La D�Fence':'Paris',
               'Gr�Nheide':'Grũnheide','K�Rdla':'Kärdla','Liptovsk� Mikul�':'Liptovsky Mikulas',
               'S�P�Lno KrajeÅskie':'Sepolno Krajenskie','C������Rdoba':'Cordoba',
               'J��Ping':'Jönköping',"L�Aquila":"L'Aquila",'Poznan�??�':'Poznan',
               'Santa Pon�A':'Santa Ponsa','Gu�A De Isora':'Guía De Isora','�Kofja Loka':'Skofja Loka',
               'G�Nes':'Genoa','Rajeck� Teplice':'Rajecké Teplice',"Pa�O D'Arcos":"Paco De Arcos",
               'Pamplona - Iru�A':'Pamplona','Norrk�Ping':'Norrköping','D�Ren':'Düren',
               'Plze�':'Plzen','G�Is':'Guia','Ringk�Bing':'Ringkøbing','J�Lich':'Jülich',
               'Castell�':'Castalla','Åsk�Dar/Istanbul':'Istanbul','�?Skǭdar/�Istanbul':'Istanbul',
               '95094 Cergy C�Dex':'Cergy','M�L�V':'Målöv','G�Teburg':'Göteborg',
               'Hafnarfj�R�Ur':'Hafnarfjörður','Bystrzyca K�Odzka':'Bystrzyca Klodzka',
               'L�Tzebuerg':'Lëtzebuerg','Boqueix�N':'Boqueixón','S�Te':'Séte','Forc�':'La Force',
               'Plicht�W':'Plichtów','Rheinm�Nster':'Rheinmünster','L�Denscheid':'Lüdenscheid',
               'Le Kremlin-Bic�Tre':'Le Kremlin-Bicêtre','Garaf�A':'Garafía','Copenhagen �':'Copenhagen',
               'Su�De':'Stockholm','H�Lar':'Hólar','Alcal�':'Alcalá','Co�Mbra':'Coimbra',
               'G�?Teborg':'Göteborg','K�Then':'Köthen','Nyk�Ping':'Nyköping','Portim�O':'Portimao',
               'V�Rpalota':'Várpalota','Göd�Ll?':'Gödöllö','H�Rstel':'Hörstel',
               'Alcal�� De Henares':'Alcalá De Henares','�Rkelljunga':'Örkelljunga',
               'G�Ppingen':'Göppingen','Besan�?On':'Besancon','Le�A Da Palmeira':'Leca Da Palmeira',
               '�Rebo':'Örebro','H�Gersten':'Hägersten','S�Tubal':'Setubal','H�Rning':'Herning',
               'Oj�N':'Ojén','Karab?�K':'Karabük','V�Lizy-Villacoublay':'Vélizy-Villacoublay',
               'H�Rsholm':'Hørsholm','Ostrava - Z�B?Eh':'Ostrava','Byt�W':'Bytów','Crac�Via':'Kraków',
               'N�Vs�':'Návsí','Dabrowa G�Rnicza':'Dabrowa Górnicza','Orl���?�Ans C���?�Dex 2_X000B__X000B_':'Orléans',
               'Kokem�Ki':'Kokemäki','Cr�Te':'Crete','Kadik�Y Istanbul':'Istanbul',
               'J�Hvi':'Jõhvi','P�Jara':'Pájara','Gr�Dek':'Gródek','T�Rva':'Tõrva',
               'Saint-�Tienne-Du-Rouvray':'Saint-Étienne-Du-Rouvray','Jyvaskyl�':'Jyväskylä',
               'Kremsm�Nster':'Kremsmünster','Nemen�In?':'Nemencine','Ath�Ne':'Athens',
               'Be�Ikta�':'Besiktas','M�Ncheberg Ortsteil Trebnitz':'Müncheberg',
               'Bal�Ova-Izmir':'Balcova-Izmir','Z�Rich':'Zürich','Bre�A Alta':'Breña Alta','V�C':'Vec',
               'Vaux-Sous-Ch�Vremont':'Vaux-Sous-Chévremont','Set�?Bal':'Setubal',
               'Bagnols Sur C�Ze Cedex':'Bagnols Sur Céze','Reykjanesb�R':'Reykjanesbær',
               'Sk�?Vde':'Skövde',"Sant�Agata Bolognese":"Sant'Agata Bolognese",
               'Li�Ge, Belgique':'Liége','Floren�A':'Florence','Gr�Ce-Hollogne':'Grâce-Hollogne',
               'Quakenbr�Ck':'Quakenbrück','Ma�Eikiai':'Mazeikiai','Gro�-Enzersdorf':'Groß-Enzersdorf',
               'P�Daste Village, Muhu Parish':'Pädaste, Muhu','Toulouse C�Dex 9':'Toulouse',
               'J�Rf�Lla':'Järfälla','Santa Perp�Tua De Mogoda':'Santa Perpétua De Mogoda',
               'Loul�':'Loulé','Sant Vicen� Dels Horts Barcelona':'Sant Vicente Dels Horts',
               'Reith Bei Kitzb�Hel':'Reith Bei Kitzbühel','M�Chela (Michelau)':'Michelau',
               'Fl�Malle':'Flémalle','R�Jiena':'Rujiena','Valdepe�As':'Valdepeñas',
               'Ile De La R�Union':'La Réunion','4000 Li�Ge':'Liége','San Bartolom� De Tirajana':'San Bartolomé De Tirajana',
               "Ta�Qali":"Ta' Qali",'�Vry':'Évry','Juran�On':'Jurancon','Benicarl�':'Benicarló',
               'V�Lez-Malaga':'Vélez-Malaga','Dvur Kr�Lov� Nad Labem':'Dvur Kralove Nad Labem',
               'Inder�Y':'Inderøy','H�Xter':'Höxter','Alen�On':'Alencon','G�Tersloh':'Gütersloh',
               'H�Je Taastrup':'Høje Taastrup','Zl�N':'Zlín','Bad Br�Ckenau':'Bad Brückenau',
               'Gr�Felfing':'Grärelfing','C���?�Diz':'Cádiz','La Ca�Ada, Almeria':'La Cañada, Almeria',
               'Riihim�Ki':'Riihimäki','Bagsv�Rd':'Bagsværd','D�Nia':'Dénia',
               'AlsÅszentm�Rton':'Alsószentmárton','Hiller�D':'Hillerød','Helsing�R':'Helsingør',
               'B�Hl':'Bühl','Jandia P�Jara':'Pájara','Col�Nia':'Köln','Buda�Rs':'Budaörs',
               'Doln� Kub�N':'Dolny Kubin','Veli Lo�Inj':'Veli Losinj','Su�Ice':'Susice',
               'Ma�':'Malaga','Mog�N':'Mozón','Dob�Any':'Dobrany','D�Cines-Charpieu':'Décines-Charpieu',
               'Ponta Delgada S Miguel A�Ores':'Ponta Delgada Azores','Hradec Kr�Love':'Hradec Králove',
               'Padr�N':'Padrón','Celr�':'Celra','K�Lvi�':'Kälviä','�Ksendal':'Øksendal',
               'Vara�Din':'Varazdin','Mondrag�N':'Mondragón','Tarn�W':'Tarnów',
               'Krausnick-Gro� Wasserburg':'Krausnick-Groß Wasserburg','Korntal-M�Nchingen':'Korntal-Münchingen',
               'Pierre-B�Nite':'Pierre-Bénite','Paris La D�Fense':'Paris La Defense',
               'S. Teot�Nio':'Sao Teotónio','Corf�':'Corfu','Alcalá� De Henares':'Alcalá De Henares',
               'Lauda-K�Nigshofen':'Lauda-Königshofen','Port De S�Ller':'Port De Sóller',
               'Siglufj�R�Ur':'Siglufjördur','�Ngelholm':'Ängelholm','�Ystese':'Øystese',
               'Donauw�Rt':'Donauwörth','Aleja Lotnik�W Polskich 1':'Swidnik',
               'Sey�Isfj�R�Ur':'Seyðisfjörður','D�Rzbach':'Dörzbach','Zabierz�W':'Zabierzów',
               'Schw?Bisch Gm�Nd':'Schwäbisch Gmünd',"Port D'Alc�Dia":"Port D'Alcúdia",
               "S'Agaro G�Rone":"S'Agaro",'F�Rth':'Fürth','Sant Vicen� Dels Horts - Barcelona':'Sant Vicente Dels Horts',
               'Villeneuve D�Ascq Cedex':"Villeneuve–D'Ascq",'Gerlingen Schillerh�He':'Gerlingen Schillerhöhe',
               'Gerlingen-Schillerh�He':'Gerlingen Schillerhöhe','K�Odzko':'Kloddzko',
               'Glockengie�Erwall 2, 20095 Hamburg, Tyskland':'Hamburg','Pieks�M�Ki':'Pieksämäki',
               'Vitr�':'Vitré','Ag�Imes':'Agüimes','V�Nissieux':'Vénissieux',
               'Campus Rotenb�Hl':'Saarbrücken','B�Rgel':'Bürgel','B�Nde':'Bünde',
               'Schw�Bisch Hall':'Schwäbisch Hall','Kriv�':'Krivá','T�Inec':'Trinec',
               'Cerde�A':'Sardinia','Co. Comt� De Waterford':'Waterford',
               'Schw�Bisch-Gm�Nd':'Schwäbisch-Gmünd','Hlbok�':'Hlboké','Sj�Vegan':'Sjøvegan',
               'Dubnica Nad V�Hom':'Dubnica Nad Váhom','Bratislava - Dev�Nska Nov� Ves':'Bratislava',
               'Asni�Res-Sur-Seine':'Asnieres-Sur-Seine','Varmahl��':'Varmahlíð',
               'B�Lh':'Bühl','Baden-W�Rttemberg':'Baden-Württemberg','�Alec':'Zalec',
               'Bernsdorf Ot Strassgr�Bchen':'Bernsdorf','Cabe�A Gorda':'Cabeça Gorda',
               'Se�Ana':'Sena','Roga�Ka Slatina':'Rogaska Slatina','Portoro�':'Portoroz',
               'Dom�Ale':'Domzale','Avd. Lamadosa, 16 � C.P. 15009 Santiago De  Compostela':'Santiago De  Compostela',
               'Playa De Las Am�Ricas Teneriffa':'Playa De Las Américas Teneriffa',
               'A Ba�A':'A Baña','R�Thymno':'Réthymno','H�Dmez?VÅs�Rhely':'Hódmezővásárhely',
               'H�Chberg':'Höchberg','N�O, Tartumaa':'Nõo','�Ibenik':'Sibenik',
               'Torrej�N De Ardoz, Madrid':'Madrid','Mei�En':'Meissen','Munich�':'Munich',
               'Pomiech�Wek':'Pomiechówek','F�Rjestaden':'Färjestaden','Finsp�Ng':'Finspång',
               'L�Ganuse Vald':'Lüganuse Vald','Kohtla-J�Rve':'Kohtla-Järve','S�Villa':'Sevilla',
               'Kilingi-N�Mme':'Kilingi-Nõmme','M�Llheim':'Mülheim an der Ruhr',
               'M�Ncheberg':'Müncheberg','M�Nih':'Müchen','731 97 K�Ping':'Köping',
               'Pruszk�W':'Pruszków','Rinc�N De La Victoria':'Rincón De La Victoria',
               'Ia�I':'Iasi','�Lhavo':'Ílhavo','Pforzheim, Baden-W�Rttemberg':'Pforzheim',
               'Vair�O':'Aveiro','Feh�Rgyarmat':'Fehérgyarmat','Valdepi�Lagos':'Valdepiélagos',
               'H�Gskolan Dalarna':'Dalarna','H�Lo':'Hölö','Villanueva De G���?�Llego':'Villanueva De Gállego',
               'Pyrgos (�Lide)':'Pyrgos','H�Nfeld':'Hünfeld','H�Rnum':'Hörnum','H�Rth':'Hürth',
               'HÅsav�K':'Húsavík','Schalksm�Hle':'Schalksmühle','D�N Laoghaire':'Dún Laoghaire',
               'Saltsj�Baden':'Saltsjöbaden','Ka�Tel Luk�I�':'Kastel Luksic','Ole�Nica':'Oleśnica',
               'Santa Eul�Lia- Ibiza':'Santa Eularia des Riu','H�V�Z':'Hévíz','M�Rsta':'Märsta',
               'K�Nzell':'Künzell','Gar�Ab�R':'Gardabaer','Su�Any':'Siauliai','M�Lnlycke':'Mölnlycke',
               'R�Uge':'Rõuge','Lindenberg Im Allg�U':'Lindenberg Im Allgäu','Zapre�I?':'Zapresic',
               'Lutter-F�Rstenhagen':'Uder','Tch�Que - R�Publique':'Prague',
               'Vento - Arena - Tenerife - Spain / Espa�A':'Tenerife','Norv�Ge':'Oslo',
               'Praha�2':'Prague','C��Diz':'Cádiz','Belgi�':'Brussels','Braine Le Ch�Teau':'Braine-Le-Château',
               'Nil�Fer Bursa':'Nilüfer Bursa','Braine-Le-Ch�Teau':'Braine-Le-Château',
               'Brussel�Les':'Brussels','La R�Union':'La Réunion','El Puerto De Santa Mar�A':'El Puerto De Santa María',
               'Ozoir-La-Ferri�Re':'Ozoir-La-Ferriere','Donostia � San Sebastián':'San Sebastián',
               'Madrid - Espa�A':'Madrid','Gu�Rande':'Guérande','Zweibr�Cken':'Zweibrücken',
               'V�Nersborg':'Värnersborg','�?Rebro':'Örebro','�Jebyn':'Öjebyn','�Lvsj�':'Älvsjö','�Re':'Åre',
               '�Rebr�':'Örebro','V�Rby':'Vårby','V�Llingby':'Vällingby','Sp�Nga':'Spånga','Sj�Levad':'Sjölevad',
               'Sp�Nga, Stockholm':'Spånga',"Meslin L'Ev�Que":"Meslin L'Évêque",
               'Cucuj�Es, Oliveira De Azeméis':'Oliveira De Azeméis','Piet�':'Pieta','Neupr�':'Neupré',
               'P�Ruwelz':'Péruwelz','Qui�Vrain':'Quiévrain','R�Ves':'Réves','Ta�Xbiex':'Ta Xbiex',
               'Ctra. Circunvalaci�N Mijas, 0, 29650 Mijas, Malaga, Spain':'Mijas, Malaga',
               'Beyaz?�T, ?Istanbul':'Istanbul','Cinf�Es':'Cinfães','Stambu�':'Istanbul',
               'Tr�Vise':'Treviso','K�Flach':'Köflach', 'Lyon�Cedex�07':'Lyon',
               'Grazstra�Enbahnen 1, 7':'Graz','Ja���?�N':'Jaén','Val�I?N? K.':'Vilnius',
               '�Alcininkai':'Salcininkai','Glasgow�City':'Glasgow','�Al�Inink? R':'Salcininkai',
               'Craigavad � Holywood - Co Down':'Craigavad','Coventry�':'Coventry',
               'Holb�K':'Holbæk','�Orlu':'Çorlu','V�Lkermarkt':'Völkermarkt','�Al�Ininkai':'Salcininkai',
               '�Ytawa/Zgorzelec':'Görlitz','Obersch�Tzen':'Oberschütze','�Igli - Izmir':'Çiğli',
               'Lle�Da':'Lleida','Le Puy Ste R�Parade':'Le Puy-Ste-Réparade','St. Primus / �Entprimo�':'Sankt Primus',
               'Ik��Ile':'Ikšķile','L�Estartit':"L'Estartit",'N�Ca':'Nica',
               'Kysuck� Nov� Mesto':'Kysucké Nové Mesto','Gr�Ndola':'Grandola',
               'Kr�L�V Dv�R':'Králov dvor','M��Laga':'Malaga','Lib�Chov':'Libechov',
               'L�ZeÅsk�':'Luze','Peg�Es':'Pegoes','Mal� Strana':'Malá Strana',
               'Cergy C�Dex':'Cergy','�Migr�D':'Zmigród','Sver�Ov':'Sverzov',
               'Star� Mesto':'Staré Mesto','Star� Bystrica':'Stará Bystrica',
               'Sp�Thsttabe':'Berlin','Rimavsk� Sobota':'Rimavská Sobota',
               'Prague 1 Mal� Strana':'Prague','Brian�On':'Briancon','Bollullos De La Mitaci�N':'Bollullos De La Mitación',
               'Praha 1 - Nov� Mesto':'Prague','PrÅst�':'Præstø','Nov� Z�Mky':'Nové Zámky',
               'Nov� Sady':'Nové Sady','Boissy-Le-Ch�Tel':'Boissy-Le-Châtel',
               'Cun�O':'Cuneo','Praha 4 ? H�Je':'Prague','Sch�Llkrippen':'Schöllkrippen',
               'Ladomirov�':'Ladomirová','Si�Fok':'Siófok','Oranienbaum-W�Rlitz':'Oranienbaum-Wörlitz',
               'H�Nefoss':'Hønefoss','Altunizade/�?Skǭdar':'Üsküdar','����� / Sofia':'Sofia',
               'Baile �Tha Cliath':'Dublin','Nazar�':'Nazaré','B�':'Telemark',
               'Sant Cebri� De Vallalta (Barcelona)':'Barcelona','B�Rum':'Bærum',
               'K�Penhamn':'Copenhagen','F�Rde':'Førde','Br�Nn':'Brno','Byst�Ice':'Bystrice',
               'P�Dova':'Padua','Hadrec Kralov�':'Hradec Kralové','Charleville-M�Zi�Res':'Charleville-Méziéres',
               'Vysok� Tatry':'Vysoké Tatry','Hradec Kralov�':'Hradec Kralové',
               "Cala D�Or Mallorca":"Cala D'Or Mallorca",'Vr�Ble':'Vráble',
               'Karvin�':'Karviná',"S'Agar�, Girona":"S'Agaró",
               'Krom���':'Kroměříž','S�Fia':'Sofia','D�N Laoghaire, Dublin':'Dublin',
               '�Rbotty�N':'Örbottyán','�Ll?':'Gödöllö','Baile Chl�Ir':'Claregalway',
               'St��Varfj�R�Ur':'Stöðvarfjörður','Tr� L�':'Tralee','V�Rone':'Verona',
               'P�Rouse':'Perugia','Quartu Sant�Elena (Cagliari)':"Quartu Sant'Elena",
               'R�Ma':'Rome',"Saint Nicolas- Vall�E D'Aoste":"Saint Nicolas Vall'e D'Aoste",
               'Si�Na':'Siena','Via Roma, 94 � 90133 Palermo, Italy':'Palermo',
               'Zan� (Vicenza)':'Vicenza','B��Ardalur':'Búðardalur','�Quila':'Aquila',
               'Bir�Ai':'Birzai','Ei�I�K?S':'Eišiškės','Ei�I�Ki?, �Al�Inink?':'Eišiškės',
               'Ja�I?N? Mstl':'Jasiunai','Klaip�Da':'Klaipeda','Portoferraio- Isola D�Elba (Li)':'Portoferraio',
               'Pfitsch Eisacksta�E':'Pfitsch','Mod�Ne':'Modena','Mal�':'Malé',
               'Eppan An Der Weinstra�E':'Eppan An Der Weinstraße','Citt� Del Vaticano':'Vatican City',
               'Cefal�':'Cefalu','Agrate Brianza � Mb':'Agrate Brianza','Åsafj�R�Ur':'Ísafjörður',
               'Sau??Rkr�Kur':'Sauðárkrókur','Neskaupsta�Ur':'Neskaupstadur',
               'Kvenr�Ttindaf�Lag Åslands, T�Ng�Tu 14, 101 Reykjavik':'Reykjavik',
               '�Brah�Mhegy':'Ábrahámhegy','Tiran�-Shqip�Ri':'Tirana','Strasbourg�Cedex':'Strasbourg',
               'R�Mire - Montjoly':'Rémire-Montjoly','R�My':'Rémy','R�Union':'Réunion',
               'Saint D�Nis':'Saint Denis','Saint L�':'Saint-Lo','Saint-L�':'Saint-Lo',
               'P�Ronne':'Péronne','P�Rols':'Pérols','Pr� Saint Gervais':'Pré Saint Gervais',
               'M�Ribel':'Maribel','Moli�Res':'Moliéres','Mons�Gur':'Monségur',
               'M�Con':'Mâcon','Pl�My':'Plémy','?Rbotty�N':'Órbottyán','Zapre�I? Zagreb':'Zapresic',
               'Zapre�I?-':'Zapresic','D�R':'Dúr','Sz�Kesfeh�Rv?R':'Szekesfehervar',
               'H�Dmez�VÅs�Rhely':'Hódmezővásárhely','Pu?I�?A':'Pula','Mo�?Eni?Ka Draga':'Moscenicka Draga',
               'Maru�I?I':'Marusici','Tr�Voux':'Trévoux','V�Lizy':'Vélizy',
               '�Chirolles':'Échirolles','�Lancourt':'Élancourt','�Le-De-France':'Íle-De-France',
               '�Taples':'Etaples','�Vereux':'Évreux','Fa�Ana':'Fazana','K�Ajpeda':'Klaipeda',
               'O�Wiecim':'Oswiecim','Tel�Iai':'Telsiai','�En�Ur':'Sencur',
               '�Rnsk�Ldsvik':'Örnsköldsvik','�Rebr�':'Örebro','Kr�Ovsk� Chlmec':'Kralovsky Chlmec',
               'P�Chov':'Puchov','V�Ja':'Väja','M�Rrums':'Mörrums','R�Ttvik':'Rättvik',
               'Esc�Cia':'Edinburgh',
               }

placedict = {"Se331, Sweden":"Västerbotten, Sweden","Check The Pic In Urf For City, Spain":"Madrid, Spain",
         "0, Italy":"Rome, Italy","Paris Cedex 06, France":"Paris, France","Unknown, Sweden":"Stockholm, Sweden",
         "Leioa, Bilbao, San Sebastian And Vitoria, Spain":"Bilbao, Spain","Sceaux : (Paris), Troyes, Montpellier, France":"Montpellier, France",
         "-, Italy":"Rome, Italy", "SÅborg, Denmark":"Søborg, Denmark","Caen Cedex 5, France":"Caen, France",
         "Saint- Ouen, France":"Saint-Ouen, France","Don'T Know, Finland":"Helsinki, Finland",
         "Check The Pic In Urf For City, Finland":"Turku, Finland","Paris Cedex 05, France":"Paris, France",
         "Check The Pic In Urf For City, Denmark":"Copenhagen, Denmark","Check The Pic In Urf For City, Germany":"Hamburg, Germany",
         "Falun And BorlNge (Twin Campus), Sweden":"Falun, Sweden","Falun And Borlänge (Twin Campus), Sweden":"Borlänge, Sweden",
         "Odense, Kolding, Esbjerg, Sønderborg And Slagelse, Denmark":"Odense, Denmark",
         "SzKesfehRvR, Hungary":"Székesfehérvár, Hungary","WOcAwek, Poland":"Wloclawek, Poland",
         "Check The Pic In Urf For City, Belgium":"Brussels, Belgium","69373 Lyon Cedex 08, France":"Lyon, France",
         "Praha 5, Czech Republic":"Prague, Czech Republic", "Tr510, Turkey":"West Anatolia, Turkey",
         "D  Hamburg01, Germany":"Hamburg, Germany","GVle, Sweden":"Gävle, Sweden","Check The Pic In Urf For City, France":"Paris, France",
         "Odense, Kolding, Esbjerg, SNderborg And Slagelse, Denmark":"Kolding, Denmark","Klagenf, Austria":"Klagenfurt, Austria",
         "Rnak, Turkey":"Sirnak, Turkey","Dijon Cedex, Norway":"Dijon, France","Boedapest, Hungary":"Budapest, Hungary",
         "Xxxxx, Poland":"Warsaw, Poland","Rennes Cedex 7, France":"Rennes, France","Brüsszel, Belgium":"Brussels, Belgium",
         "You Have The Pic So You Know The City, Finland":"Joensuu, Finland","Check The Pic In Urf For City, Norway":"Oslo, Norway",
         "14195 Berlin, Germany":"Berlin, Germany","VCklabruck, Austria":"Vöcklabruck, Austria",
         "Check The Pic In Urf For City, Sweden":"Uppsala, Sweden","CracVia, Poland":"Krakow, Poland",
         "Uppsala, Umeå, Alnarp And Skara, Sweden":"Umeå, Sweden","-, Portugal":"Porto, Portugal",
         "VeszprM, Hungary":"Veszprem, Hungary","Check The Pic In Urf For City, Hungary":"Budapest, Hungary",
         "See Era Id, ":"","Undefined, France":"Brest, France","DonauwRth, Germany":"Donauwörth, Germany",
         "Dijon Cedex, Finland":"Dijon, France","Dijon Cedex, Sweden":"Dijon, France","SetBal, Portugal":"Setubal, Portugal",
         "Check The Pic In Urf For City, Austria":"Vienna, Austria","BrHl, Germany":"Brühl, Germany",
         "Es61, Spain":"Andalusia, Spain", "Irllimeric01, Ireland":"Limerick, Ireland",
         "Check The Pic In Urf For City, Turkey":"Ankara, Turkey","Check The Pic In Urf For City, Italy":"Milan, Italy",
         "Stoccolma, Sweden":"Stockholm, Sweden","Dresda, Germany":"Dresden, Germany",
         "F  Paris007, France":"Paris, France","SNderborg, Denmark":"Sønderborg, Denmark",
         "Irldublin01, Ireland":"Dublin, Ireland","Irlgalway01, Ireland":"Galway, Ireland",
         "GDLl, Hungary":"Gödöllö, Hungary","You Have The Pic So You Know The City, ":"",
         "F  Paris014, France":"Paris, France","Check The Pic In Urf For City, ":"",
         "Riga01, Latvia":"Riga, Latvia","Dortmund, Frankfurt, Hamburg, München, Köln, Germany":"Dortmund, Germany",
         "Check The Pic In Urf For City, Spain":"Madrid, Spain", "Ahinbey, Turkey":"Sahinbey, Turkey",
         "Akovec, Croatia":"Cakovec, Croatia","Enschede, Sweden":"Enskede, Sweden",
         "Varsavia, Poland":"Warsaw, Poland","Liubliana, Slovenia":"Ljublana, Slovenia",
         "Otros, Ireland":"Otterstown, Ireland","Checkurf, Spain":"Nerja, Spain","Google, Spain":"Madrid, Spain",
         "VarsVia, Poland":"Warsaw, Poland","Estocolmo, Sweden":"Stockholm, Sweden",
         "Vienna, Asutria":"Vienna, Austria","Viena, Austria":"Vienna, Austria","Enschede, Turkey":"Eskişehir‎, Turkey",
         "Kambja Vald, Tartumaa, Estonia":"Kambja, Estonia","HódmezVásárhely, Hungary":"Hódmezővásárhely, Hungary",
         "Lerissos, Greece":"Ierissos, Greece", "Ülenurme Vald, Tartumaa, Estonia":"Ülenurme, Estonia",
         "Checkurf, Turkey":"Şanlıurfa, Turkey","Checkurf, Hungary":"Budapest, Hungary",
         "Enschede, France":"Paris, France","Irlcork01, Ireland":"Cork, Ireland",
         "Desconocido, Italy":"Rome, Italy","Szekszd, Hungary":"Szekszard, Hungary",
         "Breslavia, Poland":"Warsaw, Poland","TNsberg, Norway":"Tønsberg, Norway",
         "Cadice, Spain":"Cadiz, Spain","Desconocido, Germany":"Essen, Germany",
         "Genua, Italy":"Genova, Italy","E  Valenci01, Spain":"Valencia, Spain",
         "Checkurf, Denmark":"Randers, Denmark", "Mnchen, Germany":"München, Germany",
         "Kaskelen, Kazakhstan":"Qaskelen, Kazakhstan","Otros, Portugal":"Porto, Portugal",
         "Rzym, Italy":"Rome, Italy", "Kgs Lyngby, Denmark":"Kongens Lyngby, Denmark",
         "Saint BarthLemy D'Anjou, France":"Saint Barthélemy D'Anjou, France",
         "DiyarbakR, Turkey":"Diyarbakır, Turkey", "Eskilstuna And Västerås (Twin Campus), Sweden":"Eskilstuna, Sweden",
         "Saint- Ouen, France":"Saint-Ouen, France", "See Era Id, United Kingdom":"Belfast, United Kingdom",
         "Milao, Italy":"Milan, Italy", "See Era Id, Czech Republic":"Prague, Czech Republic",
         "Bialyst, Poland":"Bialystok, Poland", "Arcavacata Di Rente (Cs), Italy":"Arcavacata, Italy",
         "Check The Pic In Urf For City, Portugal":"Braganca, Portugal","Marmolejo (Jaén), Spain":"Marmolejo, Spain",
         "La Haye, Netherlands":"The Hague, Netherlands", "Dijon Cedex, Portugal":"Dijon, France",
         "See Era Id, Austria":"Linz, Austria","Oslo, Norway, Norway":"Oslo, Norway",
         "Las Palmas, G.Canari, Spain":"Las Palmas, Spain","Dresda, Germany":"Dresden, Germany",
         "Markgroningen, Germany":"Markgröningen, Germany", "Check The Pic In Urf For City, Czech Republic":"Pardubice, Czech Republic",
         "Belgique, Belgium":"Bruges, Belgium", "Espoo (In Mailing Address Aalto), Finland":"Espoo, Finland",
         "SzekszRd, Hungary":"Szekszárd, Hungary","You Have The Pic So You Know The City, Denmark":"Herning, Denmark",
         "Carrigaline, Cork, Ireland":"Carrigaline, Ireland","Wolfenbuttel, Germany":"Wolfenbüttel, Germany",
         "Gdyinia, Poland":"Gdynia, Poland", "Mestoles-Madrid, Spain":"Mostoles, Spain",
         "Rychnov Nad KnNou, Czech Republic":"Rychnov nad Kněžnou, Czech Republic",
         "Pl22, Poland":"Śląskie, Poland","Paris 7, France":"Paris, France",
         "Oliveira De AzemIs, Portugal":"Oliveira de Azeméis, Portugal","Rzym, Italy":"Rome, Italy",
         "Stoccarda, Germany":"Stuttgart, Germany","Umea01, Sweden":"Umeå, Sweden",
         "Nepcity, Spain":"Barcelona, Spain", "Cs 40700 Grenoble 9, France":"Grenoble, France",
         "Dublin 7, Ireland":"Dublin, Ireland","Checkurf, Finland":"Rovaniemi, Finland",
         "Itf3, Italy":"Campania, Italy", "Praha07, Czech Republic":"Prague, Czech Republic",
         "Gandra-Prd, Portugal":"Gandra, Portugal", "75337 Paris Cedex 07, France":"Paris, France",
         "Lt-53361 Kauno R., Lithuania":"Kaunas, Lithuania", "De2, Germany":"Oberbayern, Germany",
         "Dsseldorf, Germany":"Düsseldorf, Germany", "Uk Bristol01, United Kingdom":"Bristol, United Kingdom",
         "Cp Groningen, Netherlands":"Groningen, Netherlands","Oth, Norway":"Tromsø, Norway",
         "Edimbourg, United Kingdom":"Edinburgh, United Kingdom","Gotemburgo, Sweden":"Gothenburg, Sweden",
         "I-00168 Roma, Italy":"Rome, Italy", "Irlmaynoot01, Ireland":"Maynooth, Ireland",
         "Landshu01, Germany":"Landshut, Germany","S-58183 Linkoping, Sweden":"Linkoping, Sweden",
         "Groning03, Netherlands":"Groningen, Netherlands", "Eberhard Karls Universitaet Tuebingen, Germany":"Tübingen, Germany",
         "GoleniW, Poland":"Goleniow, Poland", "Nepcity, Belgium":"Brussels, Belgium","Google, Turkey":"Göreme, Turkey",
         "S-104 01 Stockholm, Sweden":"Stockholm, Sweden","BBlingen, Germany":"Böblingen, Germany",
         "B  Bruxel04, Belgium":"Brussels, Belgium","Suchdol-Praha-Suchdol, Czech Republic":"Prague, Czech Republic",
         "Lisboa Codes, Portugal":"Lissabon, Portugal","Novedrate Co, Italy":"Novedrate, Italy",
         "16124 Genova, Italy":"Genoa, Italy","Francoforte, Germany":"Frankfurt, Germany",
         "Checkurf, Ireland":"Dublin, Ireland","Pt17, Portugal":"Algarve, Portugal",
         "Checkurf, Germany":"Berlin, Germany","Enschede, Finland":"Enontekiö, Finland",
         "Pl12, Poland":"Mazowieckie, Poland","Hu333, Hungary":"Csongrád-Csanád, Hungary",
         "03Ibor, Slovenia":"Maribor, Slovenia", "0, Ireland":"Dublin, Ireland",
         "Irldublin02, Ireland":"Dublin, Ireland", "Biberach An Der Riã, Germany":"Biberach an der Riß, Germany",
         "Lesparre MDoc Cedex, France":"Lesparre-Médoc, France", "Salonicco, Greece":"Thessaloniki, Greece",
         "Amburgo, Germany":"Hamburg, Germany", "Irldublin04, Ireland":"Dublin, Ireland",
         "Eská Lípa, Czech Republic":"Ceská Lípa, Czech Republic", "P Lisboa01, Portugal":"Lissabon, Portugal",
         "JRvenp, Finland":"Järvenpää, Finland","TRnitz, Austria":"Ternitz, Austria",
         "G  Thessal01, Greece":"Thessaloniki, Greece", "VNnS, Sweden":"Vännäs, Sweden",
         "Check The Pic In Urf For City, Lithuania":"Vilnius, Lithuania","L-9530 Wiltz, Luxembourg":"Wiltz, Luxembourg",
         "BYKcakmece Istanbul, Turkey":"Büyükçekmece, Turkey","Kerkyra, Korfu Sziget, Greece":"Corfu, Greece",
         "Checkurf, Sweden":"Stockholm, Sweden", "Odense, Kolding, Esbjerg, Sonderborg And Slagelse, Denmark":"Slagelse, Denmark",
         "SauRkrKur, Iceland":"Sauðárkrókur, Iceland", "75231 Paris Cedex 05, France":"Paris, France",
         "Undefined, Netherlands":'Amsterdam, Netherlands',"AngermNde, Germany":"Tangermünde, Germany",
         "BKScsaba, Hungary":"Békéscsaba, Hungary","Pl61, Poland":"Torun, Poland",
         "Si018, Slovenia":"Postjona, Slovenia","Desconocido, Netherlands":"Amsterdam, Netherlands",
         "10 000 Zagreb, Croatia":"Zagreb, Croatia","SarrebrCk, Germany":"Sarrebrück, Germany",
         "Checkurf, France":"Paris, France","Checkurf, Greece":"Athens, Greece","Checkurf, Poland":"Warsaw, Poland",
         "København C, Denmark":"Copenhagen, Denmark","VilleurbanneCedex, France":"Villeurbanne, France",
         "Nepcity, Portugal":"Lissabon, Portugal","Nepcity, Germany":"Berlin, Germany",
         "Zagabria, Croatia":"Zagreb, Croatia","Wiesbaden, Oestrich-Winkel, Germany":"Wiesbaden, Germany",
         "Otr, Austria":"Lienz, Austria", "Check The Pic In Urf For City, Bulgaria":"Sofia, Bulgaria",
         "Wilno, Lithuania":"Vilnius, Lithuania","Odense And Vejle, Denmark":"Vejle, Denmark",
         "Verona (Vr), Italy":"Verona, Italy", "75230 Paris Cedex 05, France":"Paris, France",
         "Nottingham Ng7 2Rd, United Kingdom":"Nottingham, United Kingdom","Mollet Del VallS, Spain":"Mollet Del Valles, Spain",
         "Riga, Lithuania":"Riga, Latvia","JPing, Sweden":"Köping, Sweden","Undefined, Belgium":"Mons, Belgium",
         "Itf6, Italy":"Cosenza, Italy","Dkzz, Denmark":"Skagen, Denmark","Iayes, Romania":"Iasi, Romania",
         "Be10, Belgium":"Brussels, Belgium","Es30, Spain":"Madrid, Spain","998597056, Spain":"Madrid, Spain",
         "95094 Cergy CDex, France":"Cergy, France","Xxxxx, Netherlands":"Rotterdam, Netherlands",
         "69288 Lyon Cedex 02, France":"Lyon, France","Es51, Spain":"Barcelona, Spain",
         "Prerov I, Mesto, Czech Republic":"Přerov I-Město, Czech Republic","BTera (Valencia), Spain":"Bétera, Spain",
         "999896856, Greece":"Athens, Greece","999995602, Italy":"Padova, Italy","D  Tubinge01, Germany":"Tübingen, Germany",
         "997179789, Hungary":"Budapest, Hungary","Mestoles, Spain":"Mostoles, Spain",
         "Uk London005, United Kingdom":"London, United Kingdom", "Madrid Y Reikiavik, Iceland":"Reykjavik, Iceland",
         "Edgbaston, Birmingham B5 7Sn, United Kingdom":"Birmingham, United Kingdom",
         "Cz-116 38  Praha I, Czech Republic":"Prague, Czech Republic","Athens, Zografou, Greece":"Athens, Greece",
         "Paris010, France":"Paris, France","Martorell (Barcelona), Spain":"Barcelona, Spain",
         "Irlcork, Ireland":"Cork, Ireland","-, Slovenia":"Bled, Slovenia",
         "Praha 11-Chodov, Czech Republic":"Prague, Czech Republic","Sezz, Sweden":"Malmö, Stockholm",
         "Balma Cedex, France":"Balma, France","Elverum01, Norway":"Elverum, Norway","See Urf, Poland":"Warsaw, Poland",
         "Otros, Lithuania":"Kaunas, Lithuania","Avignon, Cedex, France":"Avignon, France","949453170, France":"Lyon, France",
         "See Urf, United Kingdom":"Aberdeen, United Kingdom","8005, 139 Faro, Portugal":"Faro, Portugal",
         "Various, Spain":"Bilbao, Spain","Checkurf, Austria":"Innsbruck, Austria",
         "D  Potsdam01, Germany":"Potsdam, Germany","70833 Ostrava Poruba, Czech Republic":"Ostrava, Czech Republic",
         "56100 Pisa, Italy":"Pisa, Italy","Cz Praha09, Czech Republic":"Prague, Czech Republic",
         "0, Bulgaria":"Sofia, Bulgaria", "Ibenik, Croatia":"Šibenik, Croatia","St. Denis Cedex 09, France":"St. Denis, France",
         "Itf1, Italy":"Teramo, Italy","Pl63, Poland":"Starogardzki, Poland","D-10963 Berlin, Germany":"Berlin, Germany",
         "998164339, Turkey":"Istanbul, Turkey","999849423, Spain":"Jaén, Spain",
         "Hospitalet De Llobregat, Spain":"L'Hospitalet De Llobregat, Spain", "949496044, Bulgaria":"Sveta Gora, Bulgaria",
         "Checkurf, Italy":"Rome, Italy", "Enschede, Hungary":"Budapest, Hungary", "Enschede, Portugal":"Lissabon, Portugal",
         "999864846, Spain":"Valencia, Spain","Enschede, Norway":"Oslo, Norway", "Pt11, Portugal":"Douro, Portugal",
         "Kumes, Hungary":"Budapest, Hungary","VRpalota, Hungary":"Várpalota, Hungary",
         "Pl41, Poland":"Pilski, Poland", "999585583, Greece":"Athens, Greece", "75775 Paris Cedex 16, France":"Paris, France",
         "Kobenhagn, Denmark":"Copenhagen, Denmark", "999643492, Turkey":"Ankara, Istanbul",
         "Santiagodecompostela, Spain":"Santiago de Compostela, Spain","Irldublin, Ireland":"Dublin, Ireland",
         "75251 Paris Cedex 05, France":"Paris, France","Akwizgran, Germany":"Aachen, Germany",
         "D  Trier01, Germany":"Trier, Germany","Undefined, Greece":"Thessaloniki, Germany",
         "Surrey Tw20 0Ex, United Kingdom":"Surrey, United Kingdom","Nl Delft01, Netherlands":"Delft, Netherlands",
         "Trollhã¤Ttan, Sweden":"Trollhättan, Sweden", "Münchengladbach, Germany":"Mönchengladbach, Germany",
         "Vilnius, Litauen, Lithuania":"Vilnius, Lithuania","2520 Luxembourg, Luxembourg":"Luxembourg, Luxembourg",
         "EdArnhem, Belgium":"Arnhem, Belgium","Pl 00-927 Warszawa, Poland":"Warsaw, Poland",
         "Sztokholm, Sweden":"Stockholm, Sweden", "Herzogenerauch, Germany":"Herzogenaurach, Germany",
         "Linkopi01, Sweden":"Linköping, Sweden","Praha 8, Libe, Czech Republic":"Prague, Czech Republic",
         "Lappenraata, Finland":"Lappeenranta, Finland", " Cala'N Bosch, Spain":"Cala en Bosc, Spain",
         "HRning, Denmark":"Herning, Denmark","Cluj, Napoca, Romania":"Cluj-Napoca, Romania",
         "Jelenia GRa 5, Poland":"Jelenia Góra, Poland","Jandia, Fuerteventura, Spain":"Fuerteventura, Spain",
         "Sanningerberg, Luxembourg":"Senningerberg, Luxembourg","TRrega, Spain":"Tarrega, Spain",
         "Dijon Cedex, Estonia":"Tallinn, Estonia", "Lisboa109, Portugal":"Lissabon, Portugal",
         "Amsterd01, Netherlands":"Amsterdam, Netherlands","Ed Arnhem, Netherlands":"Arnhem, Netherlands",
         "Zurow Ot Fahren, Germany":"Zurow, Germany", "Dublin , Ireland":"Dublin, Ireland",
         "Oth, Lithuania":"Klaipeda, Lithuania", "Undefined, Germany":"Regensburg, Germany",
         "0, Croatia":"Split, Croatia", "Lv006, Latvia":"Riga, Latvia","Sk010, Slovakia":"Bratislava, Slovakia",
         "Tr100, Turkey":"Istanbul, Turkey","No051, Norway":"Hordaland, Norway","Praha, Prag, Czech Republic":"Prague, Czech Republic",
         "Kadyks, Spain":"Cadiz, Spain","Ejtun, Malta":"Żejtun, Malta", "Pamplona, Greece":"Pamplona, Spain",
         "Jùrpeland, Norway":"Jørpeland, Norway", "Check The Pic In Urf For City, Poland":"Warsaw, Poland",
         "Lingby, Denmark":"Kongens Lyngby, Denmark", "Angers Cedex 01, Hungary":"Budapest, Hungary",
         "Check The Pic In Urf For City, Croatia":"Dubrovnik, Croatia","Otros, Sweden":"Gothenburg, Sweden",
         "Desconocido, Belgium":"Brussels, Belgium","Eindhoven, Lithuania":"Eindhoven, Netherlands",
         "949261692, Germany":"Augsburg, Germany","E  Tenerif01, Spain":"Tenerife, Spain",
         "936847244, France":"Roubaix, France","Lt-44248 Kaunas, Lithuania":"Kaunas, Lithuania",
         "UnterschleiHeim, Germany":"Unterschleißheim, Germany","Koblenz And Landau, Germany":"Landau, Germany",
         "Nantes 3, France":"Nantes, France", "Nieuvennep, Netherlands":"Nieuw-Vennep, Netherlands",
         "Warszawa,, Poland":"Warsaw, Poland","HRnSand, Sweden":"Härnösand, Sweden",
         "Checkurf, Belgium":"Liege, Belgium", "Iauliai, Lithuania":"Šiauliai, Lithuania",
         "Algatocin (Malaga), Spain":"Malaga, Spain", "Dk Arhus01, Denmark":"Arhus, Denmark",
         "P  Coimbra01, Portugal":"Coimbra, Portugal","Villaviciosa De OdN, Spain":"Villaviciosa De Odon, Spain",
         "VRu, Estonia":"Võru, Estonia", "Vaxzo, Sweden":"Växjö, Sweden","Kajaanin, Finland":"Kajaani, Finland",
         "Alcuescar, Spain":"Alcuéscar, Spain","949283614, Germany":"Dortmund, Germany",
         "Monachium, Germany":"München, Germany","Desconocido, Portugal":"Lissabon, Portugal",
         "Irldublin27, Ireland":"Dublin, Ireland","75270 Paris Cedex 06, France":"Paris, France",
         "Oth, Cyprus":"Agia Napa, Cyprus","D-10117 Berlin, Germany":"Berlin, Germany",
         "Kempten02, German":"Kempten, Germany", "20126 Milano, Italy":"Milano, Italy",
         "Härnosand, Östersund, Sundsvall, Sweden":"Härnosand, Sweden","Kuanas, Lithuania":"Kaunas, Lithuania",
         "Ubisoft Entertainment Sweden Ab Box 4297 203 14 Ma, Sweden":"Malmö, Sweden",
         "Unknown, Estonia":"Tallinn, Estonia", "CalaN Bosch Cuitadella Menorca, Spain":"Cala en Bosc, Spain",
         "Reykjavik, Ireland":"Reykjavik, Iceland", "RZekne, Latvia":"Rēzekne, Latvia",
         "Valenzcia, Spain":"Valencia, Spain", "Check The Pic In Urf For City, Latvia":"Rezekne, Latvia",
         "Irldublin44, Ireland":"Dublin, Ireland", "Otr, Denmark":"Copenhagen, Denmark",
         "Norimberga, Germany":"Nürnberg, Germany", "3500 Hasselt, Belgium":"Hasselt, Belgium",
         "Brigh And Hove, United Kingdom":"Brighton And Hove, United Kingdom","Spånga Stockholm, Sweden":"Stockholm, Sweden",
         "PDaste Village, Muhu Parish, Estonia":"Pädaste, Estonia", "Poland, Poland":"Warsaw, Poland",
         "Vastera01, Sweden":"Västerås, Sweden", "69007 Lyon Cedex 07, France":"Lyon, France",
         "998076748, Turkey":"Istanbul, Turkey", "Kb Enschede, Netherlands":"Enschede, Netherlands",
         "Eindhoven, Denmark":"Copenhagen, Denmark","Otros, Bulgaria":"Sofia, Bulgaria",
         "28199 Bremen, Germany":"Bremen, Germany","Klagenfurt Am WRthersee, Austria":"Klagenfurt, Austria",
         "University College South(Dk), Denmark":"Kolding, Denmark","RJiena, Latvia":"Rūjiena, Latvia",
         "Check The Pic In Urf For City, Romania":"Bucharest, Romania","KPavogur, Iceland":"Kópavogur, Iceland",
         "OWiCim, Poland":"Oświęcim, Poland","Praha 2, Nové Mesto, Czech Republic":"Prague, Czech Republic",
         "Grenoble Cedex9, France":"Grenoble, France","SDertLje, Sweden":"Södertälje, Sweden",
         "Rahovec, Kosovo * UN resolution":"Rahovec, Kosovo","Orekhovo-Zuevo, Russian Federation":"Orekhovo-Zujevo, Russian Federation",
         "Nijimengen, Netherlands":"Nijmengen, Netherlands","Moscu, Russian Federation":"Moscow, Russian Federation",
         "Nepcity, Finland":"Helsinki, Finland","Ystese, Norway":"Øystese, Norway",
         "Crete, Hersonissos, Greece":"Chersónisos, Greece","999650088, Sweden":"Örebro, Sweden",
         "UnterfHring, Germany":"Unterföhring, Germany","Paris, Jouy-En-Josas, France":"Paris, France",
         "STubal, Portugal":"Setubal, Portugal","Maribor01, Slovakia":"Maribor, Slovakia",
         "Irlkildare04, Ireland":"Kildare, Ireland", "E  Logrono01, Spain":"Logroño, Spain",
         "Zm Utrecht, Netherlands":"Utrecht, Netherlands", "Datriina, Finland":"Kotka, Finland",
         "Kortrijk, Bulgaria":"Kortrijk, Belgium","Ochoz U Brna, Czech Republic":"Brno, Czech Republic",
         "Nijmegen, Hungary":"Nijmegen, Netherlands", "IbNeTi, Romania":"Ibănești, Romania",
         "Xxxxx, Lithuania":"Kaunas, Lithuania","Undefined, Italy":"Rome, Italy",
         "BeyazT, Fatih, Istanbul, Turkey":"Istanbul, Turkey", "Kufstein, Poland":"Kufstein, Austria",
         "ValaSké MeziÍÍ, Czech Republic":"Valasske Mezirici, Czech Republic",
         "Walencja, Spain":"Valencia, Spain","MagyaralmS, Hungary":"Magyaralmás, Hungary",
         "Reykjavã­K, Iceland":"Reykjavik, Iceland","Tralee, Co. Kerry, Ireland":"Tralee, Ireland",
         "BKara, Malta":"Birkirkara, Malta","AlIninkai, Lithuania":"Alšininkai, Lithuania",
         "Provodov, Onov, Czech Republic":"Provodov-Šonov, Czech Republic", "Eidnhover, Norway":"Oslo, Norway",
         "WeLing, Germany":"Weßling, Germany", "Cascatalà, Spain":"Cas Català, Spain","Spopron, Hungary":"Sopron, Hungary",
         "Nepcity, Denmark":"Copenhagen, Denmark","Nepcity, Turkey":"Ankara, Turkey","Lisboa107, Portugal":"Lissabon, Portugal",
         "Bercelona, Spain":"Barcelona, Spain","Elverum02, Norway":"Elverum, Norway","MaEikiai, Lithuania":"Mažeikiai, Lithuania",
         "Peterborough, Spain":"Peterborough, United Kingdom","FRstenwalde, Germany":"Fürstenwalde, Germany",
         "Nottingham, Uk, United Kingdom":"Nottingham, United Kingdom","Dijon Cedex, Lithuania":"Kaunas, Lithuania",
         "Riga (Lv), Latvia":"Riga, Latvia", "Enschede, Greece":"Thessaloniki, Greece",
         "Rkelljunga, Sweden":"Örkelljunga, Sweden", "943245461, Spain":"Valencia, Spain",
         "949083794, Denmark":"Copenhagen, Denmark", "La Roda (Albacete), Spain":"La Roda, Spain",
         "949512340, Denmark":"Copenhagen, Denmark", "Checkurf, Norway":"Oslo, Norway", "D Berlin13, Germany":"Berlin, Germany",
         "Bortonigla, Croatia":"Brtonigla, Croatia","HRnum, Germany":"Hörnum, Germany",
         "Merseyside  Liverpool, United Kingdom":"Liverpool, United Kingdom","Exeter, Devon, Ex4 4Rn., United Kingdom":"Exeter, United Kingdom",
         "I  Siena01, Italy":"Siena, Italy", "Vilnius, Romania":"Vilnius, Lithuania",
         "66860 Perpignan Cedex, France":"Perpignan, France", "Paris379, France":"Paris, France",
         "49003 Angers Cedex 01, France":"Angers, France","Toulouse CDex 9, France":"Toulouse, France",
         "Village Of Sheinovo,  Obstina Kazanlak, Bulgaria":"Sheynovo, Bulgaria",
         "Pxl, Belgium":"Hasselt, Belgium","Catalunya, Spain":"Barcelona, Spain",
         "Lappeeranta, Finland":"Lappeenranta, Finland","Vysoké Mýto, Czech Republic":"Hradec, Czech Republic",
         "D31141 Hildesheim, Germany":"Hildesheim, Germany","Xxxxx, France":"Paris, France",
         "Xxxxx, Slovakia":"Bratislava, Slovakia", "4000 Liege, Belgium":"Liege, Belgium",
         "Georg-August-Universitaet Goettingen Stiftung Oeffentlichen Rechts, Germany":"Göttingen, Germany",
         "Ie021, Ireland":"Dublin, Ireland","Ro21, Romania":"Vaslui, Romania",
         "949316982, Belgium":"Antwerpen, Belgium","997963646, Germany":"Brandenburg, Germany",
         "949657452, Germany":"Pforzheim, Germany","Enschede, Estonia":"Tartu, Estonia",
         "999986096, Belgium":"Ghent, Belgium", "999864070, France":"Aubiere, France",
         "At13, Austria":"Vienna, Austria","Hr041, Croatia":"Zagreb, Croatia",
         "31058 Toulouse Cedex 9, France":"Tolouse, France","Lt002, Lithuania":"Kaunas, Lithuania",
         "Xxxxx, Portugal":"Lissabon, Portugal","Ro11, Romania":"Cluj-Napoca, Romania",
         "JLich, Germany":"Jülich, Germany","Nepcity, Norway":"Oslo, Norway",
         "Mieziskiai, Panevezys Region, Lithuania":"Mieziskiai, Lithuania",
         "NagyvZsony, Hungary":"Nagyvázsony, Hungary", "QuTigny, France":"Quetigny, France",
         "Varsseveld, Germany":"Varsseveld, Netherlands", "Sliema, Greece":"Sliema, Malta",
         "Rommetv01, Norway":"Haugesund, Norway","Arhus01, Denmark":"Arhus, Denmark",
         "Vroklave, Poland":"Wroclaw, Poland", "Tampere, Ireland":"Tampere, Finland",
         "BGles, France":"Begles, France","Puntagords, Spain":"Puntagorda, Spain",
         "Taxbiex, Malta":"Ta' Xbiex, Malta","C0Penhagen S., Denmark":"Copenhagen, Denmark",
         "Trausnick, Germany":"Krausnick, Germany", "Athine04, Greece":"Athens, Greece",
         "Seinajoki, Ilmajoki, Jurva, Kauhajoki, Kauhava, Ahtori, Finland":"Seinäjoki, Finland",
         "Musninkai, Irvint R., Lithuania":"Musninkai, Lithuania","Paguera,  Calvia,  Mallorca, Spain":"Mallorca, Spain",
         "Valenciennes, Spain":"Valencia, Spain", "Obertsdorf, Germany":"Oberstdorf, Germany",
         "Kobenham, Denmark":"Copenhagen, Denmark", "Dijoin, France":"Dijon, France",
         "Qaqortoq, Denmark":"Qaqortoq, Greenland","Lstykke, Denmark":"Ølstykke, Denmark",
         "Ryga, Latvia":"Riga, Latvia","Wienna, Austria":"Vienna, Austria",
         "Aaaaaa, Germany":"Aachen, Germany","Aaaaaa, Portugal":"Algarve, Portugal",
         "Alcininkai, Lithuania":"Salcininkai, Lithuania","Provodov-Onov, Czech Republic":"Provodov-Šonov, Czech Republic",
         "Check The Pic In Urf For City, The Republic of North Macedonia":"Skopje, North Macedonia",
         "Irlgalway, Ireland":"Galway, Ireland","Kbenhavn, Denmark":"Copenhagen, Denmark",
         "Västerås And Eskilstuna (Twin Campus), Sweden":"Västerås, Sweden",
         "PetrAlka, Slovakia":"Petržalka, Slovakia","PieksMKi, Finland":"Pieksämäki, Finland",
         "Greifswald-Insel Riems, Germany":"Riems, Germany","Pophos, Cyprus":"Pafos, Cyprus",
         "Märjamaa Vald, Raplamaa, Estonia":"Märjamaa, Estonia","HLo, Sweden":"Hölö, Sweden",
         "Ksendal, Norway":"Øksendal, Norway","Luxlux-Vil01, Luxembourg":"Luxembourg´, Luxembourg",
         "Tingsryrd, Sweden":"Tingsryd, Sweden","Juvaskyla, Finland":"Jyväskylä, Finland",
         "Joensuu, Kuopio, Savonlinna, Finland":"Joensuu, Finland","Tãœbingen, Germany":"Tübingen, Germany",
         "Βαρκελωνη, Spain":"Barcelona, Spain","Boedapest, Hungary":"Budapest, Hungary",
         "Παρισι, France":"Paris, France","Βρυξελλες, Belgium":"Βρυξελλες, Belgium",
         "Βερολινο, Germany":"Berlin, Germany","Fundacion Universitaria San Antonio, Spain":"Murcia, Spain",
         "Clujnap, Romania":"Cluj-Napoca, Romania","Oulun Ammattikorkeakoulu Oy, Finland":"Oulu, Finland",
         "Κωνσταντινουπολη, Turkey":"Istanbul, Turkey","Bellaterra (Cerdanyola Del VallÅs), Spain":"Cerdanyola Del Vallés, Spain",
         "STurkurg, Denmark":"Copenhagen, Denmark", "Κοπεγχαγη, Denmark":"Copenhagen, Denmark",
         "Βουδαπεστη, Hungary":"Budapest, Hungary","Μαλαγα, Spain":"Malaga, Spain",
         "Fundacio Universitaria Balmes, Spain":"Vic, Spain","Fundacion Universidad Loyola Andalucia, Spain":"Cordoba, Spain",
         "Βερολίνο, Germany":"Berlin, Germany","Donauwürth, Germany":"Donauwörth, Germany","Λισαβονα, Portugal":"Lissabon, Portugal",
         "Universidad Del Pais Vasco,  Euskal Herriko Unibertsitatea, Spain":"Leioa, Spain",
         "Dortmund, Frankfurt, Hamburg, Munich, Köln, Germany":"Dortmund, Germany",
         "Γραναδα, Spain":"Granada, Spain","Βαρκελώνη, Spain":"Barcelona, Spain",
         "Ρωμη, Italy":"Rome, Italy","Biberach An Der Riãÿ, Germany":"Biberach An Der Riß, Germany",
         "Ρεν, France":"Rennes, France","Παφος, Cyprus":"Páfos, Cyprus","Ταμπερε, Finland":"Tampere, Finland",
         "Geilo. Viken County, Norway":"Geilo, Norway","Αμστερνταμ, Netherlands":"Amsterdam, Netherlands",
         "Ülenurme vald, Tartumaa, Estonia":"Ülenurme, Estonia","Μοναχο, Germany":"München, Germany",
         "Στοκχολμη, Sweden":"Stockholm, Sweden","Estrasburgo, France":"Strasbourg, France",
         "Παβια, Italy":"Pavia, Italy","Valašské Meziříčí, Czech Republic":"Valasske Mezirici, Czech Republic",
         "Dijon , Sweden":"Gothenburg, Sweden","Dijon , Finland":"Helsinki, Finland",
         "Αλμερια, Spain":"Almeria, Spain", "Fundacio Tecnocampus Mataro-Maresme, Spain":"Mataro, Spain",
         "Khimki Moskva, Russian Federation":"Khimki, Russia","Φρανκφουρτη, Germany":"Frankfurt am Main, Germany",
         "Ebc Euro-Business-College Gmbh, Germany":"Hamburg, Germany",
         "Fachhochschulstudiengänge Betriebs-Und Forschungseinrichtungen Der Wiener Wirtschaft, Austria":"Vienna, Austria",
         "Βιέννη, Austria":"Vienna, Austria","Αχεν, Germany":"Aachen, Germany",
         "Βασα, Finland":"Vaasa, Finland","Ucl Erhvervsakademi & Professionshojskole Si, Denmark":"Odense, Denmark",
         "E10209482, Belgium":"Leuven, Belgium","Αμβούργο, Germany":"Hamburg, Germany",
         "Βαρσοβια, Poland":"Warsaw, Poland","Εσεν, Germany":"Essen, Germany","Δουβλινο, Ireland":"Dublin, Ireland",
         "Μιλανο, Italy":"Μilan, Italy","Σεβιλλη, Spain":"Sevilla, Spain","Βαλενθια, Spain":"Valencia, Spain",
         "Βαρσωβια, Poland":"Warsaw, Poland", "Fachhochschule Technikum Wien, Austria":"Vienna, Austria",
         "Λισαβωνα, Portugal":"Lissabon, Portugal","Cerdanyola Del VallÅs, Barcelona, Spain":"Cerdanyola Del Vallés, Spain",
         "Ensilis, Educacao E Formacao, Unipessoal Lda, Portugal":"Lissabon, Portugal",
         "E10209131, Spain":"Madrid, Spain","Zapadoceska Univerzita V Plzni, Czech Republic":"Plzen, Czech Republic",
         "Metropolitni Univerzita Praha Ops, Czech Republic":"Strasnice, Czech Republic",
         "Sczecin, Poland":"Szczecin, Poland","165 21 Prague 6, Suchdol, Czech Republic":"Prague, Czech Republic",
         "Κολωνια, Germany":"Köln, Germany","Alma Mater Studiorum, Universita Di Bologna, Italy":"Bologna, Italy",
         "Λςυκωσία, Cyprus":"Nikosia, Cyprus","Santayi, Spain":"Santanyi, Spain",
         "00-968 Warszawa 45, Poland":"Warsaw, Poland","Mãœnchen, Germany":"Munich, Germany",
         "Vilniaus Dizaino Kolegija, Lithuania":"Vilnius, Lithuania",
         "University Of Jyvďż˝Skylďż˝, Finland":"Jyväskylä, Finland",
         "Fhw Fachhochschul-Studiengänge Betriebs- Und Forschungseinrichtungen Der Wiener Wirtschaft Gmbh, Austria":"Vienna, Austria",
         "Ριγα, Latvia":"Riga, Latvia","Παρίσι, France":"Paris, France",
         "E10208943, Spain":"Bilbao, Spain","E10209394, Netherlands":"Eindhoven, Netherlands",
         "E10209112, Italy":"Venice, Italy","Libera Universita Maria Ss. Assunta Di Roma, Italy":"Rome, Italy",
         "Saalfeden, Austria":"Saalfelden, Austria","Provodov, Šonov, Czech Republic":"Provodov-Šonov, Czech Republic",
         "Veselí Nad Moravou, Czech Republic":"Veseli Nad Moravou, Czech Republic",
         "Κυπρος, Cyprus":"Cyprus, Cyprus","Buxelles, Belgium":"Brussels, Belgium","Νιτρα, Slovakia":"Nitra, Slovakia",
         "Přerov I, Město, Czech Republic":"Prerov, Czech Republic","Βουκουρεστι, Romania":"Bucharest, Romania",
         "Fh-Campus Wien, Verein Zur Forderung Des Fachhochschul-, Entwicklungs- Und Forschungszentrums Im Suden Wiens, Austria":"Vienna, Austria",
         "Drezno, Germany":"Dresden, Germany", "Dornbirn, Greece":"Marousi, Greece",
         "Mci Management Center Innsbruck Internationale Hochschule Gmbh, Austria":"Innsbruck, Austria",
         "Kodolanyi Janos Foiskola, Hungary":"Budapest, Hungary","Aindhofen, Netherlands":"Eindhoven, Netherlands",
         "Κοπενχαγη, Denmark":"Copenhagen, Denmark", "16628 Prague 6, Czech Republic":"Prague, Czech Republic",
         "Αμβουργο, Germany":"Hamburg, Germany","Lublin, Spain":"Malaga, Spain",
         "Τορινο, Italy":"Torino, Italy","Σοφια, Bulgaria":"Sofia, Bulgaria","Munichgladbach, Germany":"Mönchengladbach, Germany",
         "E10208971, Italy":"Milan, Italy","E10208601, Spain":"Vic, Spain","S’Gravenhage, Netherlands":"The Hague, Netherlands",
         "Skinnskateberg, Sweden":"Skinnskatteberg, Sweden","Datriina, Finland":"Kotka, Finland",
         "Turunyliopisto, Finland":"Turku, Finland","Vitenberga, Germany":"Wittenberg, Germany",
         "Ουτρεχτη, Netherlands":"Utrecht, Netherlands","Ντυσσελντορφ, Germany":"Düsseldorf, Germany",
         "Μαινζ, Germany":"Mainz, Germany","Γανδη, Belgium":"Ghent, Belgium","Λιεγη, Belgium":"Liege, Belgium",
         "Masarykova Univerzita, Czech Republic":"Brno, Czech Republic","Mechelen, Norway":"Mechelen, Belgium",
         "Stichting Christelijke Hogeschool Windesheim, Netherlands":"Zwolle, Netherlands",
         "E10209385, Spain":"Barcelona, Spain","Varşova, Poland":"Warsaw, Poland","Varšava, Poland":"Warsaw, Poland",
         "Fachhochschule Vorarlberg Gmbh, Austria":"Dornbirn, Austria","E10171437, France":"Talence, France",
         "E10107269, France":"Angers, France","E10186156, Austria":"Puch Bei Hallein, Austria",
         "E10209369, Norway":"Bergen, Norway","E10208856, Spain":"Barcelona, Spain","Dimitriskiu K. Zarasu Rajonas, Lithuania":"Zarasai, Lithuania"}

# dictionary to get correct address for the most common ones
org_add = {'Panteio Panepistimio Koinonikon Kaipolitikon Epistimon':'Panteion University',
           'Panepistimio Dytikis Attikis':'University of West Attica',
           'Technologiko Ekpedeftiko Idryma Thessalias':'Technological Educational Institute of Thessaly',
           'Technologiko Ekpaideftiko Idryma Athinas':'Technological Educational Institute of Athens',
           'Technologiko Ekpedeftiko Idryma Ipirou':'Technological Educational Institute of Epirus',
           'Harokopio University':'Athens',
           'Technologiko Ekpedeftiko Idrima Stereas Elladas':'Technological Educational Institute of Central Greece',
           'Technologiko Ekpedeftiko Idrima Stereas Ellada':'Technological Educational Institute of Central Greece',
           'Anotato Ekpaideytiko Idrima Peiraia Technologikoy Tomea':'Pireas',
           'Anotati Scholi Pedagogikis & Technologikis Ekpedefsis':'Athens',
           'Technologiko Ekpaideftiko Idryma Kentrikis Makedonias':'Thessaloniki',
           'Diethnes Panepistimio Ellados':'International Hellenic University',
           'Technical University Of Crete':'Chania',
           'Sdruzhenie "Blyan Za Romantika, Cvetya I Kosmos"':'Sliven',
           'Uchilishno Nastoiatelstvo Profesionalna Gimnazia Po Tehnika I Obleklo "Docho Mihaylov"':'Tervel',
           'Ikos Pronias Lefkadas':'Lefkadas',
           'Agricultural University Of Athens':'Athens',
           'European Association Of Folklore Festivals - Eaff':'Veliko Tarnovo',
           'Sdruzenie Za Makedonsko-Balgarsko Prijatelstvo':'Bitola',
           'Profesionalna Gimnazia Po Agrarni Tehnologii "Tzanko Tzerkovski"':'Pavlikeni',
           'Panteio Panepistimio Koinonikon Kai Politikon Epistimon':'Panteion University',
           'As Cyprus College Limited':'Nicosia',
           'Fire Theatre-Art-Culture Foundation':'Sofia', 'Latvijas Universitate':'University of Latvia',
           'University Of Piraeus Research Center':'Piraeus', 'Action Art': 'Pireus',
           'Centro De Estudios Bizantinos, Neogriegos Y Chipriotas':'Grenada',
           'Univerzita Karlova':'Prague', 'Kinoniki Sineteristiki Epihirisi':'Larissa',
           'Istanbul Bilgi Universitesi':'Istanbul', 'Embassy Of Greece In Madrid':'Madrid',
           'Inspiration':'Pyce','Universitat Fur Musik Und Darstellende Kunst Wien':'Vienna',
           'Ethniki Scholi Dimosias Ygeias':'Athens', '1St Vocational High School Of Aigaleo':'Aigaleo',
           'Cyta':'Nicosia','Akademie Muzickych Umeni V Praze':'Prague',
           'Rum Cemaat Vakiflari Destekleme Derne??':'Istanbul',
           'Corporation For Succor And Care Of Elderly And Disabled-Frodizo':'Patras',
           'Foodallergens Lab':'Livadia','Fundacion Universidad San Jorge':'Zaragoza',
           'Technologiko Panepistimio Kyprou':'Limassol', 'Ks Socratous Ltd':'Paphos',
           'Epw Europe Private Wealth Limited':'Limassol','Rheinisch-Westfaelische Technische Hochschule Aachen':'Aachen',
           'Centre D?Osteopatia I Fisioterapia Isouios':'Bilbao',
           'Pontificia Universidad Catolica De Chile':'Santiago',
           'Spyridon Konstantis "Vistonia-Korfu.De':'Berlin', 'Julius-Maximilians Universitaet Wuerzburg':'Wurzburg',
           'My Language Skills':'Valencia','Panepistimio Kyprou*':'Nicosia',
           'University Of La Laguna':'San Cristóbal La Laguna',
           'Centro De Estudios Byzantinos, Neogriegos Y Cypriotas':'Grenada',
           'Kinder Barcelona-Espai Infantil I Familiar':'Barcelona',
           'Anotato Technologiko Ekpedeytiko Idryma Ionion Nison':'Technological Educational Institute of the Ionian'
           }

# symbol dictionary
sym_dict = {' - ':', ',
            ' / ':', ',
            '/':', ',
            ' | ':', '}

# read pickle in
df = pd.read_pickle("/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/Erasmus_mobilities_2014-2022_combined.pkl")

# problem list
prob_cols = ['Sending Country', 'Sending City', 'Sending Organization',
             'Receiving Country','Receiving City', 'Receiving Organization']
probs = []

# list of placenames to switch for institution names
problist = ['Google','CheckURF','Check the PIC in URF For City', '?', '??', '-',
            'Desconocido', 'desconocido', 'DESCONOCIDO', 'XXXXX', 'xxxxx', 'Undefined',
            'Unknown','See Era Id', 'Enschede', 'Nepcity', 'Dkzz', 'Otros', 'Oth']

# read list of Erasmus HEIs
heis = pd.read_excel("/home/tuomvais/GIS/MOBI-TWIN/Erasmus/erasmus_HEIS_2021-2027.xlsx",
                     sheet_name='Accedited HEIs')

# drop nas from HEI
heis = heis.dropna(thresh=4)

# make names use title case
heis['Organisation Name'] = heis['Organisation Name'].apply(lambda x: x.title())

# set as integer
heis['PIC'] = heis['PIC'].astype(int)

# get address column
heis['address'] = heis['Street'] +', ' + heis['City'] + ', ' + heis['Country']

# generate dictionaries
picdict = heis.set_index('PIC')['address'].to_dict()
oiddict = heis.set_index('OID')['address'].to_dict()
namedict = heis.set_index('Organisation Name')['address'].to_dict()

# checking if organization has known address in HEI database
print('[INFO] - Getting addresses for institutions...')
for i, row in df.iterrows():
    
    # try to add adress if there is a match with PIC identifier
    try:
        df.at[i, 'sending_org_address'] = picdict[row['Sending Organization']]
    except:
        pass
    
    # try to add adress if there is a match with OID identifier
    try:
        df.at[i, 'sending_org_address'] = oiddict[row['Sending Organization']]
    except:
        pass
    
    # try to add adress if there is a match with name of organisation
    try:
        df.at[i, 'sending_org_address'] = namedict[row['Sending Organization'].title()]
    except:
        pass
    
    # try to add adress if there is a match with PIC identifier
    try:
        df.at[i, 'receiving_org_address'] = picdict[row['Receiving Organization']]
    except:
        pass
    
    # try to add adress if there is a match with OID identifier
    try:
        df.at[i, 'receiving_org_address'] = oiddict[row['Receiving Organization']]
    except:
        pass
    
    # try to add adress if there is a match with name of organisation
    try:
        df.at[i, 'receiving_org_address'] = namedict[row['Receiving Organization'].title()]
    except:
        pass

# release memory by deleting dictionaries
del namedict, oiddict, picdict

# counters for problems
probsend = []
probrece = []

# check if sending or receiving city is "???" and replace with organization
print('[INFO] - Fixing problematic city names with institution names...')
for i, row in df.iterrows():
    
    # force values to string
    row['Sending City'] = str(row['Sending City'])
    row['Receiving City'] = str(row['Receiving City'])
    
    # check for question marks in sending
    if ('???' in row['Sending City']) or (row['Sending City'].title() in problist):
        probs.append(row[prob_cols])
        probsend.append(row)
        try:
            df.at[i, 'Sending City'] = org_add[row['Sending Organization'].title()]
        except:
            df.at[i, 'Sending City'] = row['Sending Organization'].title()
    
    
    # check for question marks in receiving city
    if ('???' in row['Receiving City']) or (row['Receiving City'].title() in problist):
        probs.append(row[prob_cols])
        probrece.append(row)
        try:
            df.at[i, 'Receiving City'] = org_add[row['Receiving Organization'].title()]
        except:
            df.at[i, 'Receiving City'] = row['Receiving Organization'].title()

# Harmonize city name capitalization
df['Sending City'] = df['Sending City'].apply(lambda x: str(x).title())
df['Receiving City'] = df['Receiving City'].apply(lambda x: str(x).title())

# replace the weird names
for old, new in umlaut_dict.items():
    
    # replace
    df['Sending City'] = df['Sending City'].str.replace(old, new, regex=False)
    df['Receiving City'] = df['Receiving City'].str.replace(old, new, regex=False)
    
# fix weird symbol use
for old, new in sym_dict.items():
    # replace
    df['Sending City'] = df['Sending City'].str.replace(old, new, regex=False)
    df['Receiving City'] = df['Receiving City'].str.replace(old, new, regex=False)

# Clean country
print('[INFO] - Cleaning up columns...')
df['o_country'] = df['Sending Country'].apply(lambda x: x.split(' - ')[1])
df['d_country'] = df['Receiving Country'].apply(lambda x: x.split(' - ')[1])

# remove all numbers
#df['Sending City'] = df['Sending City'].astype(str).str.replace(r'\d+', '', regex=True)
#df['Receiving City'] = df['Receiving City'].astype(str).str.replace(r'\d+', '', regex=True)

# strip leading and trailing whitespace
df['Sending City'] = df['Sending City'].replace(r"^ +| +$", r"", regex=True)
df['Receiving City'] = df['Receiving City'].replace(r"^ +| +$", r"", regex=True)

# Get a geocodable location
df['origin'] = df['Sending City'] + ', ' + df['o_country']
df['destination'] = df['Receiving City'] + ', ' + df['d_country']

# replace origins and destinations with the actual address for those origins and destinations that have it
for i, row in df.iterrows():
    
    # replace origin with accurate address if it is available
    if pd.isna(row['sending_org_address']) == False:
        
        # replace origin
        df.at[i, 'origin'] = row['sending_org_address']
    else:
        pass
    
    # check if destination has accurate address
    if pd.isna(row['receiving_org_address']) == False:
        
        # replace destination
        df.at[i, 'destination'] = row['receiving_org_address']
    else:
        pass

# loop over data
for i, row in df.iterrows():
    
    # drop remaining question marks
    df.at[i, 'origin'] = row['origin'].replace('?','')
    df.at[i, 'destination'] = row['destination'].replace('?','')
    
    # drop placenames with "Cedex" as it refers to french nomenclature for postal code area
    df.at[i, 'origin'] = row['origin'].replace('Cedex','')
    df.at[i, 'destination'] = row['destination'].replace('Cedex','')
    
    # replace some place names with geocodable place names
    try:
        df.at[i, 'origin'] = placedict[row['origin']]
    except:
        pass
    try:
        df.at[i, 'destination'] = placedict[row['destination']]
    except:
        pass

# save dataframe so geocoded locations can be eventually connected
print('[INFO] - Saving file...')
df.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/erasmus_combined_2014-2022_pre-geocoding.pkl')

# get unique origins and destinations
origins = df['origin'].value_counts().reset_index()
destinations = df['destination'].value_counts().reset_index()

# rename
destinations = destinations.rename(columns={'destination':'origin'})

# append
places = pd.concat([origins, destinations], ignore_index=True)

# group by and sum
places = places.groupby(['origin'])['count'].sum().reset_index().sort_values(by=['count'], ascending=False).reset_index(drop=True)

# drop duplicates
places = places.drop_duplicates(subset='origin')

# add to location list
loclist = []
loclist.append(places)

# concatenate location list to a proper dataframe
locations = pd.concat(loclist, ignore_index=True)
probs = pd.concat(probs, ignore_index=True)
print('[INFO] - Gathering locations is done!')

# sort by counts
locations = locations.sort_values(['count'], ascending=False)

# drop duplicates
locations = locations.drop_duplicates(subset=['origin']).reset_index(drop=True)

# save locations
locations.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/pickle/erasmus_2014-2022_HEIs_pre-geocoded_locations_only.pkl')
locations.to_csv('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/pickle/erasmus_2014-2022_HEIs_pre-geocoded_locations_only.csv',
                 encoding='utf-8', sep=';')

# initialize geocoder
geolocator = Photon(user_agent='FINAL_SET_V1')

# set up rate limiter
geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# get initial value for iterations
n_iter = 1
print('[INFO] - Starting to geocode...')

# keep tabs on unsuccesfull geocodes
unsuc = []

# geocode
for i, row in locations.iterrows():
    if n_iter != 20:
        
        # geocode location
        geocoded = geocoder(row['origin'], timeout=120)
        
        try:            
            # get geocoded address
            locations.at[i, 'gc_address'] = geocoded.address
            
            # save latitude and longitude
            locations.at[i, 'y'] = geocoded.latitude
            locations.at[i, 'x'] = geocoded.longitude
            
            #update
            n_iter += 1
        except:
            
            # append list
            unsuc.append(row)
            
            # fill in empty
            locations.at[i, 'gc_address'] = 'UNSUCCESSFUL'
            
            # save latitude and longitude
            locations.at[i, 'y'] = None
            locations.at[i, 'x'] = None
            
            #update
            n_iter += 1
        
    elif n_iter == 20:
        
        # geocode location
        geocoded = geolocator.geocode(row['origin'], timeout=120)
        
        try:            
            # get geocoded address
            locations.at[i, 'gc_address'] = geocoded.address
            
            # save latitude and longitude
            locations.at[i, 'y'] = geocoded.latitude
            locations.at[i, 'x'] = geocoded.longitude
            
            #update
            n_iter += 1
        except:
            
            # append list
            unsuc.append(row)
            
            # fill in empty
            locations.at[i, 'gc_address'] = 'UNSUCCESSFUL'
            
            # save latitude and longitude
            locations.at[i, 'y'] = None
            locations.at[i, 'x'] = None
            
            #update
            n_iter += 1
        
        # 1-indexed iterator
        current_i = i + 1
        
        # print progress
        print('[INFO] - Geocoding progress ' + str(current_i) + '/' + str(len(locations)))
        
        # save progress
        locations.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_locations_intermediate.pkl')
        
        # wait
        time.sleep(random.randint(40,60))
        
        # reset n_iter
        n_iter = 1

# save locations
locations.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_2014-2022_HEIs_locations.pkl')

# get nominatim locations
nomloc = pd.read_pickle("/home/tuomvais/GIS/MOBI-TWIN/Erasmus/data_v2/geocoded_2014-2022_locations_HEIs_nominatim.pkl")
nomsuc = nomloc[~nomloc['gc_address'].isin(['UNSUCCESSFUL','nan'])].reset_index(drop=True)

# get locations with unsuccessful and successful geocoding
unloc = locations[locations['gc_address'].isin(['UNSUCCESSFUL','nan'])].reset_index(drop=True)
success = locations[~locations['gc_address'].isin(['UNSUCCESSFUL','nan'])].reset_index(drop=True)

# set second origin column for joining nominatim identified data
for i, row in unloc.iterrows():
    
    # get the first part from normal address
    first = row['origin'].split(', ')[0]
    
    # check if first place exists in dictionaries
    try:
        unloc.at[i, 'nomi_match'] = picdict[first]
    except:
        pass
    try:
        unloc.at[i, 'nomi_match'] = oiddict[first]
    except:
        pass
    try:
        unloc.at[i, 'nomi_match'] = namedict[first]
    except:
        pass

# duplicate origins for unlocs for fixing
unloc['origin2'] = unloc['origin']

# unlocated fix dictionary
udict = {"Se331, Sweden":"Västerbotten, Sweden","Check The Pic In Urf For City, Spain":"Madrid, Spain",
         "0, Italy":"Rome, Italy","Paris Cedex 06, France":"Paris, France","Unknown, Sweden":"Stockholm, Sweden",
         "Leioa, Bilbao, San Sebastian And Vitoria, Spain":"Bilbao, Spain","Sceaux : (Paris), Troyes, Montpellier, France":"Montpellier, France",
         "-, Italy":"Rome, Italy", "SÅborg, Denmark":"Søborg, Denmark","Caen Cedex 5, France":"Caen, France",
         "Saint- Ouen, France":"Saint-Ouen, France","Don'T Know, Finland":"Helsinki, Finland",
         "Check The Pic In Urf For City, Finland":"Turku, Finland","Paris Cedex 05, France":"Paris, France",
         "Check The Pic In Urf For City, Denmark":"Copenhagen, Denmark","Check The Pic In Urf For City, Germany":"Hamburg, Germany",
         "Falun And BorlNge (Twin Campus), Sweden":"Falun, Sweden","Falun And Borlänge (Twin Campus), Sweden":"Borlänge, Sweden",
         "Odense, Kolding, Esbjerg, Sønderborg And Slagelse, Denmark":"Odense, Denmark",
         "SzKesfehRvR, Hungary":"Székesfehérvár, Hungary","WOcAwek, Poland":"Wloclawek, Poland",
         "Check The Pic In Urf For City, Belgium":"Brussels, Belgium","69373 Lyon Cedex 08, France":"Lyon, France",
         "Praha 5, Czech Republic":"Prague, Czech Republic", "Tr510, Turkey":"West Anatolia, Turkey",
         "D  Hamburg01, Germany":"Hamburg, Germany","GVle, Sweden":"Gävle, Sweden","Check The Pic In Urf For City, France":"Paris, France",
         "Odense, Kolding, Esbjerg, SNderborg And Slagelse, Denmark":"Kolding, Denmark","Klagenf, Austria":"Klagenfurt, Austria",
         "Rnak, Turkey":"Sirnak, Turkey","Dijon Cedex, Norway":"Dijon, France","Boedapest, Hungary":"Budapest, Hungary",
         "Xxxxx, Poland":"Warsaw, Poland","Rennes Cedex 7, France":"Rennes, France","Brüsszel, Belgium":"Brussels, Belgium",
         "You Have The Pic So You Know The City, Finland":"Joensuu, Finland","Check The Pic In Urf For City, Norway":"Oslo, Norway",
         "14195 Berlin, Germany":"Berlin, Germany","VCklabruck, Austria":"Vöcklabruck, Austria",
         "Check The Pic In Urf For City, Sweden":"Uppsala, Sweden","CracVia, Poland":"Krakow, Poland",
         "Uppsala, Umeå, Alnarp And Skara, Sweden":"Umeå, Sweden","-, Portugal":"Porto, Portugal",
         "VeszprM, Hungary":"Veszprem, Hungary","Check The Pic In Urf For City, Hungary":"Budapest, Hungary",
         "See Era Id, ":"","Undefined, France":"Brest, France","DonauwRth, Germany":"Donauwörth, Germany",
         "Dijon Cedex, Finland":"Dijon, France","Dijon Cedex, Sweden":"Dijon, France","SetBal, Portugal":"Setubal, Portugal",
         "Check The Pic In Urf For City, Austria":"Vienna, Austria","BrHl, Germany":"Brühl, Germany",
         "Es61, Spain":"Andalusia, Spain", "Irllimeric01, Ireland":"Limerick, Ireland",
         "Check The Pic In Urf For City, Turkey":"Ankara, Turkey","Check The Pic In Urf For City, Italy":"Milan, Italy",
         "Stoccolma, Sweden":"Stockholm, Sweden","Dresda, Germany":"Dresden, Germany",
         "F  Paris007, France":"Paris, France","SNderborg, Denmark":"Sønderborg, Denmark",
         "Irldublin01, Ireland":"Dublin, Ireland","Irlgalway01, Ireland":"Galway, Ireland",
         "GDLl, Hungary":"Gödöllö, Hungary","You Have The Pic So You Know The City, ":"",
         "F  Paris014, France":"Paris, France","Check The Pic In Urf For City, ":"",
         "Riga01, Latvia":"Riga, Latvia","Dortmund, Frankfurt, Hamburg, München, Köln, Germany":"Dortmund, Germany",
         "Check The Pic In Urf For City, Spain":"Madrid, Spain", "Ahinbey, Turkey":"Sahinbey, Turkey",
         "Akovec, Croatia":"Cakovec, Croatia","Enschede, Sweden":"Enskede, Sweden",
         "Varsavia, Poland":"Warsaw, Poland","Liubliana, Slovenia":"Ljublana, Slovenia",
         "Otros, Ireland":"Otterstown, Ireland","Checkurf, Spain":"Nerja, Spain","Google, Spain":"Madrid, Spain",
         "VarsVia, Poland":"Warsaw, Poland","Estocolmo, Sweden":"Stockholm, Sweden",
         "Vienna, Asutria":"Vienna, Austria","Viena, Austria":"Vienna, Austria","Enschede, Turkey":"Eskişehir‎, Turkey",
         "Kambja Vald, Tartumaa, Estonia":"Kambja, Estonia","HódmezVásárhely, Hungary":"Hódmezővásárhely, Hungary",
         "Lerissos, Greece":"Ierissos, Greece", "Ülenurme Vald, Tartumaa, Estonia":"Ülenurme, Estonia",
         "Checkurf, Turkey":"Şanlıurfa, Turkey","Checkurf, Hungary":"Budapest, Hungary",
         "Enschede, France":"Paris, France","Irlcork01, Ireland":"Cork, Ireland",
         "Desconocido, Italy":"Rome, Italy","Szekszd, Hungary":"Szekszard, Hungary",
         "Breslavia, Poland":"Warsaw, Poland","TNsberg, Norway":"Tønsberg, Norway",
         "Cadice, Spain":"Cadiz, Spain","Desconocido, Germany":"Essen, Germany",
         "Genua, Italy":"Genova, Italy","E  Valenci01, Spain":"Valencia, Spain",
         "Checkurf, Denmark":"Randers, Denmark", "Mnchen, Germany":"München, Germany",
         "Kaskelen, Kazakhstan":"Qaskelen, Kazakhstan","Otros, Portugal":"Porto, Portugal",
         "Rzym, Italy":"Rome, Italy", "Kgs Lyngby, Denmark":"Kongens Lyngby, Denmark",
         "Saint BarthLemy D'Anjou, France":"Saint Barthélemy D'Anjou, France",
         "DiyarbakR, Turkey":"Diyarbakır, Turkey", "Eskilstuna And Västerås (Twin Campus), Sweden":"Eskilstuna, Sweden",
         "Saint- Ouen, France":"Saint-Ouen, France", "See Era Id, United Kingdom":"Belfast, United Kingdom",
         "Milao, Italy":"Milan, Italy", "See Era Id, Czech Republic":"Prague, Czech Republic",
         "Bialyst, Poland":"Bialystok, Poland", "Arcavacata Di Rente (Cs), Italy":"Arcavacata, Italy",
         "Check The Pic In Urf For City, Portugal":"Braganca, Portugal","Marmolejo (Jaén), Spain":"Marmolejo, Spain",
         "La Haye, Netherlands":"The Hague, Netherlands", "Dijon Cedex, Portugal":"Dijon, France",
         "See Era Id, Austria":"Linz, Austria","Oslo, Norway, Norway":"Oslo, Norway",
         "Las Palmas, G.Canari, Spain":"Las Palmas, Spain","Dresda, Germany":"Dresden, Germany",
         "Markgroningen, Germany":"Markgröningen, Germany", "Check The Pic In Urf For City, Czech Republic":"Pardubice, Czech Republic",
         "Belgique, Belgium":"Bruges, Belgium", "Espoo (In Mailing Address Aalto), Finland":"Espoo, Finland",
         "SzekszRd, Hungary":"Szekszárd, Hungary","You Have The Pic So You Know The City, Denmark":"Herning, Denmark",
         "Carrigaline, Cork, Ireland":"Carrigaline, Ireland","Wolfenbuttel, Germany":"Wolfenbüttel, Germany",
         "Gdyinia, Poland":"Gdynia, Poland", "Mestoles-Madrid, Spain":"Mostoles, Spain",
         "Rychnov Nad KnNou, Czech Republic":"Rychnov nad Kněžnou, Czech Republic",
         "Pl22, Poland":"Śląskie, Poland","Paris 7, France":"Paris, France",
         "Oliveira De AzemIs, Portugal":"Oliveira de Azeméis, Portugal","Rzym, Italy":"Rome, Italy",
         "Stoccarda, Germany":"Stuttgart, Germany","Umea01, Sweden":"Umeå, Sweden",
         "Nepcity, Spain":"Barcelona, Spain", "Cs 40700 Grenoble 9, France":"Grenoble, France",
         "Dublin 7, Ireland":"Dublin, Ireland","Checkurf, Finland":"Rovaniemi, Finland",
         "Itf3, Italy":"Campania, Italy", "Praha07, Czech Republic":"Prague, Czech Republic",
         "Gandra-Prd, Portugal":"Gandra, Portugal", "75337 Paris Cedex 07, France":"Paris, France",
         "Lt-53361 Kauno R., Lithuania":"Kaunas, Lithuania", "De2, Germany":"Oberbayern, Germany",
         "Dsseldorf, Germany":"Düsseldorf, Germany", "Uk Bristol01, United Kingdom":"Bristol, United Kingdom",
         "Cp Groningen, Netherlands":"Groningen, Netherlands","Oth, Norway":"Tromsø, Norway",
         "Edimbourg, United Kingdom":"Edinburgh, United Kingdom","Gotemburgo, Sweden":"Gothenburg, Sweden",
         "I-00168 Roma, Italy":"Rome, Italy", "Irlmaynoot01, Ireland":"Maynooth, Ireland",
         "Landshu01, Germany":"Landshut, Germany","S-58183 Linkoping, Sweden":"Linkoping, Sweden",
         "Groning03, Netherlands":"Groningen, Netherlands", "Eberhard Karls Universitaet Tuebingen, Germany":"Tübingen, Germany",
         "GoleniW, Poland":"Goleniow, Poland", "Nepcity, Belgium":"Brussels, Belgium","Google, Turkey":"Göreme, Turkey",
         "S-104 01 Stockholm, Sweden":"Stockholm, Sweden","BBlingen, Germany":"Böblingen, Germany",
         "B  Bruxel04, Belgium":"Brussels, Belgium","Suchdol-Praha-Suchdol, Czech Republic":"Prague, Czech Republic",
         "Lisboa Codes, Portugal":"Lissabon, Portugal","Novedrate Co, Italy":"Novedrate, Italy",
         "16124 Genova, Italy":"Genoa, Italy","Francoforte, Germany":"Frankfurt, Germany",
         "Checkurf, Ireland":"Dublin, Ireland","Pt17, Portugal":"Lissabon, Portugal",
         "Checkurf, Germany":"Berlin, Germany","Enschede, Finland":"Enontekiö, Finland",
         "Pl12, Poland":"Mazowieckie, Poland","Hu333, Hungary":"Csongrád-Csanád, Hungary",
         "03Ibor, Slovenia":"Maribor, Slovenia", "0, Ireland":"Dublin, Ireland",
         "Irldublin02, Ireland":"Dublin, Ireland", "Biberach An Der Riã, Germany":"Biberach an der Riß, Germany",
         "Lesparre MDoc Cedex, France":"Lesparre-Médoc, France", "Salonicco, Greece":"Thessaloniki, Greece",
         "Amburgo, Germany":"Hamburg, Germany", "Irldublin04, Ireland":"Dublin, Ireland",
         "Eská Lípa, Czech Republic":"Ceská Lípa, Czech Republic", "P Lisboa01, Portugal":"Lissabon, Portugal",
         "JRvenp, Finland":"Järvenpää, Finland","TRnitz, Austria":"Ternitz, Austria",
         "G  Thessal01, Greece":"Thessaloniki, Greece", "VNnS, Sweden":"Vännäs, Sweden",
         "Check The Pic In Urf For City, Lithuania":"Vilnius, Lithuania","L-9530 Wiltz, Luxembourg":"Wiltz, Luxembourg",
         "BYKcakmece Istanbul, Turkey":"Büyükçekmece, Turkey","Kerkyra, Korfu Sziget, Greece":"Corfu, Greece",
         "Checkurf, Sweden":"Stockholm, Sweden", "Odense, Kolding, Esbjerg, Sonderborg And Slagelse, Denmark":"Slagelse, Denmark",
         "SauRkrKur, Iceland":"Sauðárkrókur, Iceland", "75231 Paris Cedex 05, France":"Paris, France",
         "Undefined, Netherlands":'Amsterdam, Netherlands',"AngermNde, Germany":"Tangermünde, Germany",
         "BKScsaba, Hungary":"Békéscsaba, Hungary","Pl61, Poland":"Torun, Poland",
         "Si018, Slovenia":"Postjona, Slovenia","Desconocido, Netherlands":"Amsterdam, Netherlands",
         "10 000 Zagreb, Croatia":"Zagreb, Croatia","SarrebrCk, Germany":"Sarrebrück, Germany",
         "Checkurf, France":"Paris, France","Checkurf, Greece":"Athens, Greece","Checkurf, Poland":"Warsaw, Poland",
         "København C, Denmark":"Copenhagen, Denmark","VilleurbanneCedex, France":"Villeurbanne, France",
         "Nepcity, Portugal":"Lissabon, Portugal","Nepcity, Germany":"Berlin, Germany",
         "Zagabria, Croatia":"Zagreb, Croatia","Wiesbaden, Oestrich-Winkel, Germany":"Wiesbaden, Germany",
         "Otr, Austria":"Lienz, Austria", "Check The Pic In Urf For City, Bulgaria":"Sofia, Bulgaria",
         "Wilno, Lithuania":"Vilnius, Lithuania","Odense And Vejle, Denmark":"Vejle, Denmark",
         "Verona (Vr), Italy":"Verona, Italy", "75230 Paris Cedex 05, France":"Paris, France",
         "Nottingham Ng7 2Rd, United Kingdom":"Nottingham, United Kingdom","Mollet Del VallS, Spain":"Mollet Del Valles, Spain",
         "Riga, Lithuania":"Riga, Latvia","JPing, Sweden":"Köping, Sweden","Undefined, Belgium":"Mons, Belgium",
         "Itf6, Italy":"Cosenza, Italy","Dkzz, Denmark":"Skagen, Denmark","Iayes, Romania":"Iasi, Romania",
         "Be10, Belgium":"Brussels, Belgium","Es30, Spain":"Madrid, Spain",
         "95094 Cergy CDex, France":"Cergy, France","Xxxxx, Netherlands":"Rotterdam, Netherlands",
         "69288 Lyon Cedex 02, France":"Lyon, France","Es51, Spain":"Barcelona, Spain",
         "Prerov I, Mesto, Czech Republic":"Přerov I-Město, Czech Republic","BTera (Valencia), Spain":"Bétera, Spain",
         "999896856, Greece":"Athens, Greece","999995602, Italy":"Padova, Italy","D  Tubinge01, Germany":"Tübingen, Germany",
         "997179789, Hungary":"Budapest, Hungary","Mestoles, Spain":"Mostoles, Spain",
         "Uk London005, United Kingdom":"London, United Kingdom", "Madrid Y Reikiavik, Iceland":"Reykjavik, Iceland",
         "Edgbaston, Birmingham B5 7Sn, United Kingdom":"Birmingham, United Kingdom",
         "Cz-116 38  Praha I, Czech Republic":"Prague, Czech Republic","Athens, Zografou, Greece":"Athens, Greece",
         "Paris010, France":"Paris, France","Martorell (Barcelona), Spain":"Barcelona, Spain",
         "Irlcork, Ireland":"Cork, Ireland","-, Slovenia":"Bled, Slovenia",
         "Praha 11-Chodov, Czech Republic":"Prague, Czech Republic","Sezz, Sweden":"Örebro, Stockholm",
         "Balma Cedex, France":"Balma, France","Elverum01, Norway":"Elverum, Norway","See Urf, Poland":"Warsaw, Poland",
         "Otros, Lithuania":"Riga, Latvia","Avignon, Cedex, France":"Avignon, France",
         "See Urf, United Kingdom":"Aberdeen, United Kingdom","8005, 139 Faro, Portugal":"Faro, Portugal",
         "Various, Spain":"Bilbao, Spain","Checkurf, Austria":"Innsbruck, Austria",
         "D  Potsdam01, Germany":"Potsdam, Germany","70833 Ostrava Poruba, Czech Republic":"Ostrava, Czech Republic",
         "56100 Pisa, Italy":"Pisa, Italy","Cz Praha09, Czech Republic":"Prague, Czech Republic",
         "0, Bulgaria":"Sofia, Bulgaria", "Ibenik, Croatia":"Šibenik, Croatia","St. Denis Cedex 09, France":"St. Denis, France",
         "Itf1, Italy":"Teramo, Italy","Pl63, Poland":"Starogardzki, Poland","D-10963 Berlin, Germany":"Berlin, Germany",
         "999849423, Spain":"Jaén, Spain",
         "Hospitalet De Llobregat, Spain":"L'Hospitalet De Llobregat, Spain",
         "Checkurf, Italy":"Rome, Italy", "Enschede, Hungary":"Budapest, Hungary", "Enschede, Portugal":"Lissabon, Portugal",
         "999864846, Spain":"Valencia, Spain","Enschede, Norway":"Oslo, Norway", "Pt11, Portugal":"Douro, Portugal",
         "Kumes, Hungary":"Budapest, Hungary","VRpalota, Hungary":"Várpalota, Hungary",
         "Pl41, Poland":"Pilski, Poland", "999585583, Greece":"Athens, Greece", "75775 Paris Cedex 16, France":"Paris, France",
         "Kobenhagn, Denmark":"Copenhagen, Denmark",
         "Santiagodecompostela, Spain":"Santiago de Compostela, Spain","Irldublin, Ireland":"Dublin, Ireland",
         "75251 Paris Cedex 05, France":"Paris, France","Akwizgran, Germany":"Aachen, Germany",
         "D  Trier01, Germany":"Trier, Germany","Undefined, Greece":"Thessaloniki, Germany",
         "Surrey Tw20 0Ex, United Kingdom":"Surrey, United Kingdom","Nl Delft01, Netherlands":"Delft, Netherlands",
         "Trollhã¤Ttan, Sweden":"Trollhättan, Sweden", "Münchengladbach, Germany":"Mönchengladbach, Germany",
         "Vilnius, Litauen, Lithuania":"Vilnius, Lithuania","2520 Luxembourg, Luxembourg":"Luxembourg, Luxembourg",
         "EdArnhem, Belgium":"Arnhem, Belgium","Pl 00-927 Warszawa, Poland":"Warsaw, Poland",
         "Sztokholm, Sweden":"Stockholm, Sweden", "Herzogenerauch, Germany":"Herzogenaurach, Germany",
         "Linkopi01, Sweden":"Linköping, Sweden","Praha 8, Libe, Czech Republic":"Prague, Czech Republic",
         "Lappenraata, Finland":"Lappeenranta, Finland", " Cala'N Bosch, Spain":"Cala en Bosc, Spain",
         "HRning, Denmark":"Herning, Denmark","Cluj, Napoca, Romania":"Cluj-Napoca, Romania",
         "Jelenia GRa 5, Poland":"Jelenia Góra, Poland","Jandia, Fuerteventura, Spain":"Fuerteventura, Spain",
         "Sanningerberg, Luxembourg":"Senningerberg, Luxembourg","TRrega, Spain":"Tarrega, Spain",
         "Dijon Cedex, Estonia":"Tallinn, Estonia", "Lisboa109, Portugal":"Lissabon, Portugal",
         "Amsterd01, Netherlands":"Amsterdam, Netherlands","Ed Arnhem, Netherlands":"Arnhem, Netherlands",
         "Zurow Ot Fahren, Germany":"Zurow, Germany", "Dublin , Ireland":"Dublin, Ireland",
         "Oth, Lithuania":"Klaipeda, Lithuania", "Undefined, Germany":"Regensburg, Germany",
         "0, Croatia":"Split, Croatia", "Lv006, Latvia":"Riga, Latvia","Sk010, Slovakia":"Bratislava, Slovakia",
         "Tr100, Turkey":"Istanbul, Turkey","No051, Norway":"Hordaland, Norway","Praha, Prag, Czech Republic":"Prague, Czech Republic",
         "Kadyks, Spain":"Cadiz, Spain","Ejtun, Malta":"Żejtun, Malta",
         "Jùrpeland, Norway":"Jørpeland, Norway", "Check The Pic In Urf For City, Poland":"Warsaw, Poland",
         "Lingby, Denmark":"Kongens Lyngby, Denmark", "Angers Cedex 01, Hungary":"Budapest, Hungary",
         "Check The Pic In Urf For City, Croatia":"Dubrovnik, Croatia","Otros, Sweden":"Jönköping, Sweden",
         "Desconocido, Belgium":"Brussels, Belgium",
         "949261692, Germany":"Augsburg, Germany","E  Tenerif01, Spain":"Tenerife, Spain",
         "936847244, France":"Roubaix, France","Lt-44248 Kaunas, Lithuania":"Kaunas, Lithuania",
         "UnterschleiHeim, Germany":"Unterschleißheim, Germany","Koblenz And Landau, Germany":"Landau, Germany",
         "Nantes 3, France":"Nantes, France", "Nieuvennep, Netherlands":"Nieuw-Vennep, Netherlands",
         "Warszawa,, Poland":"Warsaw, Poland","HRnSand, Sweden":"Härnösand, Sweden",
         "Checkurf, Belgium":"Liege, Belgium", "Iauliai, Lithuania":"Šiauliai, Lithuania",
         "Algatocin (Malaga), Spain":"Malaga, Spain", "Dk Arhus01, Denmark":"Arhus, Denmark",
         "P  Coimbra01, Portugal":"Coimbra, Portugal","Villaviciosa De OdN, Spain":"Villaviciosa De Odon, Spain",
         "VRu, Estonia":"Võru, Estonia", "Vaxzo, Sweden":"Växjö, Sweden","Kajaanin, Finland":"Kajaani, Finland",
         "Alcuescar, Spain":"Alcuéscar, Spain","949283614, Germany":"Dortmund, Germany",
         "Monachium, Germany":"München, Germany","Desconocido, Portugal":"Lissabon, Portugal",
         "Irldublin27, Ireland":"Dublin, Ireland","75270 Paris Cedex 06, France":"Paris, France",
         "Oth, Cyprus":"Agia Napa, Cyprus","D-10117 Berlin, Germany":"Berlin, Germany",
         "Kempten02, German":"Kempten, Germany", "20126 Milano, Italy":"Milano, Italy",
         "Härnosand, Östersund, Sundsvall, Sweden":"Härnosand, Sweden","Kuanas, Lithuania":"Kaunas, Lithuania",
         "Ubisoft Entertainment Sweden Ab Box 4297 203 14 Ma, Sweden":"Malmö, Sweden",
         "Unknown, Estonia":"Tallinn, Estonia", "CalaN Bosch Cuitadella Menorca, Spain":"Cala en Bosc, Spain",
         "Reykjavik, Ireland":"Reykjavik, Iceland", "RZekne, Latvia":"Rēzekne, Latvia",
         "Valenzcia, Spain":"Valencia, Spain", "Check The Pic In Urf For City, Latvia":"Rezekne, Latvia",
         "Irldublin44, Ireland":"Dublin, Ireland",
         "Norimberga, Germany":"Nürnberg, Germany", "3500 Hasselt, Belgium":"Hasselt, Belgium",
         "Brigh And Hove, United Kingdom":"Brighton And Hove, United Kingdom","Spånga Stockholm, Sweden":"Stockholm, Sweden",
         "PDaste Village, Muhu Parish, Estonia":"Pädaste, Estonia", "Poland, Poland":"Warsaw, Poland",
         "Vastera01, Sweden":"Västerås, Sweden", "69007 Lyon Cedex 07, France":"Lyon, France",
         "998076748, Turkey":"Istanbul, Turkey", "Kb Enschede, Netherlands":"Enschede, Netherlands",
         "Eindhoven, Denmark":"Copenhagen, Denmark","Otros, Bulgaria":"Sofia, Bulgaria",
         "28199 Bremen, Germany":"Bremen, Germany","Klagenfurt Am WRthersee, Austria":"Klagenfurt, Austria",
         "RJiena, Latvia":"Rūjiena, Latvia",
         "Check The Pic In Urf For City, Romania":"Bucharest, Romania","KPavogur, Iceland":"Kópavogur, Iceland",
         "OWiCim, Poland":"Oświęcim, Poland","Praha 2, Nové Mesto, Czech Republic":"Prague, Czech Republic",
         "Grenoble Cedex9, France":"Grenoble, France","SDertLje, Sweden":"Södertälje, Sweden",
         "Rahovec, Kosovo * UN resolution":"Rahovec, Kosovo","Orekhovo-Zuevo, Russian Federation":"Orekhovo-Zujevo, Russian Federation",
         "Nijimengen, Netherlands":"Nijmengen, Netherlands","Moscu, Russian Federation":"Moscow, Russian Federation",
         "Ystese, Norway":"Øystese, Norway",
         "Crete, Hersonissos, Greece":"Chersónisos, Greece","999650088, Sweden":"Örebro, Sweden",
         "UnterfHring, Germany":"Unterföhring, Germany","Paris, Jouy-En-Josas, France":"Paris, France",
         "STubal, Portugal":"Setubal, Portugal","Maribor01, Slovakia":"Maribor, Slovakia",
         "Irlkildare04, Ireland":"Kildare, Ireland", "E  Logrono01, Spain":"Logroño, Spain",
         "Zm Utrecht, Netherlands":"Utrecht, Netherlands", "Datriina, Finland":"Kotka, Finland",
         "Kortrijk, Bulgaria":"Kortrijk, Belgium","Ochoz U Brna, Czech Republic":"Brno, Czech Republic",
         "IbNeTi, Romania":"Ibănești, Romania",
         "Xxxxx, Lithuania":"Kaunas, Lithuania","Undefined, Italy":"Rome, Italy",
         "BeyazT, Fatih, Istanbul, Turkey":"Istanbul, Turkey", "Kufstein, Poland":"Kufstein, Austria",
         "ValaSké MeziÍÍ, Czech Republic":"Valasske Mezirici, Czech Republic",
         "Walencja, Spain":"Valencia, Spain","MagyaralmS, Hungary":"Magyaralmás, Hungary",
         "Reykjavã­K, Iceland":"Reykjavik, Iceland","Tralee, Co. Kerry, Ireland":"Tralee, Ireland",
         "BKara, Malta":"Birkirkara, Malta","AlIninkai, Lithuania":"Alšininkai, Lithuania",
         "Provodov, Onov, Czech Republic":"Provodov-Šonov, Czech Republic", "Eidnhover, Norway":"Oslo, Norway",
         "WeLing, Germany":"Weßling, Germany", "Cascatalà, Spain":"Cas Català, Spain","Spopron, Hungary":"Sopron, Hungary",
         "Lisboa107, Portugal":"Lissabon, Portugal",
         "Bercelona, Spain":"Barcelona, Spain","Elverum02, Norway":"Elverum, Norway","MaEikiai, Lithuania":"Mažeikiai, Lithuania",
         "Peterborough, Spain":"Peterborough, United Kingdom","FRstenwalde, Germany":"Fürstenwalde, Germany",
         "Nottingham, Uk, United Kingdom":"Nottingham, United Kingdom","Dijon Cedex, Lithuania":"Kaunas, Lithuania",
         "Riga (Lv), Latvia":"Riga, Latvia", "Enschede, Greece":"Thessaloniki, Greece",
         "Rkelljunga, Sweden":"Örkelljunga, Sweden", "943245461, Spain":"Valencia, Spain",
         "La Roda (Albacete), Spain":"La Roda, Spain",
         "Checkurf, Norway":"Oslo, Norway", "D Berlin13, Germany":"Berlin, Germany",
         "Bortonigla, Croatia":"Brtonigla, Croatia","HRnum, Germany":"Hörnum, Germany",
         "Merseyside  Liverpool, United Kingdom":"Liverpool, United Kingdom","Exeter, Devon, Ex4 4Rn., United Kingdom":"Exeter, United Kingdom",
         "I  Siena01, Italy":"Siena, Italy", "Vilnius, Romania":"Vilnius, Lithuania",
         "66860 Perpignan Cedex, France":"Perpignan, France", "Paris379, France":"Paris, France",
         "49003 Angers Cedex 01, France":"Angers, France","Toulouse CDex 9, France":"Toulouse, France",
         "Village Of Sheinovo,  Obstina Kazanlak, Bulgaria":"Sheynovo, Bulgaria",
         "Pxl, Belgium":"Hasselt, Belgium","Catalunya, Spain":"Barcelona, Spain",
         "Lappeeranta, Finland":"Lappeenranta, Finland","Vysoké Mýto, Czech Republic":"Hradec, Czech Republic",
         "D31141 Hildesheim, Germany":"Hildesheim, Germany","Xxxxx, France":"Paris, France",
         "Xxxxx, Slovakia":"Bratislava, Slovakia", "4000 Liege, Belgium":"Liege, Belgium",
         "Georg-August-Universitaet Goettingen Stiftung Oeffentlichen Rechts, Germany":"Göttingen, Germany",
         "Ie021, Ireland":"Dublin, Ireland","Ro21, Romania":"Vaslui, Romania",
         "949316982, Belgium":"Antwerpen, Belgium","997963646, Germany":"Brandenburg, Germany",
         "949657452, Germany":"Pforzheim, Germany",
         "999986096, Belgium":"Ghent, Belgium",
         "At13, Austria":"Vienna, Austria","Hr041, Croatia":"Zagreb, Croatia",
         "31058 Toulouse Cedex 9, France":"Tolouse, France","Lt002, Lithuania":"Kaunas, Lithuania",
         "Xxxxx, Portugal":"Lissabon, Portugal","Ro11, Romania":"Cluj-Napoca, Romania",
         "JLich, Germany":"Jülich, Germany",
         "Mieziskiai, Panevezys Region, Lithuania":"Mieziskiai, Lithuania",
         "NagyvZsony, Hungary":"Nagyvázsony, Hungary", "QuTigny, France":"Quetigny, France",
         "Sliema, Greece":"Sliema, Malta",
         "Rommetv01, Norway":"Haugesund, Norway","Arhus01, Denmark":"Arhus, Denmark",
         "Vroklave, Poland":"Wroclaw, Poland", "Tampere, Ireland":"Tampere, Finland",
         "BGles, France":"Begles, France","Puntagords, Spain":"Puntagorda, Spain",
         "Taxbiex, Malta":"Ta' Xbiex, Malta","C0Penhagen S., Denmark":"Copenhagen, Denmark",
         "Trausnick, Germany":"Krausnick, Germany", "Athine04, Greece":"Athens, Greece",
         "Seinajoki, Ilmajoki, Jurva, Kauhajoki, Kauhava, Ahtori, Finland":"Seinäjoki, Finland",
         "Musninkai, Irvint R., Lithuania":"Musninkai, Lithuania","Paguera,  Calvia,  Mallorca, Spain":"Mallorca, Spain",
         "Valenciennes, Spain":"Valencia, Spain", "Obertsdorf, Germany":"Oberstdorf, Germany",
         "Kobenham, Denmark":"Copenhagen, Denmark", "Dijoin, France":"Dijon, France",
         "Qaqortoq, Denmark":"Qaqortoq, Greenland","Lstykke, Denmark":"Ølstykke, Denmark",
         "Ryga, Latvia":"Riga, Latvia","Wienna, Austria":"Vienna, Austria",
         "Alcininkai, Lithuania":"Salcininkai, Lithuania","Provodov-Onov, Czech Republic":"Provodov-Šonov, Czech Republic",
         "Check The Pic In Urf For City, The Republic of North Macedonia":"Skopje, North Macedonia",
         "Irlgalway, Ireland":"Galway, Ireland","Kbenhavn, Denmark":"Copenhagen, Denmark",
         "Västerås And Eskilstuna (Twin Campus), Sweden":"Västerås, Sweden",
         "PetrAlka, Slovakia":"Petržalka, Slovakia","PieksMKi, Finland":"Pieksämäki, Finland",
         "Greifswald-Insel Riems, Germany":"Riems, Germany","Pophos, Cyprus":"Pafos, Cyprus",
         "Märjamaa Vald, Raplamaa, Estonia":"Märjamaa, Estonia","HLo, Sweden":"Hölö, Sweden",
         "Ksendal, Norway":"Øksendal, Norway","Luxlux-Vil01, Luxembourg":"Luxembourg´, Luxembourg",
         "Tingsryrd, Sweden":"Tingsryd, Sweden","Juvaskyla, Finland":"Jyväskylä, Finland",
         "Joensuu, Kuopio, Savonlinna, Finland":"Joensuu, Finland","Tãœbingen, Germany":"Tübingen, Germany",
         "Βαρκελωνη, Spain":"Barcelona, Spain","Boedapest, Hungary":"Budapest, Hungary",
         "Παρισι, France":"Paris, France","Βρυξελλες, Belgium":"Brussels, Belgium",
         "Βερολινο, Germany":"Berlin, Germany","Fundacion Universitaria San Antonio, Spain":"Murcia, Spain",
         "Clujnap, Romania":"Cluj-Napoca, Romania","Oulun Ammattikorkeakoulu Oy, Finland":"Oulu, Finland",
         "Κωνσταντινουπολη, Turkey":"Istanbul, Turkey","Bellaterra (Cerdanyola Del VallÅs), Spain":"Cerdanyola Del Vallés, Spain",
         "STurkurg, Denmark":"Copenhagen, Denmark", "Κοπεγχαγη, Denmark":"Copenhagen, Denmark",
         "Βουδαπεστη, Hungary":"Budapest, Hungary","Μαλαγα, Spain":"Malaga, Spain",
         "Fundacio Universitaria Balmes, Spain":"Vic, Spain","Fundacion Universidad Loyola Andalucia, Spain":"Cordoba, Spain",
         "Βερολίνο, Germany":"Berlin, Germany","Donauwürth, Germany":"Donauwörth, Germany","Λισαβονα, Portugal":"Lissabon, Portugal",
         "Universidad Del Pais Vasco,  Euskal Herriko Unibertsitatea, Spain":"Leioa, Spain",
         "Dortmund, Frankfurt, Hamburg, Munich, Köln, Germany":"Dortmund, Germany",
         "Γραναδα, Spain":"Granada, Spain","Βαρκελώνη, Spain":"Barcelona, Spain",
         "Ρωμη, Italy":"Rome, Italy","Biberach An Der Riãÿ, Germany":"Biberach An Der Riß, Germany",
         "Ρεν, France":"Rennes, France","Παφος, Cyprus":"Páfos, Cyprus","Ταμπερε, Finland":"Tampere, Finland",
         "Geilo. Viken County, Norway":"Geilo, Norway","Αμστερνταμ, Netherlands":"Amsterdam, Netherlands",
         "Ülenurme vald, Tartumaa, Estonia":"Ülenurme, Estonia","Μοναχο, Germany":"München, Germany",
         "Στοκχολμη, Sweden":"Stockholm, Sweden","Estrasburgo, France":"Strasbourg, France",
         "Παβια, Italy":"Pavia, Italy","Valašské Meziříčí, Czech Republic":"Valasske Mezirici, Czech Republic",
         "Dijon , Sweden":"Gothenburg, Sweden","Dijon , Finland":"Helsinki, Finland",
         "Αλμερια, Spain":"Almeria, Spain", "Fundacio Tecnocampus Mataro-Maresme, Spain":"Mataro, Spain",
         "Khimki Moskva, Russian Federation":"Khimki, Russia","Φρανκφουρτη, Germany":"Frankfurt am Main, Germany",
         "Ebc Euro-Business-College Gmbh, Germany":"Hamburg, Germany",
         "Fachhochschulstudiengänge Betriebs-Und Forschungseinrichtungen Der Wiener Wirtschaft, Austria":"Vienna, Austria",
         "Βιέννη, Austria":"Vienna, Austria","Αχεν, Germany":"Aachen, Germany",
         "Βασα, Finland":"Vaasa, Finland","Ucl Erhvervsakademi & Professionshojskole Si, Denmark":"Odense, Denmark",
         "E10209482, Belgium":"Leuven, Belgium","Αμβούργο, Germany":"Hamburg, Germany",
         "Βαρσοβια, Poland":"Warsaw, Poland","Εσεν, Germany":"Essen, Germany","Δουβλινο, Ireland":"Dublin, Ireland",
         "Σεβιλλη, Spain":"Sevilla, Spain","Βαλενθια, Spain":"Valencia, Spain",
         "Βαρσωβια, Poland":"Warsaw, Poland", "Fachhochschule Technikum Wien, Austria":"Vienna, Austria",
         "Λισαβωνα, Portugal":"Lissabon, Portugal","Cerdanyola Del VallÅs, Barcelona, Spain":"Cerdanyola Del Vallés, Spain",
         "Ensilis, Educacao E Formacao, Unipessoal Lda, Portugal":"Lissabon, Portugal",
         "E10209131, Spain":"Madrid, Spain","Zapadoceska Univerzita V Plzni, Czech Republic":"Plzen, Czech Republic",
         "Metropolitni Univerzita Praha Ops, Czech Republic":"Strasnice, Czech Republic",
         "Sczecin, Poland":"Szczecin, Poland","165 21 Prague 6, Suchdol, Czech Republic":"Prague, Czech Republic",
         "Κολωνια, Germany":"Köln, Germany","Alma Mater Studiorum, Universita Di Bologna, Italy":"Bologna, Italy",
         "Λςυκωσία, Cyprus":"Nikosia, Cyprus","Santayi, Spain":"Santanyi, Spain",
         "00-968 Warszawa 45, Poland":"Warsaw, Poland","Mãœnchen, Germany":"Munich, Germany",
         "Vilniaus Dizaino Kolegija, Lithuania":"Vilnius, Lithuania",
         "University Of Jyvďż˝Skylďż˝, Finland":"Jyväskylä, Finland",
         "Fhw Fachhochschul-Studiengänge Betriebs- Und Forschungseinrichtungen Der Wiener Wirtschaft Gmbh, Austria":"Vienna, Austria",
         "Ριγα, Latvia":"Riga, Latvia","Παρίσι, France":"Paris, France",
         "E10208943, Spain":"Bilbao, Spain","E10209394, Netherlands":"Eindhoven, Netherlands",
         "E10209112, Italy":"Venice, Italy","Libera Universita Maria Ss. Assunta Di Roma, Italy":"Rome, Italy",
         "Saalfeden, Austria":"Saalfelden, Austria","Provodov, Šonov, Czech Republic":"Provodov-Šonov, Czech Republic",
         "Veselí Nad Moravou, Czech Republic":"Veseli Nad Moravou, Czechia",
         "Κυπρος, Cyprus":"Cyprus, Cyprus","Buxelles, Belgium":"Brussels, Belgium","Νιτρα, Slovakia":"Nitra, Slovakia",
         "Přerov I, Město, Czech Republic":"Prerov, Czech Republic","Βουκουρεστι, Romania":"Bucharest, Romania",
         "Fh-Campus Wien, Verein Zur Forderung Des Fachhochschul-, Entwicklungs- Und Forschungszentrums Im Suden Wiens, Austria":"Vienna, Austria",
         "Drezno, Germany":"Dresden, Germany", "Dornbirn, Greece":"Marousi, Greece",
         "Mci Management Center Innsbruck Internationale Hochschule Gmbh, Austria":"Innsbruck, Austria",
         "Kodolanyi Janos Foiskola, Hungary":"Budapest, Hungary","Aindhofen, Netherlands":"Eindhoven, Netherlands",
         "Κοπενχαγη, Denmark":"Copenhagen, Denmark", "16628 Prague 6, Czech Republic":"Prague, Czech Republic",
         "Αμβουργο, Germany":"Hamburg, Germany","Lublin, Spain":"Malaga, Spain",
         "Τορινο, Italy":"Torino, Italy","Σοφια, Bulgaria":"Sofia, Bulgaria","Munichgladbach, Germany":"Mönchengladbach, Germany",
         "E10208971, Italy":"Milan, Italy","E10208601, Spain":"Vic, Spain","S’Gravenhage, Netherlands":"The Hague, Netherlands",
         "Skinnskateberg, Sweden":"Skinnskatteberg, Sweden","Datriina, Finland":"Kotka, Finland",
         "Turunyliopisto, Finland":"Turku, Finland","Vitenberga, Germany":"Wittenberg, Germany",
         "Ουτρεχτη, Netherlands":"Utrecht, Netherlands","Ντυσσελντορφ, Germany":"Düsseldorf, Germany",
         "Μαινζ, Germany":"Mainz, Germany","Γανδη, Belgium":"Ghent, Belgium","Λιεγη, Belgium":"Liege, Belgium",
         "Masarykova Univerzita, Czech Republic":"Brno, Czech Republic","Mechelen, Norway":"Mechelen, Belgium",
         "Stichting Christelijke Hogeschool Windesheim, Netherlands":"Zwolle, Netherlands",
         "E10209385, Spain":"Barcelona, Spain","Varşova, Poland":"Warsaw, Poland","Varšava, Poland":"Warsaw, Poland",
         "Fachhochschule Vorarlberg Gmbh, Austria":"Dornbirn, Austria","E10171437, France":"Talence, France",
         "E10107269, France":"Angers, France","E10186156, Austria":"Puch Bei Hallein, Austria",
         "E10209369, Norway":"Bergen, Norway","E10208856, Spain":"Barcelona, Spain","Dimitriskiu K. Zarasu Rajonas, Lithuania":"Zarasai, Lithuania",
         "E10134445, Spain":"Dos Hermanas, Sevilla, Spain","E10209094, Portugal":"Porto, Portugal",
         "E10148416, France":"Euralille, France", "Clujnapoca, Romania":"Cluj Napoca, Romania",
         "Mariánske Lázně, Czech Republic":"Marianske Lazne, Czech Republic",
         "E10209396, Germany":"München, Germany","E10209399, Norway":"Trondheim, Norway",
         "E10133370, France":"Toulouse, France", "Dijon , Estonia":"Tartu, Estonia",
         "Hameen Ammattikorkeakoulu Oy, Finland":"Hämeenlinna, Finland",
         "Havířov-Šumbark, Czech Republic":"Havířov, Czech Republic", "Gardabaer, Iceland":"Garðabær, Iceland",
         "Szczecin, Spain":"Malaga, Spain","Iade-Instituto De Artes Visuais Design E Marketing Sa, Portugal":"Lissabon, Portugal",
         "Schw?Bisch Gm?Nd, Germany":"Schwäbisch Gmünd, Germany","Schiltigheim, Germany":"Schiltigheim, France",
         "Münchengladbach, Germany":"Mönchengladbach, Germany","Vmu, Lithuania":"Kaunas, Lithuania",
         "Τεργεστη, Italy":"Trieste, Italy","Στουτγαρδη, Germany":"Stuttgart, Germany","Akademia Ignatianum W Krakowie, Poland":"Cracow, Poland",
         "Ναπολη, Italy":"Naples, Italy","Χαγη, Netherlands":"Haag, Netherlands","Μπρατισλάβα, Slovakia":"Bratislava, SLovakia",
         "Μπρατισλαβα, Slovakia":"Bratislava, Slovakia", "Σαραγόσα, Spain":"Zaragoza, Spain","Στοκχόλμη, Sweden":"Stockholm, Sweden",
         "Ρώμη, Italy":"Rome, Italy","Wroclaw, Romania":"Wroclaw, Poland","999864846, Spain":"Valencia, Spain",
         "997179789, Hungary":"Budapest, Hungary","165 21 Prague 6, Schudol, Czech Republic":"Prague, Czech Republic",
         "Βουκουρέστι, Romania":"Bucharest, Romania","Καλοπαναγιωτης, Cyprus":"Kalopanagiotis, Cyprus",
         "936847244, France":"Roubaix, France","949453170, France":"Paris, France",
         "Lapin Ammattikorkeakoulu Oy, Finland":"Rovaniemi, Finland","Κοπεγχάγη, Denmark":"Copenhagen, Denmark",
         "Universidade Europeia, Ensilis, Educação E Formação, Unipessoal Lda, Portugal":"Estrada da Correia, Lissabon, Portugal",
         "Paris & Ile De France,Rennes & West Of France,Lille & The North Of France,Lyon & Rhône-Alpes,Bordeaux & The Southwest Of France,Strasbourg & Eastern France, France":"Paris, France",
         "Universita Commerciale Luigi Bocconi, Italy":"Milan, Italy","Κωνσταντινουπολη, Türkiye":"Istanbul, Turkey",
         "Sant Vicente Dels Horts, Spain":"Sant Vicenc Dels Horts, Spain","Stichting Hogeschool Van Arnhem Ennijmegen Han, Netherlands":"Nijmegen, Netherlands",
         "E10206644, Italy":"Castellanza, Italy","E10066634, Portugal":"Lisbon, Portugal","Komorní Lhotka, Czech Republic":"Komorni Lhotka, Czechia",
         "B’Kara, Malta":"Birkirkara, Malta", "CBurgasRdoba, Spain":"Cordoba, Spain",
         "Srh Hochschule Der Populären Künste (Hdpk), Germany":"Berlin, Germany","Yrkeshogskolan Arcada Ab, Finland":"Helsinki, Finland",
         "Havířov-Prostřední Suchá, Czech Republic":"Havirov, Czech Republic", "Tessalonica, Greece":"Thessaloniki, Greece",
         "E10209085, Italy":"Pavia, Italy","E10209430, Sweden":"Gothenburg, Sweden","Hongarije, Hungary":"Budapest, Hungary",
         "Dhrousha, Cyprus":"Drouseia, Cyprus", "Mieziskiai, Panevezys Region, Lithuania":"Mieziskiai, Lithuania",
         "Οσλο, Norway":"Oslo, Norway","Estugarda, Germany":"Stuttgart, Germany","Julius-Maximilians-Universitat Wurzburg, Germany":"Wurzburg, Germany",
         "Praha 8, Libeň, Czech Republic":"PRague, Czech Republic","Lymassol, Cyprus":"Limassol, Cyprus",
         "Aachen, Spain":"Malaga, Spain","Ολλανδια, Netherlands":"Amsterdam, Netherlands","Σαραγοσα, Spain":"Zaragoza, Spain",
         "Paris244, France":"Paris, France", "Paris379, France":"Paris, France","Paris190, France":"Paris, France",
         "Halandri, Greece":"Chalandri, Greece","Zakhyntos, Greece":"Zákynthos, Greece",
         "Eslovàquia, Slovakia":"Banska Bystrica, Slovakia",'Vieshoji Istaiga "Europos Humanitarinis Universitetas", Lithuania':"Vilnius, Lithuania",
         "Στρασβουργο, France":"Strasbourg, France","Pau01, France":"Pau, France","998597056, Spain":"Villaviciosa, Spain",
         "Iayes, Romania":"Iasi, Romania","999643492, Turkey":"Ankara, Turkey","999995602, Italy":"Padova, Italy",
         "Μόναχο, Germany":"Μünchen, Germany","Vlinius, Lithuania":"Vilnius, Lithuania","Vaxjo, Finland":"Växjö, Sweden",
         "Karklės Kaimas, Lithuania":"Karklė, Lithuania","E10209037, Malta":"Msida, Malta", "Kortrijk, Bulgaria":"Kortrijk, Belgium",
         "E10200921, Germany":"Friedrichshafen, Germany","E10209019, Sweden":"Stockholm, Sweden",
         "E10209011, Iceland":"Reykjavik, Iceland", "E10209143, Türkiye":"Istanbul, Türkiye","E10208854, Austria":"Vienna, Austria",
         "E10209395, Netherlands":"Delft, Netherlands","E10209141, Sweden":"Lund, Sweden","E10209173, Germany":"Hamburg, Germany",
         "Anglo-Americka Vysoka Skola, Z.U., Czech Republic":"Mala Strana, Czech Republic","E10209107, Greece":"Athens, Greece",
         "Pamplona, Greece":"Athens, Greece","E10209515, Italy":"Padova, Italy","E10209120, Spain":"Zaragoza, Spain",
         "E10208637, Italy":"Trento, Italy","Poitiers , Haiti":"Port-au-Prince, Haiti",
         "Heltesberg, Germany":"Heltersberg, Germany","Mortorell, Spain":"Martorell, Spain",
         "Stiftung Fachhochschule Osnabrueck, Germany":"Osnabrück, Germany","E10085420, Belgium":"Bruxelles, Belgium",
         "E10189599, France":"Lille, France","E10112968, Portugal":"Lisbon, Portugal","Seeland Ot Gatersleben, Germany":"Seeland, Germany",
         "?Ahinbey, Turkey":"Sahinbey, Turkey","949496044, Bulgaria":"Veliko Tarnovo, Bulgaria",
         "949512340, Denmark":"Aarhus, Denmark", "949261692, Germany":"Augsburg, Germany","949283614, Germany":"Dortmund, Germany",
         "999585583, Greece":"Athens, Greece","Hiszpania, Spain":"Barcelona, Spain",
         "Otr, Denmark":"Aarhus, Denmark","Varsseveld, Germany":"Bocholt, Germany",
         "998164339, Turkey":"Fatih, Turkey","Various, Hungary":"Budapest, Hungary",
         "Hlilversum, Netherlands":"Hilversum, Netherlands", "Ãœskã¼Dar, Ä°Stanbul, Turkey":"Istanbul, Turkey",
         "Eindhoven, Lithuania":"Vilnius, Lithuania","Margitta, Romania":"Marghita, Romania",
         "Ramatvelle, France":"Ramatuelle, France","Imc Fachhochschule Krems Gmbh, Austria":"Krems an der Donau, Austria",
         "Γρανάδα, Spain":"Granada, Spain","Hamr Na Jezeře, Czech Republic":"Ceska Lipa, Czech Republic",
         "Ratyzbona, Germany":"Regensburg, Germany","Εικονες Ρεθυμνου Αξτε, Greece":"Rethymno, Greece",
         "Ζαγκρεμπ, Croatia":"Zagreb, Croatia","Rseberget, Sweden":"Stockholm, Sweden",
         "Rožnov Pod Radhoštem, Czech Republic":"Vsetin, Czech Republic","Undefined, Malta":"St. Julians, Malta",
         "Ostrožská Lhota, Czech Republic":"Ostrozska Lhota, Czechia", "Βελγιο, Belgium":"Ghent, Belgium",
         "Κολωνία, Germany":"Köln, Germany","Βρυξέλλες, Belgium":"Brussels, Belgium",
         "Klagenfurt Am W?Rthersee, Austria":"Klagenfurt Am Wörthersee, Austria","Nepcity, Turkey":"Istanbul, Turkey",
         "Nepcity, Norway":"Volda, Norway","Paris003, France":"Paris, France","Μαδρίτη, Spain":"Madrid, Spain",
         "Raunheim, Sweden":"Stockholm, Sweden","Groning01, Netherlands":"Groningen, Netherlands","Pirkanmaan Ammattikorkeakoulu Ltd., Finland":"Tampere, Finland",
         "Κρακοβια, Poland":"Cracow, Poland","Κουκλια Κυπρος, Cyprus":"Kouklia, Cyprus","18 Malmö, Suecia, Sweden":"Malmö, Sweden",
         "Kilonia, Germany":"Kiel, Germany","Nagyvárad, Romania":"Oradea, Romania", "Marosvásárhely, Romania":"Targu Miures, Romania",
         "Ta’Xbiex, Malta":"Ta' Xbiex, Malta","Taxbiex, Malta":"Ta' Xbiex, Malta","Leipzig, Ukraine":"Lviv, Ukraine",
         "Katowicache, Poland":"Katowice, Poland","Pophos, Cyprus":"Pafos, Cyprus","Železný Brod, Czech Republic":"Zelezny Brod, Czech Republic",
         "Uniwersytet Ekonomiczny W Krakowie, Poland":"Cracow, Poland","RÅsselsheim, Germany":"Rüsselsheim, Germany",
         "Φλωρεντια, Italy":"Florence, Italy","Jyvasky11, Finland":"Jyväskylä, Finland","Stettino, Poland":"Szczecin, Poland",
         "Haaga-Helia Ammattikorkeakoulu Oy, Finland":"Helsinki, Finland","Wäisswampech, Luxembourg":"Weiswampach, Luxembourg",
         "Mladá Boleslav (Kreis Pardubice), Czech Republic":"Mlada Boleslav, Czech Republic","Kaunas, Liechtenstein":"Kaunas, Lithuania",
         "Bajaoz, Spain":"Badajoz, Spain","Victor Babes University Of Medicine And Pharmacy, Romania":"Timisoara, Romania",
         "Karvina-Mizerov, Czech Republic":"Karvina, Czech Republic","Barrett Aerospace Pte Ltd, Czech Republic":"Prague, Czech Republic",
         "Viadrina, Germany":"Frankfurt am Oder, Germany","Nãœrtingen, Germany":"Nürtingen, Germany","Wrzburg, Germany":"Würzburg, Germany",
         "Helsinquia, Finland":"Helsinki, Finland","Grärelfing, Germany":"Gräfelfing, Germany","Glasway, Ireland":"Galway, Ireland",
         "Sounenjoki, Finland":"Suonenjoki, Finland","Kracovia, Poland":"Cracow, Poland","Srh Hochschulen Gmbh University Of Applied Sciences, Germany":"Berlin, Germany",
         "Georg-August-Universitaet Goettingen Stiftung Oeffentlichen Rechts, Germany":"Göttingen, Germany",
         "Village Of Sheinovo,  Obstina Kazanlak, Bulgaria":"Sheynovo, Bulgaria","Kongsbe02, Norway":"Kongsberg, Norway",
         "Alborg01, Denmark":"Alborg, Denmark","Puerto De Andratx, Mallorca, Spain":"Port D'Andratx, Spain",
         "Puerto De Alcudia Mallorca, Spain":"Puerto De Alcudia, Spain","Vyciaik, Lithuania":"Panevezys, Lithuania",
         "Fredkristad, Norway":"Fredrikstad, Norway","Beklinge, Sweden":"Bleklinge, Sweden",
         "Frankfurtamoder, Germany":"Frankfurt am Oder, Germany","Opole, Spain":"Malaga, Spain",
         "Provodov-Šonov, Czech Republic":"Vysokov, Czech Republic","Kralupy Nad Vltavou, Czech Republic":"Kralupy, Czech Republic",
         "Pl43, Poland":"Zielona Gora, Poland","Bapha, Bulgaria":"Varna, Bulgaria","Vilnius, Romania":"Vilnius, Lithuania",
         "Rwzeszow, Poland":"Rzeszow, Poland","University College South(Dk), Denmark":"Esbjerg ø, Denmark",
         "Weisbaden, Germany":"Wiesbaden, Germany","Nantes, Denmark":"Copenhagen, Denmark",
         "Lille103, France":"Lille, France","Rahovec, Kosovo * UN resolution":"Rahovec, Kosovo",
         "Κατοβίτσε, Poland":"Katovice, Poland","Cascatalà, Spain":"Cas Català, Spain",
         "Ελσινκι, Finland":"Helsinki, Finland", "Undefined, Finland":"Helsinki, Finland",
         "Rožnov Pod Radhoštěm, Czech Republic":"Roznov, Czech Republic","Nijmegen, Hungary":"Budapest, Hungary",
         "Carrer Pere Iv, 51 Piso 4 Oficina 2 Barcelona, Spain, Spain":"Barcelona, Spain",
         "Universitat Fur Angewandte Kunst Wien, Austria":"Vienna, Austria","Nijmegen, Spain":"Malaga, Spain",
         "Liepzig, Germany":"Leipzig, Germany","Říčany, Jažlovice, Czech Republic":"Ricany, Czech Republic",
         "Dijon , Lithuania":"Vilnius, Lithuania", "Hu101, Hungary":"Budapest, Hungary",
         "Madrid, Denmark":"Madrid, Spain", "Irlletterk01, Ireland":"Letterkenny, Ireland",
         "Irllimeric04, Ireland":"Limerick, Ireland","Ταταβανυα, Hungary":"Tatabanya, Hungary",
         "Τενεριφη, Spain":"Tenerife, Spain","06205 Nice Cédex 03, France":"Nice, France",
         "Paris011, France":"Paris, France","Trausnick, Germany":"Krausnick, Germany",
         "Ӧstersund, Sweden":"Östersund, Sweden","Tukholma, Sweden":"Stockholm, Sweden",
         "Lt- 91274 Klaipeda, Lithuania":"Klaipeda, Lithuania","Χαϊδελβεργη, Germany":"Heidelberg, Germany",
         "Λιουμπλιανα, Slovenia":"Ljubljana, Slovenia","Μάλαγα, Spain":"Malaga, Spain","Λισσαβόνα, Portugal":"Lisbon, Portugal",
         "Λημνος, Greece":"Limnos, Greece","Κωνσταντινούπολη, Turkey":"Istanbul, Turkey",
         "Roznov Pod Radhostem, Czech Republic":"Roznov, Czech Republic","Iade, Instituto De Artes Visuais Design E Marketing Sa, Portugal":"Lisbon, Portugal",
         "Cornelia De Liobregat, Spain":"Cornella De Llobregat, Spain","Qvrebo, Norway":"Øvrebo, Norway",
         "Μιλάνο, Italy":"Milano, Italy","Μασσαλια, France":"Marseille, France",
         "Nepcity, Denmark":"Kolding, Denmark","Nepcity, Lithuania":"Vilnius, Lithuania",
         "Nepcity, Finland":"Rauma, Finland", "Satalice, Praha 9, Czech Republic":"Prague, Czech Republic",
         "951672530, Belgium":"Heverlee, Belgium", "Various, Lithuania":"Vilnius, Lithuania",
         "Various, Portugal":"Lisbon, Portugal", "Various, Denmark":"Copenhagen, Denmark",
         "954831626, France":"Nancy, France","956546101, Germany":"Kleve, Germany",
         "960782479, Portugal":"Lisbon, Portugal","Various, Germany":"Berlin, Germany",
         "949708183, Sweden":"Trollhättan, Sweden","Enschede, Denmark":"Aalborg, Denmark","Sveuciliste U Rijeci, Croatia":"Rijeka, Croatia",
         "Enschede, Estonia":"Tallinn, Estonia","997963646, Germany":"Brandenburg, Germany",
         "Enschede, Greece":"Thessaloniki, Greece","Enschedna, Netherlands":"Twente, Netherlands",
         "Székelyudvarhely, Romania":"Odorheiu Secuiesc, Romania","949539500, Croatia":"Zagreb, Croatia",
         "949572383, Spain":"Pozuelo de Alarcon, Spain","949657452, Germany":"Pforzheim, Germany",
         "943245461, Spain":"Valencia, Spain","949083794, Denmark":"Koge, Denmark","Bortonigla, Croatia":"Brtonigla, Croatia",
         "949316982, Belgium":"Antwerpen, Belgium","Sz?Kesfeh?Rv?R, Hungary":"Szekesfehervar, Hungary",
         "Velencia, Spain":"Valencia, Spain","Estocolm, Sweden":"Stockholm, Sweden",
         "999864070, France":"Clermont Ferrand, France","Joensuu, Kuopio, Savonlinne, Finland":"Joensuu, Finland",
         "999650088, Sweden":"Örebro, Sweden","Hermoupolis, Greece":"Ermoupoli, Greece",
         "?Esk? Bud?Jovice, Czech Republic":"Ceske Budejovice, Czech Republic",
         "999986387, Spain":"Barcelona, Spain","Lahanagora, Greece":"Thessaloniki, Greece",
         "Eskilstuna And VÅster?S (Twin Campus), Sweden":"Eskilstuna, Sweden",
         "Munster01, Germany":"Munster, Germany","E10188141, Germany":"Pforzheim, Germany",
         "E10189655, France":"Strasbourg, France","E10199260, Türkiye":"Istanbul, Turkey",
         "E10201956, Norway":"Oslo, Norway","Henningsdorf, Germany":"Hennigsdorf, Germany",
         "E10205342, Austria":"Innsbruck, Austria","E10208607, Germany":"Hamburg, Germany",
         "E10208663, Italy":"Rome, Italy","E10208664, Lithuania":"Kaunas, Lithuania","E10208685, Finland":"Vaasa, Finland",
         "E10208724, Sweden":"Linköping, Sweden","E10208731, Germany":"Köln, Germany","E10208908, Austria":"Graz, Austria",
         "E10187241, Austria":"Wien, Austria","E10175531, Norway":"Oslo, Norway","E10175006, France":"Lyon, France",
         "E10084730, France":"Paris, France","E10158452, Iceland":"Reykjavik, Iceland","Juvaskyla, Finland":"Jyväskylä, Finland",
         "E10209507, Finland":"Helsinki, Finland","E10209488, Netherlands":"Nijmegen, Netherlands",
         "E10209130, Netherlands":"Tilburg, Netherlands","E10209138, Netherlands":"Twente, Netherlands",
         "E10209243, Slovenia":"Ljubljana, Slovenia","E10209381, Norway":"Oslo, Norway","E10209427, Netherlands":"Wagenigen, Netherlands",
         "Mcerata, Italy":"Macerata, Italy","Legraina, Greece":"Legrena, Greece","Pořičí Nad Sázavou, Czech Republic":"Pořičí Nad Sázavou, Czechia",
         "Bátorkeszi, Slovakia":"Batorove Kosihy, Slovakia","EdﾠArnhem, Belgium":"Arnhem, Belgium",
         "Egaleo Postal Code 12241, Athens, Greece":"Athens, Greece","Aschkeim, Germany":"Aschheim, Germany",
         "Ostrava, Záb Eh, Czech Republic":"Ostrava, Czechia","Justrup, Denmark":"Jystrup, Denmark",
         "Irldundalk, Ireland":"Dundalk, Ireland","Karviná-Hranice, Czech Republic":"Karviná, Czechia",
         "Otros, Estonia":"Tallinn, Estonia","Aruküla Small Town, Estonia":"Aruküla, Estonia",
         "Maδριτη, Spain":"Madrid, Spain","Jelgava, Lithuania":"Jelgava, Latvia",
         "Phapos, Cyprus":"Paphos, Cyprus","Argus Vickers Eguity Ownership, United Kingdom":"London, United Kingdom",
         "Jerapetra, Greece":"Ierapetra, Greece","Janské Lázně, Czech Republic":"Janske Lazne, Czechia",
         "Jandia, Pajara, Fuerteventura, Spain":"Jandia, Spain","Kabenhavn, Denmark":"Copenhagen, Denmark",
         "Satul Horodiste, Moldova (Republic of)":"Horodiste, Moldova","Istanbulcan, Turkey":"Istanbul, Turkey",
         "Papendrecht, Belgium":"Papendrecht, Netherlands","Rhetymnon, Greece":"Rethymnon, Greece",
         "Rüsselcheim, Germany":"Rüsselsheim, Germany","Ααρχους, Denmark":"Århus, Denmark",
         "Révkomárom, Slovakia":"Komarno, Slovakia","601 90 Brno, Czech Republic":"Brno, Czech Republic",
         "Laspalmas, Spain":"Las Palmas, Spain","949236666, Spain":"Mondragon, Spain",
         "949313781, Belgium":"Brussels, Belgium","949445313, France":"Paris, France","949482076, Turkey":"Bornova, Turkey",
         "949551819, Denmark":"Copenhagen, Denmark","Lappeenranta, Kuopio, Joensuu, Finland":"Lappeenranta, Finland",
         "941883678, Denmark":"Kolding, Denmark","701 21 Ostrava, Czech Republic":"Ostrava, Czechia",
         "Pamplona, Lithuania":"Vilnius, Lithuania","6289 Sluppen, 7489 Trondheim ,, Norway":"Trondheim, Norway",
         "Ådalsbryk, Norway":"Ådalsbruk, Norway","Äœeskã© Budä›Jovice, Czech Republic":"Ceske Budejovice, Czechia",
         "Ρουμανια, Romania":"Bucharest, Romania","Ροτερνταμ, Netherlands":"Rotterdam, Netherlands",
         "Lykovrissi, Greece":"Lykovrysi, Greece","Paris213, France":"Paris, France","Lv005, Latvia":"Latgale, Latvia",
         "Στουτγάρδης, Germany":"Stuttgart, Germany","Σουηδια, Sweden":"Lund, Sweden",
         "Σμυρνη, Turkey":"Izmir, Turkey","Σλοβακια, Slovakia":"Trnava, Slovakia","Σεβίλλη, Spain":"Sevilla, Spain",
         "Ουτρέχτη, Netherlands":"Utrecht, Netherlands","Παδοβα, Italy":"PAdova, Italy","Lyngbylm, Denmark":"Lyngby, Denmark",
         "Rommetv01, Norway":"Haugesund, Norway","Paris008, France":"Paris, France","Παλερμο, Italy":"Palermo, Italy",
         "Paryžius, France":"Paris, France","Ritz-Carlton Abama Golf & Spa Resort, Spain":"Santa Cruz de Tenerife, Spain",
         "Στουτγκαρδη, Germany":"Stuttgart, Germany","Στουτγκάρδη, Germany":"Stuttgart, Germany",
         "Ltzz, Lithuania":"Klaipeda, Lithuania","Lt00A, Lithuania":"Vilnius, Lithuania",
         "Lt-12142 Vilnius Lietuva, Lithuania":"Vilnius, Lithuania","Louxembourg, Luxembourg":"Luxembourg, Luxembourg",
         "Χαιδελβεργη, Germany":"Heidelberg, Germany","Φλωρεντία, Italy":"Florence, Italy",
         "Νυρεμβεργη, Germany":"Nürnberg, Germany","Ελσίνκι, Finland":"Helsinki, Finland",
         "Maastrcith, Netherlands":"Maastricht, Netherlands","Κρακοβία, Poland":"Cracow, Poland",
         "Κορδοβα, Spain":"Cordoba, Spain","Livorno, Greece":"Glyfada, Greece",
         "Litoměřice, Pokratice, Czech Republic":"Litoměřice, Czechia","200678, Romania":"Craiova, Romania",
         "Limerick, Iceland":"Limerick, Ireland","Βουπερταλ, Germany":"Wuppertal, Germany",
         "Rukantuturi, Finland":"Ruka, Finland","Γένοβα, Italy":"Genoa, Italy","Βρέμη, Germany":"Bremen, Germany",
         "Βουκουρεστη, Romania":"Bucharest, Romania","Βενετια, Italy":"Venice, Italy","Βελιγραδι, Serbia":"Belgrad, Serbia",
         "Μπολονια, Italy":"Bologna, Italy","Μπαρι, Italy":"Bari, Italy","Μεγαλη Βρετανια, United Kingdom":"Chester, United Kingdom",
         "Νυρεμβέργη, Germany":"Nürnberg, Germany","Ντελφτ, Netherlands":"Delft, Netherlands",
         "Rosice U Brna, Czech Republic":"Rosice, Czechia","Νάπολη, Italy":"Napoli, Italy",
         "Llerop, Netherlands":"Lierop, Netherlands","Λεττονια, Latvia":"Riga, Latvia","Λερος, Greece":"Leros, Greece",
         "Λειψια, Germany":"Leipzig, Germany","L’Escala, Spain":"L'Escala, Spain",
         "Ljubljana, Germany":"Ljubljana, Slovenia","Λαιντεν, Netherlands":"Leiden, Netherlands",
         "Λουμπλιανα, Slovenia":"Ljubljana, Slovenia","Λισσαβονα, Portugal":"Lisbon, Portugal",
         "Λιέγη, Belgium":"Liege, Belgium","Rotterdam, Hungary":"Budapest, Hungary",
         "Rigas Juridiska Augstskola, Latvia":"Riga, Latvia","Kodolanyi Janos Foiskola, France":"Szekesfehervar, Hungary",
         "Alcobandas, Spain":"Alcobendas, Spain","Koblencja, Germany":"Koblenz, Germany",
         "Koln01, Germany":"Köln, Germany","Yalysos, Greece":"Ialysos, Greece","Kleinmanchov, Germany":"Kleinmachnow, Germany",
         "Kobenhamman, Denmark":"Copenhagen, Denmark","Klipphausen-Ot Groitzsch, Germany":"Groitzsch, Germany",
         "Akademia Gorniczo-Hutnicza Im. Stanislawa Staszica W Krakowie, Poland":"Krakow, Poland",
         "Kowno, Lithuania":"Kaunas, Lithuania","KrakBurgasW, Poland":"Cracow, Poland",
         "Wyzsza Szkola Jezykow Obcych Im. Samuela Bogumila Lindego, Poland":"Poznan, Poland",
         "Www.Fromm-Automation.Com, Italy":"Verona, Italy","Rathenow Ot Semlin, Germany":"Semlin, Germany",
         "Wroc&#322;Aw&#8203;, Poland":"Wroclaw, Poland","Alingsaa, Sweden":"Alingsås, Sweden",
         "Királyhelmec, Slovakia":"Královsky Chlmec, Slovakia","Kiel01, Germany":"Kiel, Germany",
         "Raunheim, Norway":"Lysaker, Norway", "Aaaaaa, Germany":"Kiel, Germany",
         "Aaaaaa, Poland":"Wroclaw, Poland","Aaaaaa, Portugal":"Lissabon, Portugal",
         "Aaaaaa, Sweden":"Gothenburg, Sweden","Pentafolos, Greece":"Pentalofos, Greece",
         "998686684, Belgium":"Kortrijk, Belgium","993345961, Germany":"Bremen, Germany","994934045, Austria":"Puch Bei Hallein, Austria",
         "996682955, Finland":"Jyväskylä, Finland","997456724, Spain":"Hoyo De Manzanares, Spain",
         "997826391, Portugal":"Coimbra, Portugal","998159392, Austria":"Kufstein, Austria",
         "998929669, France":"Paris, France","Zollikon, Austria":"Zollikon, Switzerland","Malmďż˝, Sweden":"Malmö, Sweden",
         "999489941, France":"Villetaneuse, France","999576465, France":"Avignon, France",
         "999776673, Finland":"Kotka, Finland","999848938, Germany":"Marburg, Germany","999854564, Germany":"Leipzig, Germany",
         "954982461, Norway":"Oslo, Norway","985024428, France":"Mont Saint Aignan, France",
         "986080370, Germany":"Ingolstadt, Germany","Zlin, Spain":"Malaga, Spain",
         "Republic Of Macedonia Goce Delcev State University Stip, The Republic of North Macedonia":"Stip, North Macedonia",
         "?Iauliai, Lithuania":"Siauliai, Lithuania","?Lstykke, Denmark":"Ølstykke, Denmark",
         "Zittau – Ot Pethau, Germany":"Zittau, Germany","999859608, France":"Poitiers, France",
         "999884440, Spain":"Almeria, Spain","999886768, France":"Lille, France","999887156, France":"Tarbes, France",
         "999894916, Portugal":"Porto, Portugal","?Akovec, Croatia":"Cakovec, Croatia",
         "Paguera Calvia Mallorca, Spain":"Peguera, Mallorca, Spain","Zagreb, Hungary":"Zagreb, Croatia",
         "Marianske Lazne, Czech Republic":"Marianske Lazne, Czechia","Zagrebacka Skola Ekonomije I Managementa, Croatia":"Zagreb, Croatia",
         "Paguera,  Calvia,  Mallorca, Spain":"Mallorca, Spain","Ahens, Greece":"Athens, Greece",
         "Agrigento (Tierra Techo Trabajo), Italy":"Agrigento, Italy","LBurgasNeburg, Germany":"Lüneburg, Germany",
         "Abodes, Spain":"Abades, Tenerife, Spain","Adadas, Lithuania":"Vilnius, Lithuania",
         "Active Ideas Foundation, Bulgaria":"Haskovo, Bulgaria","Plze? 2-Slovany, Czech Republic":"Plzen, Czechia",
         "Brno, Stred, Pisárky, Czech Republic":"Brno, Czechia","Vandevoure, France":"Nancy, France",
         "Murnberg, Germany":"Nürnberg, Germany","Pntevedra, Spain":"Pontevedra, Spain","Es70, Spain":"Canary Islands, Spain",
         "Es62, Spain":"Murcia, Spain","Es63, Spain":"Ceuta, Spain","Various, Latvia":"Riga, Latvia",
         "Varsova, Poland":"Warsaw, Poland","Varšuva, Poland":"Warsaw, Poland","Enschede, Poland":"Lodz, Poland",
         "Düsseldorf, Belgium":"Düsseldorf, Germany","E10174122, Finland":"Helsinki, Finland",
         "E10190690, Netherlands":"Groningnen, Netherlands","E10194968, Sweden":"Jönköping, Sweden",
         "E10200255, Austria":"Kufstein, Austria","E10202176, Germany":"München, Germany",
         "E10204863, Portugal":"Lisbon, Portugal","E10208167, Ireland":"Waterford, Ireland",
         "E10208615, Italy":"Ferrara, Italy","E10155097, Austria":"Wels, Austria","E10126199, Netherlands":"Zwolle, Netherlands",
         "E10030187, France":"Roubaix, France","E10084497, France":"Le Havre, France","E10102751, Spain":"Valencia, Spain",
         "E10108600, France":"Montpellier, France","Nook, Greenland":"Nuuk, Greenland",
         "Valasske Mezirici, Czech Republic":"Valasske Mezirici, Czechia","München, Kazakhstan":"Almaty, Kazakhstan",
         "Nordbyhang, Norway":"Nordby, Norway","Byalistok, Poland":"Bialystok, Poland",
         "E10208745, Germany":"Leipzig, Germany","Märjamaa Vald, Raplamaa, Estonia":"Märjamaa, Estonia",
         "Prague 5- Hlubocepy, Czech Republic":"Prague, Czechia","Eglisstaoir, Iceland":"Egilsstaðir, Iceland",
         "E10209437, Sweden":"Uppsala, Sweden","E10209444, Belgium":"Gent, Belgium","E10209504, Italy":"Bologna, Italy",
         "E10209514, Portugal":"Braga, Portugal","E10212965, Germany":"Essen, Germany","E10213059, Netherlands":"Groningen, Netherlands",
         "E10209184, Portugal":"Lisbon, Portugal","E10209186, Spain":"Madrid, Spain","E10209382, Netherlands":"Maastricht, Netherlands",
         "Budimpešta, Hungary":"Budapest, Hungary","Esparta, Greece":"Sparta, Greece","Boedapast, Hungary":"Budapest, Hungary",
         "Flille102, France":"Lille, France","Stanbul, Turkey":"Istanbul, Turkey","Plopsa Indoor Hasselt, Belgium":"Hasselt, Belgium",
         "Stichting Nhtv Internationale Hogeschool Breda, Netherlands":"Breda, Netherlands",
         "Finspong, Sweden":"Finspång, Sweden","Stiftelsen Hogskolan I Jonkoping, Sweden":"Jönköping, Sweden",
         "More For Less Srls, Italy":"Brescia, Italy","Stepanov Nad Svratkou, Czech Republic":"Stepanov Nad Svratkou, Czechia",
         "Frenštát Pod Radhoštěm, Czech Republic":"Frenštát, Czechia","Bizerbuggia, Malta":"Birzebbuga, Malta",
         "Bkara, Malta":"Birkirkara, Malta","Birzebbuga, Greece":"Birzebbuga, Malta",
         "Staatliche Hochschule Für Musik Und Darstellende Kunst Stuttgart, Germany":"Stuttgart, Germany",
         "Staarbrucken, Germany":"Saarbrücken, Germany","Frammi Við Gjónna, Leynavatn, Îles Féroé, Denmark":"Faroe Islands, Denmark",
         "Blomsterladen, Norway":"Blomsterdalen, Norway","Fraulquemont, France":"Faulqemont, France",
         "Frankfurt Nad Menem, Germany":"Frankfurt am Main, Germany","Stromness, Denmark":"Copenhagen, Denmark",
         "Fachhochschule Kärnten, Gemeinnützige Privatstiftung, Austria":"Klagenfurt am Wörthersee, Austria",
         "Nueswtadt-Glewe, Germany":"Neustadt-Glewe, Germany","Stukkard, Germany":"Stuttgart, Germany",
         "Nrnberg, Germany":"Nürnberg, Germany","Mt00, Malta":"Valletta, Malta","Bratislava, Lithuania":"Vilnius, Lithuania",
         "Espoo, Sweden":"Espoo, Finland","European School Of Economics, Ese Insight Ltd, United Kingdom":"London, United Kingdom",
         "Ms. Marijana Federoff, Malta":"Valencia, Spain","Brasov, Spain":"Malaga, Spain",
         "Events Coordination In The Regional Headquarter Of Stryker (Amsterdam), Netherlands":"Amsterdam, Netherlands",
         "Mosfellsbaer, Iceland":"Mosfellsbær, Iceland","Fh Joanneum Gesellschaft Mbh, Austria":"Graz, Austria",
         "Falun And Borlange, Sweden":"Falun, Sweden","Fara Gera D’Adda (Bg), Italy":"Fara Gera d’Adda, Italy",
         "Mougins, Spain":"Grasse, France","Numegen, Netherlands":"Nijmegen, Netherlands","StraTurkuurg, France":"Strasbourg, France",
         "Corradino, Malta":"Valletta, Malta","Cepellen, Luxembourg":"Capellen, Luxembourg",
         "Uham, Germany":"Hamburg, Germany","Cayenne, Spain":"Cayenne, French Guiana",
         "Cbs International Business School, Germany":"Köln, Germany","Cordoba, Ukraine":"Kharkiv, Ukraine",
         "Nearchou 23, Chania , Grecja, Greece":"Chania, Greece","Ullman Dynamics, Gothenburg, Sweden, Sweden":"Gothenburg, Sweden",
         "Tomeloso, Spain":"Tomelloso, Spain","Nepcity, Sweden":"Malmö, Sweden","Nepcity, Ireland":"Blanchardstown, Dublin, Ireland",
         "Nepcity, Hungary":"Budapest, Hungary","Nenerife, Spain":"Tenerife, Spain","Ukl1, Netherlands":"Brabant, Netherlands",
         "Trogstar, Norway":"Trøgstad, Norway","Tullamore, Co. Offaly003535793 23040, Ireland":"Tullamore, Offaly, Ireland",
         "Trondheim, Finland":"Trondheim, Norway","Troisrivières, Canada":"Trois-Rivières, Canada",
         "Ciombra, Portugal":"Coimbra, Portugal","Tromsø_X000B_, Norway":"Tromsø, Norway",
         "Changan Automobile European Designing Center S.R.L.,\xa0Rivoli, Via Simioli, 21, 10098 Rivoli To, Italy, Italy":"Rivoli, Italy",
         "Changan Automobile European Designing Center S.R.L.,?Rivoli, Via Simioli, 21, 10098 Rivoli To, Italy, Italy":"Rivoli, Italy",
         "Coimbra, Poland":"Coimbra, Portugal","Port D'Andratx, Mallorca, Spain":"Mallorca, Spain",
         "Coleraine, Noord-Ierland, United Kingdom":"Coleraine, Nothern Ireland",
         "Uppsala, (Umeå, Alnarp And Skara), Sweden":"Uppsala, Sweden","Doetinchem, Spain":"Marbella, Spain",
         "Terragona, Spain":"Tarragona, Spain","Donauwrth, Germany":"Donauwörth, Germany",
         "Dondoukov Boulevard 54 P.O. Box 37 1504 Sofia, Bulgaria":"Sofia, Bulgaria",
         "Dobrovnik, Croatia":"Dubrovnik, Croatia",'The "Baltazar Adam Krcelic" College Of Business And Management(Cro), Croatia':'Zapresic, Croatia',
         "Unknown, Cyprus":"Nicosia, Cyprus","Unterschleibheim, Germany":"Unterschleißheim, Germany",
         "Tessalonique, Greece":"Thessaloniki, Greece","Tesalonica, Greec":"Thessaloniki, Greece","MǁLaga, Spain":"Malaga, Spain",
         "Bρυξελλες, Belgium":"Brussels, Belgium","Duinkerke, France":"Dunkerque, France",
         "TelemarkRum, Norway":"Telemark, Norway","Dornbirn, France":"Saint-Etienne, France",
         "Dornbirn, Slovakia":"Bratislava, Slovakia","Dornbirn, Spain":"Salamanca, Spain","Nmannheim, Germany":"Mannheim, Germany",
         "Drellinden, Germany":"Dreilinden, Berlin, Germany","No011, Norway":"Oslo, Norway","Dratchen, Netherlands":"Drachten, Netherlands",
         "The General Soft Drinks Co. Ltd, Malta":"Marsa, Malta","Tingsryrd, Sweden":"Tingsryd, Sweden",
         "Universidade Portucalense Infante D Henrique-Cooperativa De Ensino Superior Crl, Portugal":"Porto, Portugal",
         "Pos.Mayskiy, Belgorod Region, Russian Federation":"Mayskiy, Russia","Nijmegen, Belgium":"Nijmegen, Netherlands",
         "Undefined, Croatia":"Zadar, Croatia","Undefined, Denmark":"Århus, Denmark","Castedenolo, Italy":"Castenedolo, Italy",
         "Casteldefels, Spain":"Castelldefels, Spain","Undefined, Norway":"Tromsø, Norway","Undefined, Portugal":"Porto, Portugal",
         "Denham, Ubrix; Middlesex, Ub8 9Ux, United Kingdom":"Denham, United Kingdom",
         "The Provost, Fellows, Foundation Scholars & The Other Members Of Board Of The College Of The Holy & Undivided Trinity Of Queen Elizabeth Near Dublin, Ireland":"Dublin, Ireland",
         "Nijmingen, Netherlands":"Nijmegen, Netherlands","Virezenveen, Netherlands":"Vriezenveen, Netherlands",
         "Oldenburg, Italy":"Cagliari, Italy","Badapest, Hungary":"Budapest, Hungary",
         "Avikilu Kaimas, Liudvinavo Seniunija, Lithuania":"Marijampole, Lithuania",
         "Hradec Nad Moravicí, Czech Republic":"Hradec Nad Moravici, Czechia","Hersonnisos, Greece":"Chersonisos, Greece",
         "Horní Tošanovice, Czech Republic":"Horni Tosanovice, Czechia","Groningen, Poland":"Wroclaw, Poland",
         "Olfsburg, Germany":"Wolfsburg, Germany","Hornbak, Denmark":"Hornbæk, Denmark",
         "Herzogernrath, Germany":"Herzogenrath, Germany","Oldrichov V Hajich, Czech Republic":"Oldrichov v Hajich, Czechia",
         "Vilnius, Liechtenstein":"Vilnius, Lithuania","Vilnius, Greece":"Rhodes, Greece","Benifajo, Spain":"Benifato, Spain",
         "Schönstedt Ot Alterstedt, Germany":"Schönstedt, Germany","Se224, Sweden":"Skåne, Sweden",
         "Oscolano Mnaderno Bs, Italy":"Toscolano Maderno, Italy","Monaco Di Baviera (Germania), Germany":"München, Germany",
         "Soleczniki, Lithuania":"Šalčininkai, Lithuania","Sofiasofia, Bulgaria":"Sofia, Bulgaria","Se-901 87 Umeå, Sweden":"Umeå, Sweden",
         "Midswed, Sweden":"Sundsvall, Sweden","H?Gersten-Liljeholmen, Sweden":"Hägersten-Liljeholmen, Sweden",
         "Hochschule Rhein-Waal-Hsrw Rhine-Waal University Of Applied Sciences, Germany":"Kleve, Germany",
         "Barranco Esquinzo-Buthiondo-Fuerteventura, Spain":"Buthiondo, Fuerteventura, Spain","Volksmarsen, Germany":"Volkmarsen, Germany",
         "Halikidiki, Greece":"CHalkidiki, Greece","Baäÿcä±Lar, Ä°Stanbul, Turkey":"Istanbul, Turkey",
         "Barcelona. World Traded Center Muelle De Barcalona, Edificio Sur, Planta 2, 08039, Barcelona, Spain, Spain":"Barcelona, Spain",
         "Bblingen, Germany":"Böblingen, Germany","Skuodas Region Mosedis, Lithuania":"Mosedis, Lithuania",
         "Groβefehn, Germany":"Aurich, Germany","Bdapest, Hungary":"Budapest, Hungary","Grünzburg, Germany":"Günzburg, Germany",
         "Be21, Belgium":"Antwerp, Belgium","Puntagords, Spain":"Puntagorda, Spain","Olomouc, Spain":"Malaga, Spain",
         "Basilej, Switzerland":"Basel, Switzerland","Baticce, Belgium":"Battice, Belgium",
         "Hielbronn, Germany":"Heilbronn, Germany","Skaelskor, Denmark":"Skælskør, Denmark",
         "Skafidaras, Greece":"Amoudara, Greece","Hinterzarten Am Titisee. Bruderhalde, 21, Germany":"Titisee, Germany",
         "Innsbruck, Croatia":"Split, Croatia","Villabilla, Spain":"Villalbilla, Spain",
         "Bajadoz, Spain":"Badajoz, Spain","Innsbruck, Poland":"Poznan, Poland","Geisenheim, Armenia":"Yerevan, Armenia",
         "Ss. Cyril And Methodius University In Skopje, The Republic of North Macedonia":"Skopje, North Macedonia",
         "Obertsdorf, Germany":"Oberstdorf, Germany","Schawanheide Ot Zweedorf, Germany":"Schwanheide, Germany",
         "Montescudo Montecolombo (Rn), Italy":"Montescudo-Monte Colombo, Italy","Ingolst01, Germany":"Ingolstadt, Germany",
         "Oberusel, Germany":"Oberursel, Germany","Merbella, Spain":"Marbella, Spain","Asterdam, Netherlands":"Amsterdam, Netherlands",
         "Asrhus, Denmark":"Århus, Denmark","Waldershofen, Germany":"Freiburg im Breisgau, Germany","Innsbruck, Turkey":"Ankara, Turkey",
         "Bergenbe, Norway":"Bergen, Norway","WBurgasRzburg, Germany":"Würzburg, Germany","Schwarzenebeck, Germany":"Schwarzenbek, Germany",
         "Schwiederberdingen, Germany":"Schwieberdingen, Germany","Bercellona, Spain":"Barcelona, Spain",
         "Golčův Jeníkov, Czech Republic":"Golcuv Jenikov, Czechia","Schwierberdingen, Germany":"Schwieberdingen, Germany",
         "Pl11, Poland":"Lodz, Poland","Fuerta Ventura Pajara, Spain":"Pajara, Fuertaventura, Spain",
         "Gfggg, Sweden":"Gothenburg, Sweden","Giebelstadt, Norway":"Sande i Vestfold, Norway",
         "Ibs Nemzetközi Üzleti Foiskola, Hungary":"Budapest, Hungary","Icec Play And Learn(Sf), Finland":"Espoo, Finland",
         "Helsinki, Sweden":"Helsinki, Finland","Bagsvaert, Denmark":"Bagsværd, Denmark",
         "Attecife, Spain":"Arrecife, Spain","Iasi, Spain":"Malaga, Spain","Berlin Music Video Awards, Germany":"Berlin, Germany",
         "Plans-Les-Ouates, Switzerland":"Plan-Les-Ouates, Switzerland","Atmelo, Netherlands":"Almelo, Netherlands",
         "Falun And Borl?Nge (Twin Campus), Sweden":"Falun, Sweden","Odense, Kolding, Esbjerg, S?Nderborg And Slagelse, Denmark":"Odense, Denmark",
         "Μαδριτη, Spain":"Madrid, Spain","Βιεννη, Austria":"Vienna, Austria","Maynooth, Ukraine":"Maynooth, Ireland",
         "Kempten02, Germany":"Kempten, Germany","Μιλανο, Italy":"Milano, Italy","Krakow, Spain":"Malaga, Spain",
         "Koln04, Germany":"Köln, Germany","Ultrecht, Netherlands":"Utrecht, Netherlands",
         "Paris009, France":"Paris, France","LeBurgasN, Spain":"Leon, Spain","Es41, Spain":"Avila, Spain",
         "Leiden01, Netherlands":"Leiden, Netherlands","Ee001, Estonia":"Harjumaa, Estonia",
         "Oulu, Spain":"Malaga, Spain",":Železný Brod, Czech Republic":"Železný Brod, Czechia",
         "Σαντιαγκο, Chile":"Santiago de Chile, Chile","Leposavic, Ukraine":"Poltava, Ukraine",
         "Αμμαν, Jordan":"Amman, Jordan","Quakenbrck, Germany":"Quakenbrück, Germany","Port D' Andratx (Mallorca), Spain":"Mallorca, Spain",
         "Rafelbuñol, Spain":"Rafelbunyol, Spain","Piaget, Belgium":"Brussels, Belgium","Risskov06, Denmark":"Aarhus, Denmark",
         "Pontypridd, Italy":"Lecce, Italy","Radolfszell, Germany":"Radolfzell, Germany",
         "Portal 3B, Piso 3A,, Spain":"Madrid, Spain","Pforzheim, Austria":"Innsbruck, Austria",
         "Phaphos, Cyprus":"Paphos, Cyprus","Pharnafluidics, Belgium":"Zwijnaard, Belgium",
         "Rijswijk, Greece":"Rijswijk, Netherlands","Postfach 601553, 14415 Potsdam, Germany":"Potsdam, Germany",
         "Rennes, Denmark":"Copenhagen, Denmark","Praha-Vr�Ovice, Czech Republic":"Praha-Vrsovice, Czechia",
         "R. Da Cal�Ada Fonte Lameiro, 10 6200-358 Covilha, Portugal":"Covilha, Portugal"
         }

# fix place names for mobilities with 2 or more flows
for old, new in udict.items():
    
    # replace
    unloc['origin2'] = unloc['origin2'].str.replace(old, new, regex=False)
    

# get initial value for iterations
n_iter = 1
print('[INFO] - Starting to geocode...')

# keep tabs on unsuccesfull geocodes
unsuc = []

# geocode
for i, row in unloc.iterrows():
    if n_iter != 25:
        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)
        
        try:            
            # get geocoded address
            unloc.at[i, 'gc_address'] = geocoded.address
            
            # save latitude and longitude
            unloc.at[i, 'y'] = geocoded.latitude
            unloc.at[i, 'x'] = geocoded.longitude
            
            #update
            n_iter += 1
        except:
            
            # append list
            unsuc.append(row)
            
            # fill in empty
            unloc.at[i, 'gc_address'] = 'UNSUCCESSFUL'
            
            # save latitude and longitude
            unloc.at[i, 'y'] = None
            unloc.at[i, 'x'] = None
            
            #update
            n_iter += 1
        
    elif n_iter == 25:
        
        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)
        
        try:            
            # get geocoded address
            unloc.at[i, 'gc_address'] = geocoded.address
            
            # save latitude and longitude
            unloc.at[i, 'y'] = geocoded.latitude
            unloc.at[i, 'x'] = geocoded.longitude
            
            #update
            n_iter += 1
        except:
            
            # append list
            unsuc.append(row)
            
            # fill in empty
            unloc.at[i, 'gc_address'] = 'UNSUCCESSFUL'
            
            # save latitude and longitude
            unloc.at[i, 'y'] = None
            unloc.at[i, 'x'] = None
            
            #update
            n_iter += 1
        
        # 1-indexed iterator
        current_i = i + 1
        
        # print progress
        print('[INFO] - Geocoding progress ' + str(current_i) + '/' + str(len(unloc)))
        
        # save progress
        unloc.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_2014-2022_fixed_locations_intermediate_2.pkl')
        
        # wait
        time.sleep(random.randint(40,60))
        
        # reset n_iter
        n_iter = 1

# drop origin2
unloc_res = unloc[['origin', 'count', 'gc_address', 'y', 'x']]

# save better fixed locations
unloc_res.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_2014-2022_fixed_locations.pkl')

# separate unsuccesfuls
unloc_res_u = unloc_res[unloc_res['x'].isna()]
unloc_res_s = unloc_res[~unloc_res['x'].isna()]

# read in Oula's corrections
oula = pd.read_excel("/home/tuomvais/GIS/MOBI-TWIN/Erasmus/Unsuccessfuls_geocoded_ALL_DONE.xlsx",
                     converters={'origin':str, 'count':int, 'gc_address':str, 'y':float, 'x':float})
oula = oula[['origin', 'count', 'gc_address', 'y', 'x']]

# update unsuccesfully corrected geocodes with manually checked geocodes
up_unsuc = pd.merge(unloc_res_u[['origin']], oula, on='origin', how='left')
up_unsuc = up_unsuc[['origin', 'count', 'gc_address', 'y', 'x']]

# get error rows
up_unsuc_errors = up_unsuc[up_unsuc['origin2'].isna()]

# dictionary for some final corrections
fincor = {"Zakhyntos, Greece":"Zakynthos, Greece","Tullamore, Co. Offaly003535793 23040, Ireland":"Tullamore Bypass, Tullamore, Ireland",
          "Rennes (Hq), Barcellona (Mobility, Spain":"Barcelona, Spain","Puerto De Alcudia, Mallorca, Spain":"Port D'Alcúdia, Spain",
          "Puerto De Andratx Mallorca, Spain":"Port D'Andratx, Spain","Puerto Del Rosario, Fuerteventura, Kanarski Otoki, Spain":"Puerto del Rosario, Las Palmas, Spain",
          "Rdanyola Del Vallès (Bellaterra), Spain":"Cerdanyola del Vallès, Spain","Puerto De Alcudia (Mallorca), Spain":"Port D'Alcúdia, Spain",
          "Reichesdorf, Austria":"Richis, Romania","Průhonice, Τσεχικη Δημοκρατια, Czech Republic":"Průhonice, Czechia",
          "Psychiatric Hospital St. Norbertus, Belgium":"Antwerp, Belgium","Psichiko 154 52, Grécia, Greece":"Psichiko, Greece",
          "Riana, Tunisia":"ARiana, Tunisia","Pädaste Village, Muhu Parish, Estonia":"Pädaste, Estonia",
          "Pecsna, Hungary":"Pecs, Hungary","Ribesalves, Spain":"Ribesalbes, Spain","Pulheim, Austria":"Pulheim, Germany",
          "Praha 10, Hostiva?, Czech Republic":"Praha 10, Hostivar, Czechia","Prague 6, Lysolaje, Czech Republic":"Praha 6, Lysolaje, Czechia",
          "Rfh-Koeln Ggmbh, Germany":"Köln, Germany","Poho?Elice, Czech Republic":"Pohorelice, Czechia",
          "Urbanstra�E 116, 10967 Berlin, Germany, Germany":"Urbanstrasse 116, 10967 Berlin, Germany",
          "Urb. Los Vergeles, Granada, Spain":"Granada, Spain","Uxelles, Belgium":"Brussels, Belgium",
          "Uuemõisa, Ridala Vald, Estonia":"Uuemõisa, Estonia","Vagivere K�Lla Lihula Vald, Estonia":"Vagivere Küla, Estonia",
          "Vagivere Külla Lihula Vald, Estonia":"Vagivere küla, Estonia","Ucph, Denmark":"Copenhagen, Denmark",
          "Uantwerpen, Belgium":"Antwerp, Belgium","Velk� Ho�Tice, Czech Republic":"Horice, Czechia",
          "Velden Am W�Rthersee, Austria":"Velden Am Wörthersee, Austria"
          }



# initialize geocoder
geolocator = Nominatim(user_agent='FINAL_SET_V1')

# set up rate limiter
geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# duplicate origins for unlocs for fixing
up_unsuc_errors['origin2'] = up_unsuc_errors['origin']

# fix place names for mobilities with 2 or more flows
for old, new in fincor.items():
    
    # replace
    up_unsuc_errors['origin2'] = up_unsuc_errors['origin2'].str.replace(old, new, regex=False)

# get initial value for iterations
n_iter = 1
print('[INFO] - Starting to geocode with Nominatim...')

# keep tabs on unsuccesfull geocodes
unsuc2 = []

# geocode
for i, row in up_unsuc_errors.iterrows():
    if n_iter != 25:
        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)
        
        try:            
            # get geocoded address
            up_unsuc_errors.at[i, 'gc_address'] = geocoded.address
            
            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = geocoded.latitude
            up_unsuc_errors.at[i, 'x'] = geocoded.longitude
            
            #update
            n_iter += 1
        except:
            
            # append list
            unsuc2.append(row)
            
            # fill in empty
            up_unsuc_errors.at[i, 'gc_address'] = 'UNSUCCESSFUL'
            
            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = None
            up_unsuc_errors.at[i, 'x'] = None
            
            #update
            n_iter += 1
        
    elif n_iter == 25:
        
        # geocode location
        geocoded = geolocator.geocode(row['origin2'], timeout=120)
        
        try:            
            # get geocoded address
            up_unsuc_errors.at[i, 'gc_address'] = geocoded.address
            
            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = geocoded.latitude
            up_unsuc_errors.at[i, 'x'] = geocoded.longitude
            
            #update
            n_iter += 1
        except:
            
            # append list
            unsuc2.append(row)
            
            # fill in empty
            up_unsuc_errors.at[i, 'gc_address'] = 'UNSUCCESSFUL'
            
            # save latitude and longitude
            up_unsuc_errors.at[i, 'y'] = None
            up_unsuc_errors.at[i, 'x'] = None
            
            #update
            n_iter += 1
        
        # 1-indexed iterator
        current_i = i + 1
        
        # print progress
        print('[INFO] - Geocoding progress ' + str(current_i) + '/' + str(len(up_unsuc_errors)))
        
        # save progress
        up_unsuc_errors.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_2014-2022_fixed_nominatims_locations_intermediate_2.pkl')
        
        # wait
        time.sleep(random.randint(40,60))
        
        # reset n_iter
        n_iter = 1

# columns to use in result
rescols = ['origin', 'count', 'gc_address', 'y', 'x']

# join together
result = pd.concat([success[rescols], unloc_res_s[rescols], up_unsuc_errors[rescols]],
                   ignore_index=True).sort_values(['count'], ascending=False).reset_index(drop=True)

# save
result.to_pickle('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_2014-2022_placenames_539_missing.pkl')

# combine with original
combined

# join together
result = pd.concat([unloc_res, success, oula], ignore_index=True).sort_values(['count'], ascending=False).reset_index(drop=True)

# drop unsuccesfull
result = result.dropna(subset=['x']).reset_index(drop=True)

# force datatypes to float for x and y
result['x'] = pd.to_numeric(result['x'])
result['y'] = pd.to_numeric(result['y'])

## convert to geodataframe
print('[INFO] - Turning geocoded locations into a GeoDataFrame..')
result = gpd.GeoDataFrame(result, geometry=gpd.points_from_xy(result['x'], result['y']), crs='EPSG:4326')
result.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_2014-2022_fixed_locations_539missing.gpkg', driver='GPKG')
print('[INFO] - Saved result to geopackage..')

# convert to geodataframe
print('[INFO] - Turning geocoded locations into a GeoDataFrame..')
result = gpd.GeoDataFrame(locations, geometry=gpd.points_from_xy(locations['x'], locations['y']), crs='EPSG:4326')
result.to_file('/home/tuomvais/GIS/MOBI-TWIN/Erasmus/geocoded_locations.gpkg', driver='GPKG')
print('[INFO] - Saved result to geopackage..')

# get short-term mobility
short = df[df['Mobility Duration'] < 330]
long = df[df['Mobility Duration'] >= 330]
