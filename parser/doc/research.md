### Wybór parser pdf

[PyMuPDF](https://github.com/pymupdf/PyMuPDF): Rekomendowany przez panią i posiada dobre wyniki w [benchmark'ach](https://github.com/py-pdf/benchmarks)  
Aktywnie developowany i ma ładną dokumentacje [Link](https://pymupdf.readthedocs.io/en/latest)


### Pasowanie odf vs docx

Wiadomo, że odf > docx, ale biblioteki pythona do odf są o wiele mniej popularne niż dla docx,  
dlatego bezpiecznień wybrać docx.

Przetestowaliśmy kilka różnych bibliotek umożliwiających odczytanie tekstu z plików DOCX.

#### python-docx

Najpopularniejszą biblioteką, która zapewnia podstawową obsługę plików DOCX 
w Pythonie jest [python-docx](https://github.com/python-openxml/python-docx/tree/master).
Umożliwia ona m.in. odczytanie tekstu z akapitów oraz tabel, z czym owa biblioteka poradziła sobie dobrze.
Duża część testowanych przez nas przykładowych CV zamiast standardowych akapitów używa jednak 
swobodnie przemieszczalnych pól tekstowych, których python-docx [nie obsługuje](https://github.com/python-openxml/python-docx/issues/413). 
W efekcie tego przy próbie sparsowania pliku otrzymujemy puste wejście. 

#### docx_parser

Alternatywą mógłby być [docx_parser](https://github.com/suqingdong/docx_parser/tree/master), jednak w testach dawał wyniki 
jeszcze gorsze od wcześniej opisanego python-docx. Biblioteka wygląda na niedokończoną oraz przeznaczoną bardziej 
do celów eksperymentalnych.

#### docx2txt

Biblioteka [docx2txt](https://github.com/ankushshah89/python-docx2txt) jest zbudowana na bazie python-docx 
oraz obiecuje wydobywanie tekstu dodatkowo z nagłówków, stopki i hiperlinków. W praktyce okazało się, 
że udało się odczytać tekst także z pól tekstowych. Jednak efektem ubocznym był fakt, że tekst z każdego z pól tekstowych 
powtarzał się dwukrotnie. Można jednak sobie z tym w dużej mierze poradzić na etapie post-processingu. 
Narzędzie zapewniło zadowalający wynik oraz wyodrębniło cały tekst z każdego CV.

#### PyMuPDF

Chociaż w niekomercyjnej wersji format DOCX teoretycznie nie jest wspierany, w praktyce jego parsowanie jest możliwe
poprzez moduł XML. Wyniki były bardzo zbliżone do docx2txt, chociaż końcowe formatowanie nieco się różniło. 
Ostatecznie wygoda podczas używania tylko jednej biblioteki do wyodrębniania tekstu zamiast dwóch różnych oraz 
wystarczająca skuteczność zadecydowały, że do DOCX PyMuPDF okazał się być najlepszym wyborem.

#### PyMuPDF Pro

Komercyjna wersja PyMuPDF zapewnia obsługę plików Office Open XML, w tym DOCX. Chociaż jest płatna, możliwe jest 
również użycie biblioteki bez zakupionej licencji - w tym przypadku nałożone jest ograniczenie, uniemożliwiające 
przetworzenie więcej niż 3 stron dla jednego dokumentu. CV składa się zazwyczaj tylko z 1 strony, także nie jest to dla nas 
problemem. Chociaż wynikowy tekst nie zawiera powtórzonego tekstu z każdego pola, wersja Pro usilnie próbuje rozmieszczać 
cały tekst zgodnie z oryginalnym rozmieszczeniem pól tekstowych. Mieliśmy również problem z ucinaniem tekstu w niektórych
fragmentach dokumentu, zwłaszcza przy narysowanych kształtach czy obrazkach - trudno zatem zaufać w 100% temu rozwiązaniu. 
Ostatecznie PyMuPDF Pro bierzemy pod uwagę jako opcję zapasową.
