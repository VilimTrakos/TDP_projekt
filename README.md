# Upute za Postavljanje i Pokretanje Sustava

## Priprema
Prije svega, potrebno je imati instaliran **Docker Desktop**.

## Potrebne Biblioteke

Prije pokretanja projekta, instalirajte potrebne biblioteke koristeći sljedeće naredbe:
```bash
pip install couchdb
pip install cryptography
pip install requests
pip install tkcalendar
pip install tk
```

## Pokretanje Baze Podataka i Testiranje

1. Otvorite terminal u **Visual Studio Code-u** ili običan terminal.
2. Pozicionirajte se u direktorij u kojem se nalazi projekt.
3. Pokrenite naredbu:
   ```bash
   docker-compose up -d
   ```
   Ova naredba pokreće postavljanje baza podataka.
4. Pričekajte 30-40 sekundi da se baze podataka postave i uspostavi njihova replikacija.
5. Test replikacije izvršit će se automatski pomoću skripte:
   ```bash
   ./init-replication.sh
   ```

## Postavljanje Ključeva za Kriptiranje i Dekriptiranje

1. Potrebno je generirati tri ključa pomoću skripte `key-generator.py`.
2. Pokrenite skriptu i generirani tekst zalijepite u terminal. Na primjer:
   ```bash
   $env:ENCRYPTION_KEY_SHARED= "ZQkdQtWqr_Wtdw8mEtF5sABy0Ava0q5fDZUw0c0zh_M="
   ```

## Dodavanje Pacijenata

Pacijente je moguće dodati na dva načina:

### 1. GUI Način
Pokrenite skriptu:
```bash
python .\add_patient.py
```

### 2. Terminal Način
Pokrenite skriptu s potrebnim parametrima. Primjer:
```bash
python add_patient.py --terminal --first_name "Emily" --last_name "Martin" --oib "01234567890" --dob "2002-06-18" --gender "Female" --email "emily.martin@example.com" --baza Osijek
```

## Dodavanje Doktora i Osoblja

1. Pokrenite skriptu `add_user.py` koristeći GUI:
   ```bash
   python .\add_user.py
   ```
2. Unutar GUI-a vidjet ćete popis pacijenata. Možete odabrati jednog ili više pacijenata za dodavanje doktora ili osoblja.
   - Za odabir više pacijenata držite **Ctrl** i kliknite lijevim gumbom miša na željene pacijente.

## Pokretanje Aplikacije za Prijavu

1. Nakon što su dodani doktori i osoblje, pokrenite aplikaciju za prijavu:
   ```bash
   python .\login.py
   ```
2. Prijavite se pomoću podataka kreiranog korisnika i odaberite bazu na koju se želite povezati.

