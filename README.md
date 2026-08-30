# Kirja-arvostelut

Tämä sovellus on tarkoitettu kirja-arvosteluiden jakamiseen. Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan omia kirja-arvosteluitaan ja sen lisäksi lukemaan vapaasti muiden kirjoittamia arvosteluita.

Sovelluksen toteuttamiseen on käytetty Claude-kielimallia apukätenä, mutta jokainen muutos ja toiminnallisuus on itse tarkastettu.

## Sovelluksen toiminnot

- [x] Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
- [x] Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kirja-arvosteluja
- [x] Käyttäjä näkee sovellukseen lisätyt kirja-arvostelut
- [x] Käyttäjä pystyy etsimään kirja-arvosteluja hakusanalla
- [x] Sovelluksessa on käyttäjäsivu, joka näyttää tilastoja ja käyttäjän lisäämät kirja-arvostelut
- [x] Käyttäjä pystyy valitsemaan kirja-arvostelulle yhden tai useamman luokittelun
- [x] Käyttäjä pystyy kommentoimaan kirja-arvosteluja

## Sovelluksen asennus

1. Asenna `flask`-kirjasto:
```bash
$ pip install flask
```

2. Luo tietokannan taulut ja lisää luokittelut:
```bash
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

3. Sovelluksen käynnistys:
```bash
$ flask run
```

## Sovelluksen testaus suurella tietomäärällä
Raportti luotu Claude-kielimallin avulla

Tiedostolla `seed.py` voi luoda tietokantaan suuren testiaineiston:

```bash
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
$ python3 seed.py
```

`seed.py` luo 1 000 käyttäjää, 100 000 kirja-arvostelua, noin 200 000
luokitteluriviä ja 1 000 000 kommenttia. Kaikkien testikäyttäjien salasana
on `password` (esim. käyttäjä `user1`).

### Mittaustulokset

Sivujen latausajat mitattiin testiaineistolla (mediaani seitsemästä
pyynnöstä) ennen ja jälkeen tietokantaindeksien lisäämisen. Mittaus tehtiin
erillisellä skriptillä, jota ei ole jätetty koodiin.

| Sivu | Ilman indeksejä | Indeksien kanssa |
|---|---|---|
| Etusivu `/` (sivu 1) | ~21 ms | ~13 ms |
| Haku `/?genre=Horror` | ~61 ms | ~60 ms |
| Käyttäjäsivu `/user/1` | ~40 ms | ~12 ms |
| Arvostelusivu `/review/1` (arvostelu + kommentit) | ~121 ms | ~8 ms |

Suurin hyöty näkyy arvostelusivulla: ilman indeksiä sivun kommenttien haku
käy läpi koko `comments`-taulun (miljoona riviä), ja indeksin kanssa haku on
lähes vakioaikainen. Käyttäjäsivun tilastot ja arvostelulista nopeutuvat
vastaavasti, kun `book_reviews.user_id` on indeksoitu.

### Lisätyt indeksit (`schema.sql`)

```sql
CREATE INDEX idx_book_reviews_user_id ON book_reviews (user_id);
CREATE INDEX idx_review_classes_review_id ON review_classes (review_id);
CREATE INDEX idx_review_classes_value ON review_classes (value);
CREATE INDEX idx_comments_review_id ON comments (review_id);
```

`EXPLAIN QUERY PLAN` vahvistaa, että kyselyt käyttävät indeksejä
(`SEARCH ... USING INDEX ...` koko taulun läpikäynnin sijaan).

### Sivutus

Etusivulla ja käyttäjäsivulla näytetään 10 arvostelua kerrallaan
(`LIMIT` ja `OFFSET`). Sivua vaihdetaan osoitteen `?page=`-parametrilla, ja
edellinen/seuraava-linkit näkyvät listan alla. Virheelliset sivunumerot
ohjataan ensimmäiselle tai viimeiselle sivulle.
