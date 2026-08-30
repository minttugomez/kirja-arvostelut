# Kirja-arvostelut

Tämä sovellus on tarkoitettu kirja-arvosteluiden jakamiseen. Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan omia kirja-arvosteluitaan ja sen lisäksi lukemaan vapaasti muiden kirjoittamia arvosteluita.

Sovelluksen toteuttamiseen on käytetty Claude-kielimallia apukätenä, mutta jokainen muutos ja toiminnallisuus on itse tarkastettu.

## Sovelluksen toiminnot

- [x] Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
- [x] Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kirja-arvosteluja
- [x] Käyttäjä näkee sovellukseen lisätyt kirja-arvostelut
- [x] Käyttäjä pystyy etsimään kirja-arvosteluja hakusanalla
- [x] Sovelluksessa on käyttäjäsivu, joka näyttää tilastoja ja käyttäjän lisäämät kirja-arvostelut
- [ ] Käyttäjä pystyy valitsemaan kirja-arvostelulle yhden tai useamman luokittelun
- [ ] Käyttäjä pystyy kommentoimaan kirja-arvosteluja

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
