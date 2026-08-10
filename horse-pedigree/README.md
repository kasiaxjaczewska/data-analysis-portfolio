# Baza rodowodowa koni półkrwi – Serwis REST

Projekt zaliczeniowo-egzaminacyjny.  
Serwis REST do zarządzania bazą danych rodowodów koni półkrwi.

## Technologie

- **Node.js** + **Express**
- **Knex.js** (query builder)
- **PostgreSQL** (baza danych)
- **Docker** (uruchomienie PostgreSQL)
- **dotenv**

## Funkcjonalności

### Encje
- **Kraje** – kod ISO (2 litery) + nazwa w języku polskim
- **Hodowcy** – nazwa + kraj
- **Maści** (colors)
- **Rasy** (breeds) – kody: `oo`, `xx`, `xo`, `xxoo`
- **Konie** – imię, rasa, data urodzenia, płeć, ojciec, matka, maść, hodowca

### Reguły biznesowe
- Płeć konia: `klacz`, `ogier`, `wałach`
- Ojcem może być tylko **ogier**, matką tylko **klacz**
- Rasa konia:
  - Jeśli nie podano rodziców → można ustawić arbitralnie
  - Jeśli podano rodziców → rasa wyliczana automatycznie według reguł:
    - `oo + oo` → `oo`
    - `oo + xo` → `xo`
    - `oo + xx` → `xxoo`
    - `xx + xx` → `xx`
    - `xx + xo` → `xo`
    - `xx + xxoo` → `xxoo`
    - `xo + xo` → `xo`

### Endpointy

#### Kraje
- `GET /countries`
- `GET /countries/:iso_code`
- `POST /countries`
- `PUT /countries/:iso_code`
- `DELETE /countries/:iso_code`

#### Hodowcy
- `GET /breeders` (opcjonalny filtr `?country_iso_code=`)
- `GET /breeders/:id`
- `POST /breeders`
- `PUT /breeders/:id`
- `DELETE /breeders/:id`

#### Maści
- `GET /colors`
- `GET /colors/:id`
- `POST /colors`
- `PUT /colors/:id`
- `DELETE /colors/:id`

#### Rasy
- `GET /breeds`
- `GET /breeds/:code`
- `POST /breeds`
- `PUT /breeds/:code`
- `DELETE /breeds/:code`

#### Konie
- `GET /horses` (filtry: `breed_code`, `color_id`, `breeder_id`, `gender`, `birth_date_start`, `birth_date_end`)
- `GET /horses/:id`
- `POST /horses`
- `PUT /horses/:id`
- `DELETE /horses/:id`

#### Rodowód i potomstwo
- `GET /rodowod/:id/:depth` – dane rodowodu w formacie JSON (głębokość 1–5)
- `GET /potomstwo/:id` – potomstwo konia (opcjonalne filtry: `?gender=` oraz `?breeder_id=`)
- `GET /wizualizacja-rodowodu/:id/:depth` – wizualizacja rodowodu w HTML (drzewo genealogiczne)