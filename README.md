```markdown
# 🎵 Bollywood Songs Metadata Dataset

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dataset](https://img.shields.io/badge/dataset-8%20decades-green.svg)]()
[![Maintenance](https://img.shields.io/badge/maintained-yes-success.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

> A comprehensive, structured dataset of Bollywood (Hindi Cinema) songs metadata spanning from 1930s to 2020s, featuring quality ratings, YouTube Music links, and multi-tier filtering for research and application development.

## 🌟 Dataset Highlights

- **📅 Temporal Coverage**: 9 decades (1930s–2020s) of Bollywood music history
- **🎼 Multi-Modal**: Rich metadata including singers, composers, lyricists, ratings, and streaming URLs
- **⚡ Quality-Tiered**: Pre-filtered datasets for high-quality songs (Rating ≥4.0 and ≥4.3)
- **🔗 Streaming Ready**: Curated YouTube Music URLs for direct audio access
- **📊 Research Grade**: UUID-based relational structure linking songs to albums
- **🔓 Open Access**: Free for commercial and non-commercial use

## 📁 Repository Structure

```
bollywood-songs-metadata/
├── 📂 data/
│   ├── 📁 raw/                          # Original scraped data by decade
│   │   ├── 1930s/
│   │   ├── 1940s/
│   │   ├── 1950s/
│   │   ├── 1960s/
│   │   ├── 1970s/
│   │   ├── 1980s/
│   │   ├── 1990s/
│   │   ├── 2000s/
│   │   ├── 2010s/
│   │   └── 2020s/
│   │
│   └── 📁 filtered/                     # Quality-filtered datasets
│       ├── 📂 rating_4.0_plus/          # Good quality (Rating ≥ 4.0/5.0)
│       └── 📂 rating_4.3_plus/          # Excellent quality (Rating ≥ 4.3/5.0)
│
├── 📂 schemas/                          # JSON schema definitions
│   ├── songs_schema.json
│   └── albums_schema.json
│
├── 📂 scraper progs/                    # Data collection scripts
├── 📂 scripts/                          # Validation & processing utilities
└── 📄 README.md                         # This file
```

## 📊 Data Schema

### 🎵 Songs Table (`songs.csv`)
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `song_uuid` | UUIDv4 | Unique identifier | `550e8400-e29b-41d4-a716-446655440000` |
| `album_uuid` | UUIDv4 | Foreign key to album | `6ba7b810-9dad-11d1-80b4-00c04fd430c8` |
| `track_number` | Integer | Position in album | `1`, `2`, `3` |
| `song_title` | String | Song name | *"Dum Maro Dum"* |
| `song_singers` | String | Vocalist(s) | *"Asha Bhosle, R. D. Burman"* |
| `song_rating` | Float (0-5) | Quality rating | `4.5` |
| `youtube_url` | URL | Official video | `https://youtube.com/watch?v=...` |
| `music_yt_url_1` | URL | YouTube Music (Primary) | `https://music.youtube.com/watch?v=...` |
| `music_yt_url_2` | URL | YouTube Music (Alt 1) | Backup link |
| `music_yt_url_3` | URL | YouTube Music (Alt 2) | Backup link |

### 💿 Albums Table (`albums.csv`)
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `album_uuid` | UUIDv4 | Unique identifier | Primary Key |
| `album_title` | String | Movie/Album name | *"Hare Rama Hare Krishna"* |
| `album_year` | Integer | Release year | `1971` |
| `album_category` | String | Type | *"Soundtrack"*, *"Album"*, *"Single"* |
| `album_music_director` | String | Composer | *"R. D. Burman"* |
| `album_lyricist` | String | Songwriter(s) | *"Anand Bakshi"* |
| `album_label` | String | Music label | *"Saregama"*, *"T-Series"* |
| `album_rating` | Float (0-5) | Overall rating | `4.2` |

## 🚀 Quick Start

### Python (Pandas)
```python
import pandas as pd

# Load high-quality songs only (Rating >= 4.3)
df = pd.read_csv('data/filtered/rating_4.3_plus/1970s/tobe_songs_1931_1944_final.csv')

# Find all songs by Kishore Kumar from excellent albums
kishore_classics = df[
    df['song_singers'].str.contains('Kishore Kumar', na=False) &
    (df['song_rating'] >= 4.5)
]

print(f"Found {len(kishore_classics)} classics")
print(kishore_classics[['song_title', 'album_title', 'song_rating']].head())
```

### SQL Analysis
```sql
-- Find top-rated duets from the 1970s
SELECT song_title, album_title, song_singers, song_rating
FROM songs
WHERE song_singers LIKE '%,%'  -- Multiple singers = duet/collaboration
  AND song_rating >= 4.5
ORDER BY song_rating DESC
LIMIT 20;
```

### Loading Album Relationships
```python
# Relational query example
songs = pd.read_csv('data/raw/1970s/songs.csv')
albums = pd.read_csv('data/raw/1970s/albums.csv')

# Join to get full metadata
full_data = songs.merge(
    albums, 
    on='album_uuid', 
    suffixes=('', '_album')
)

# Filter by music director
rd_burman_songs = full_data[
    full_data['album_music_director'] == 'R. D. Burman'
]
```

## 📈 Dataset Statistics

| Metric | Count | Details |
|--------|-------|---------|
| **Total Decades** | 9 | 1930s through 2020s |
| **Quality Tiers** | 3 | Raw, 4.0+, 4.3+ |
| **Schema Version** | 1.0 | UUID-based relational |
| **Update Frequency** | Quarterly | New decades added periodically |

*Statistics update automatically via CI/CD pipeline*

## 🎯 Use Cases

### 🎧 **Music Streaming Applications**
Build playlist generators using `music_yt_url_*` columns for direct audio streaming.

### 🤖 **Machine Learning**
- **Recommendation Systems**: Train on `album_music_director` + `song_rating` patterns
- **Sentiment Analysis**: Correlate `lyricist` with `song_rating` across decades
- **Genre Classification**: Use `album_category` + `album_year` features

### 📊 **Data Visualization**
```python
# Example: Ratings distribution by decade
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('data/merged/all_songs_4.0_plus.csv')
sns.boxplot(data=df, x='decade', y='song_rating')
plt.title('Song Quality Evolution (1940-2020)')
plt.show()
```

### 🎓 **Academic Research**
- Bollywood music evolution studies
- Cultural analytics of playback singing trends
- Network analysis of composer-lyricist-singer relationships



## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Data Quality**: Ensure ratings are from reliable sources (IMDb, Filmfare, or aggregate user ratings)
2. **Schema Compliance**: Run `validate_data.py` before submitting
3. **YouTube Links**: Verify `music_yt_url_*` are official uploads, not user-generated content
4. **Decade Organization**: Place files in appropriate `data/raw/[DECADE]/` folder

### Adding New Songs
1. Fork the repository
2. Add your CSV to the appropriate decade folder
3. Ensure UUIDs are unique (use `uuid.uuid4()`)
4. Validate with provided scripts
5. Submit a Pull Request

## ⚠️ Important Notes

- **Metadata Only**: This dataset contains links and metadata, not audio files. Please respect copyright laws.
- **YouTube Terms**: Usage of `music_yt_url_*` fields must comply with [YouTube's Terms of Service](https://www.youtube.com/t/terms).
- **Rating Source**: Ratings are aggregated from public sources (IMDb, music streaming platforms, critic scores).
- **Data Accuracy**: While we strive for accuracy, verify critical data points before commercial use.

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**You are free to:**
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use privately
- ✅ Sublicense

**Condition:** Attribution required (link back to this repo).

## 🙏 Acknowledgments

- **Data Sources**: IMDb, Wikipedia, Official Music Labels, YouTube Music
- **Community Contributors**: [List contributors here]
- **Inspiration**: The rich musical heritage of Indian Cinema

## 📬 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/MrAsacker/bollywood-songs-metadata/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MrAsacker/bollywood-songs-metadata/discussions)
- **Email**: [your-email@example.com] *(optional)*

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for Bollywood music enthusiasts and data scientists

[Contributors](https://github.com/MrAsacker/bollywood-songs-metadata/graphs/contributors) • [Issues](https://github.com/MrAsacker/bollywood-songs-metadata/issues) • [Pull Requests](https://github.com/MrAsacker/bollywood-songs-metadata/pulls)

</div>
```