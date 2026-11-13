# PSP-project
# SplitPay

**SplitPay** – išlaidų dalijimosi programa, skirta grupių išlaidoms registruoti, automatiškai apskaičiuoti kiekvieno nario dalį ir nustatyti tarpusavio skolas.

Projektas sukurtas kaip veikiantis programos prototipas, naudojant Python, FastAPI, SQLite ir Bootstrap.

## 1. Pagrindinės funkcijos

- Vartotojų registracija ir prisijungimas.
- Asmeninių paskyrų valdymas.
- Vartotojų pridėjimas prie paskyros.
- Grupių kūrimas ir narių pasirinkimas.
- Automatinis grupės kūrėjo įtraukimas į grupę.
- Bendrų išlaidų registravimas.
- Automatinis išlaidų padalijimas grupės nariams.
- Balansų ir tarpusavio skolų apskaičiavimas.
- Grupės išlaidų ištrynimas.
- Skirtingų paskyrų duomenų izoliavimas.

## 2. Naudojamos technologijos

| Technologija | Paskirtis |
|---|---|
| Python | Programavimo kalba |
| FastAPI | Backend ir REST API |
| SQLAlchemy | Duomenų bazės valdymas |
| SQLite | Duomenų saugojimas |
| HTML | Vartotojo sąsajos struktūra |
| CSS | Vartotojo sąsajos stilius |
| Bootstrap | Vartotojo sąsajos komponentai |
| JavaScript | Frontend funkcionalumas |
| Pytest | Automatiniai testai |

## 3. Programos paleidimas

### 3.1. Virtualios aplinkos sukūrimas

### 3.2. Bibliotekų įdiegimas

```powershell
python -m pip install python-multipart itsdangerous
python -m pip install fastapi uvicorn sqlalchemy pydantic "pwdlib[argon2]" itsdangerous
python -m pip install uvicorn
python -m pip install jinja2
$env:SPLITPAY_SESSION_SECRET = python -c "import secrets; print(secrets.token_urlsafe(32))"
python -m pip install pytest
python -m pip install httpx2
```

### 3.3. Serverio paleidimas

```powershell
python -m uvicorn app.main:app --reload
```

Programą galima atidaryti naršyklėje:

http://127.0.0.1:8000

FastAPI API dokumentacija:

http://127.0.0.1:8000/docs

## 4. Programos naudojimas

1. Užregistruojama nauja paskyra, nurodant vartotojo vardą, vardą, pavardę ir slaptažodį.
2. Prisijungiama prie sukurtos paskyros.
3. Pridedami vartotojai, su kuriais bus dalijamasi išlaidomis.
4. Sukuriama grupė, pasirenkant jos narius.
5. Registruojama išlaida, nurodant sumą ir ją apmokėjusį asmenį.
6. Programa automatiškai padalija išlaidą grupės nariams.
7. Balansų skiltyje pateikiama, kiek kiekvienas narys sumokėjo, kiek jam priklauso mokėti ir kokios yra tarpusavio skolos.

## 5. Taisyklės

- Grupę gali sudaryti ne mažiau kaip du nariai.
- Grupės kūrėjas automatiškai įtraukiamas į grupę.
- Išlaidos suma turi būti didesnė už nulį.
- Išlaidas gali apmokėti tik grupei priklausantis vartotojas.
- Išlaidos dalijamos visiems grupės nariams.
- Skaičiavimai atliekami centų tikslumu.
- Kai suma nesidalija po lygiai, likę centai paskirstomi nariams paeiliui.
- Viena paskyra negali pasiekti kitos paskyros grupių ir išlaidų.

## 6. Automatiniai testai

Projekte naudojama **Pytest** testavimo sistema.

Sukurti keturi automatiniai testai:

| Testas | Tikrinamas scenarijus |
|---|---|
| `test_normal_expense.py` | Įprastas išlaidų padalijimas |
| `test_boundary_expense.py` | Ribinis atvejis, kai suma nesidalija centų tikslumu |
| `test_invalid_expense.py` | Klaidos atvejis su neigiama išlaidos suma |
| `test_account_isolation.py` | Skirtingų paskyrų duomenų izoliavimas |

### Testų paleidimas

```powershell
python -m pytest -v
```

## 7. Projekto architektūra

Programa suskirstyta į atskirus sluoksnius:

- **Routers** – priima HTTP užklausas ir pateikia atsakymus.
- **Services** – vykdo išlaidų dalijimo ir balansų skaičiavimo logiką.
- **Models** – aprašo duomenų bazės lenteles ir jų ryšius.
- **Schemas** – aprašo API duomenų struktūras.
- **Frontend** – pateikia vartotojo sąsają.
- **Tests** – automatiškai tikrina pagrindinius programos scenarijus.

Tokia struktūra padeda atskirti programos atsakomybes ir palengvina kodo priežiūrą, peržiūrą bei testavimą.
