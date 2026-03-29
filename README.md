# Kirja-arvostelut

## Sovelluksen toiminnot

- [x] Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
- [ ] Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kirja-arvosteluja
- [x] Käyttäjä näkee sovellukseen lisätyt kirja-arvostelut
- [ ] Käyttäjä pystyy etsimään kirja-arvosteluja hakusanalla
- [ ] Sovelluksessa on käyttäjäsivu, joka näyttää tilastoja ja käyttäjän lisäämät kirja-arvostelut
- [ ] Käyttäjä pystyy valitsemaan kirja-arvostelulle yhden tai useamman luokittelun
- [ ] Käyttäjä pystyy kommentoimaan kirja-arvosteluja

## Sovelluksen asennus

1. Asenna `flask`-kirjasto:
```bash
$ pip install flask
```

2. Luo tietokannan taulut:
```bash
$ sqlite3 database.db < sql/schema.sql
```

3. Sovelluksen käynnistys:
```bash
$ flask run
```
