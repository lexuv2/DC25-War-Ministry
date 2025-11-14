## API recenzja 2025

### `/cv`
Jeśli chodzi o CV samo w sobie, to może zostać struktura, którą wyodrębnił parser. Natomiast do tego trzeba będzie dołożyć stanowisko, ocenę CV i status aplikacji.

Wtedy `GET /cv` mogłoby zwracać listę tego typu danych:
- imię i nazwisko kandydata - tekst
- stanowisko - tekst
- data wpłynięcia aplikacji - data
- ocena - jak ma być ranking to pewnie liczba
- status - tekst
- ID CV
  
A `GET /cv/{id}` dawałoby pojedynczy obiekt tego samego, ale zamiast ID byłoby całe CV.

Możnaby też było rozbić to API na osobny endpoint dla CV i osobny dla aplikacji, który kierowałby tylko na zasób z CV, ale to wymagałoby więcej zmian, obecna forma powinna wystarczyć.

### `/mails`
Prawdę mówiąc, to nie wiem co metody z `/mails` mają robić. We frontendzie i tak za dużo styczności z mailami chyba nie ma, nie licząc przycisku zaakceptowania bądź odrzucenia kandydata. Tylko, że to powinno też zaktualizować status jego aplikacji i dopiero z tego wynika mail o akceptacji/odrzuceniu.

Także jeśli dobrze rozumiem kryteria to mi obojętne jak będzie działać API dla maili.