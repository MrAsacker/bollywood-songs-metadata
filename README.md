
# 🎶 Bollywood Songs & Albums Metadata Dataset (1931–2025)

[![Dataset](https://img.shields.io/badge/Dataset-Bollywood-blueviolet)](#)
[![Years](https://img.shields.io/badge/Years-1931–2025-success)](#)
[![Format](https://img.shields.io/badge/Format-CSV-orange)](#)
[![UUID](https://img.shields.io/badge/UUID-UUIDv5-blue)](#)
[![License](https://img.shields.io/badge/license-MIT-red)](#)

A **comprehensive, structured, and reproducible metadata dataset** of Bollywood film albums and songs spanning **over 90 years (1931–2025)**.

This dataset is designed for:
- 🎧 Music information retrieval
- 📊 Data analysis & visualization
- 🤖 Machine learning & recommendation systems
- 🧠 Digital humanities & cultural research
- 🏗️ Scalable music databases

---

## 📌 Dataset Overview

| Category | Count |
|--------|------:|
| 🎞️ Albums | **12,673** |
| 🎵 Songs | **57,005** |
| 📅 Year Range | **1931 – 2025** |
| 📁 Format | CSV |
| 🔑 Identifiers | Deterministic UUIDv5 |
| 🔁 De-duplication | Yes (content-based) |

---

## 📝 Data Dictionary

Detailed schema for the CSV files found in `data/raw/`.

### 1. Albums Schema (`albums.csv`)

Each row represents a unique film soundtrack or album.

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `album_uuid` | `string` | **Primary Key**. Deterministic UUIDv5 generated from title + year. | `a3f9...` |
| `album_title` | `string` | Normalized title of the film/album. | `Sholay` |
| `album_year` | `int` | Release year of the album. | `1975` |
| `music_director` | `string` | Primary composer(s) of the album. | `R.D. Burman` |
| `label` | `string` | Music label (e.g., T-Series, Saregama), if available. | `Polydor` |
| `album_url` | `string` | Source URL for the album metadata. | `https://myswar...` |

### 2. Songs Schema (`songs.csv`)

Each row represents a unique track within an album.

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `song_uuid` | `string` | **Primary Key**. Deterministic UUIDv5 generated from album + track + title. | `c1b2...` |
| `album_uuid` | `string` | **Foreign Key**. Links to the parent Album. | `a3f9...` |
| `track_number` | `int` | Sequential order of the song in the album. | `1` |
| `song_title` | `string` | Title of the track. | `Mehbooba Mehbooba` |
| `singers` | `string` | Comma-separated list of singers. | `R.D. Burman` |
| `1 youtube_url` | `string` | Direct link to the official music video or audio. | `https://youtu.be/...` |
| `3 yt_music_urls`| `string` | Direct link to the official music track | `https://music.youtube.com/watch?v=.....`|

## 🗂️ Dataset Structure
```

data/
├── raw/
│   ├── albums/
│   │   ├── albums_1931_1944.csv
│   │   ├── albums_1945_1954.csv
│   │   ├── ...
│   │   └── albums_2015_2025.csv
│   └── songs/
│       ├── songs_1931_1944.csv
│       ├── songs_1945_1954_completed.csv
│       ├── ...
│       └── songs_2015_2025.csv

```
## 📊 Verified Record Counts

### 💿 Albums (12,673 total)

| Period | Albums |
|------|-------:|
| 1931–1944 | 387 |
| 1945–1954 | 1,066 |
| 1955–1964 | 1,058 |
| 1965–1974 | 1,079 |
| 1975–1984 | 1,173 |
| 1985–1994 | 1,245 |
| 1995–2004 | 1,127 |
| 2005–2014 | 1,551 |
| 2015–2025 | 3,987 |

---

### 🎵 Songs (57,005 total)

| Period | Songs |
|------|------:|
| 1931–1944 | 1,606 |
| 1945–1954 | 6,507 |
| 1955–1964 | 6,757 |
| 1965–1974 | 5,411 |
| 1975–1984 | 5,950 |
| 1985–1994 | 6,862 |
| 1995–2004 | 6,248 |
| 2005–2014 | 8,191 |
| 2015–2025 | 9,473 |

---

## 🧬 Deterministic UUID Design (UUIDv5)

This dataset uses **UUID version 5** to ensure **stable, repeatable, and collision-free identifiers** across re-scrapes and future updates.

---

### 💿 Album UUID Generation

Each album UUID is generated from a **normalized, human-readable album identity**.

#### Inputs
- `album_title`
- `album_year`

```python
unique_album_string = f"{album_title}_{album_year}".lower().strip()
album_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, unique_album_string)
````

#### Why this works

* Same album title + year → **same UUID forever**
* Prevents duplicate albums across re-scrapes
* Stable primary key for joins, updates, and merges
* Human-explainable identity source

---

### 🎵 Song UUID Generation

Each song UUID is generated **relative to its parent album**, ensuring correct hierarchy and uniqueness.

#### Inputs

* `album_uuid` (parent)
* `track_number`
* `song_title`

```python
unique_song_string = f"{album_uuid}_{track_number}_{song_title}".lower().strip()
song_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, unique_song_string)
```

#### Why this works

* Same album + track + title → **same song UUID**
* Allows identical song titles across different albums
* Enforces album → song referential integrity
* Ideal for relational databases and graph models

---

## 🧠 Relational Model

```
Album (album_uuid)
 ├── album_title
 ├── album_year
 ├── music_director
 └── label
        │
        └── Song (song_uuid)
            ├── track_number
            ├── song_title
            ├── singers
            └── youtube_url
```



---

## 🧪 Example Use Cases

* 🎼 Music recommendation engines
* 📈 Trend analysis across decades
* 🎤 Singer & composer network graphs
* 🤖 ML training datasets
* 🗃️ Music archival systems

---

## 📦 Kaggle & HuggingFace Ready

* Flat CSV files
* Stable UUID primary keys
* Clear schema
* Deterministic regeneration
* Version-friendly structure

Perfect for:

* Kaggle Datasets
* HuggingFace `datasets`
* BigQuery / DuckDB / Postgres imports

---

## 📖 Cite This Dataset

If you use this dataset in research, projects, or publications, please cite it as:

```bibtex
@dataset{bollywood_metadata_1931_2025,
  title   = {Bollywood Songs and Albums Metadata Dataset (1931--2025)},
  author  = {Asacker},
  year    = {2026},
  url     = {https://github.com/<your-username>/<your-repo>},
  note    = {12,673 albums and 57,005 songs with deterministic UUIDv5 identifiers}
}
```

---


## ⚖️ License

This project and dataset are released under the **MIT License**.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the dataset and code, subject to the terms of the MIT License.

See the [LICENSE](LICENSE) file for full details.



### **If this dataset helped you, consider giving the repo a ⭐ — it really helps.**

