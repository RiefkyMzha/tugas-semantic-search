# Semantic Search & Vector Database

## Project Information

**Nama Project:**

Semantic Search Buku

**Tema Dataset:**

Buku dan deskripsi buku (Open Library Works With Descriptions)

**Deskripsi Singkat:**

Aplikasi semantic search yang mengambil deskripsi buku sebagai sumber dokumen, mengubah dokumen dan kueri pengguna menjadi embedding menggunakan model SentenceTransformer, lalu mencari buku yang paling mirip secara semantik menggunakan Qdrant sebagai vector database. Aplikasi menyediakan API indexing dan pencarian melalui FastAPI dengan endpoint `GET /health`, `POST /index`, dan `POST /search`.

------------------------------------------------------

# Dataset

### Jumlah Data

Dataset yang digunakan dalam aplikasi ini berjumlah 50 data buku yang seleksi dan dikategorikan dari dataset asli [openlibrary_work_with_descriptions.json](https://www.kaggle.com/datasets/abdallamohamed312/open-library-works-with-descriptions-jsonl), lalu disimpan dalam file data.json. Data yang diseleksi mencakup judul, deskripsi, dan kategori buku.

### Kategori yang Digunakan

Menggunakan 10 kategori:
- fiction_novel
- science_tech_medicine
- history_biography
- art_architecture
- religion_islam
- education_reference
- business_finance
- politics_law_government
- language_linguistics
- travel

### Kenapa kalian memilih dataset tersebut?

Dataset Open Library Works With Descriptions karena memuat judul dan deskripsi buku yang sesuai untuk pengujian pencarian semantik. Informasi deskripsi membantu sistem menemukan buku berdasarkan makna dan konteks pertanyaan pengguna. Dari dataset tersebut, saya memilih 50 data buku yang dikelompokkan ke dalam 10 kategori agar pengolahan data lebih terarah. Data ini kemudian digunakan dalam proses embedding dan pencarian semantik menggunakan Qdrant

------------------------------------------------------

# Tech Stack

Tuliskan teknologi yang digunakan.

- Python
- FastAPI
- SentenceTransformers (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- Qdrant (local persistent, folder qdrant_data/, Distance.COSINE)
- HTML / CSS / JavaScript

------------------------------------------------------

# Application Flow

Jelaskan menggunakan bahasa kalian sendiri bagaimana flow berikut bekerja:

**Indexing:**
```text
data.json
    ↓
Validasi dan transformasi dokumen
    ↓
SentenceTransformer
    ↓
Embedding vector
    ↓
Qdrant collection
```

**Pencarian:**
```text
User Query
    ↓
Validasi query dan top_k
    ↓
SentenceTransformer
    ↓
Qdrant cosine similarity search
    ↓
Top-K hasil: title, text, category, score
    ↓
API response / Frontennd
```

Penjelasan kalian:

Aplikasi ini bekerja melalui dua alur utama:

1. **Alur Indexing (Persiapan Data ke Vector Database):**
   - Dokumen buku diambil dari `data.json` (berisi 50 data buku dengan field `id`, `title`, `text`, dan `category`).
   - Setiap teks buku diekstraksi lalu diubah menjadi representasi vektor numerik berdimensi 384 menggunakan model SentenceTransformer (`paraphrase-multilingual-MiniLM-L12-v2`) dengan `normalize_embeddings=True`.
   - Vektor beserta metadata (`title`, `text`, `category`) dibungkus menjadi objek `PointStruct` Qdrant dengan ID unik stabil.
   - Poin-poin tersebut disimpan ke dalam Qdrant local collection (`books`) menggunakan operasi `upsert` dengan metrik `Distance.COSINE` agar data tersimpan persisten dan tidak duplikasi saat di-index ulang.

2. **Alur Pencarian Semantik (Semantic Search):**
   - Pengguna mengirim kueri teks dan parameter `top_k` melalui API `POST /search` atau form antarmuka web.
   - Teks kueri dikonversi ke vektor berdimensi 384 menggunakan model embedding yang sama dan dinormalisasi.
   - Qdrant membandingkan vektor kueri terhadap semua vektor buku dalam koleksi menggunakan metode cosine similarity (`client.query_points()`).
   - Qdrant mengembalikan kandidat teratas sejumlah `top_k` beserta skor kemiripan (similarity score) dan metadata payload.
   - Hasil pencarian diformat menjadi respon JSON yang menampilkan `id`, `title`, `text`, `category`, dan `score`.

------------------------------------------------------

# Embedding Model

Model yang digunakan:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### Menurut kalian, apa fungsi embedding model pada project ini?

Embedding model berfungsi sebagai penerjemah bahasa alami menjadi representasi vektor numerik berdimensi tinggi (384 dimensi) yang menangkap makna semantik dan konteks kalimat. Model dapat memahami kueri maupun dokumen dalam bahasa Indonesia maupun bahasa Inggris, memetakan konsep yang maknanya serupa ke titik koordinat yang berdekatan di ruang vektor, serta memungkinkan pencarian berbasis arti/konsep tanpa harus bergantung pada kecocokan kata kunci secara persis.

------------------------------------------------------

# Vector Database

### Apa fungsi Qdrant pada aplikasi kalian?

Qdrant berfungsi sebagai tempat penyimpanan dan mesin pengindeksan vektor. Qdrant mengelola penyimpanan vektor di folder lokal (`qdrant_data/`) dan melakukan perhitungan pencarian tetangga terdekat (Approximate Nearest Neighbor search) berbasis Cosine Distance, sehingga sistem dapat menemukan dokumen paling relevan terhadap vektor kueri dalam waktu singkat tanpa perlu komputasi manual brute-force di memori Python.

### Apa saja data yang kalian simpan di payload?

Data yang disimpan dalam payload Qdrant adalah metadata buku:
- `title`: Judul buku.
- `text`: Gabungan judul dan deskripsi lengkap buku yang menjadi dasar representasi makna.
- `category`: Kategori klasifikasi buku (misal: `fiction_novel`, `science_tech_medicine`, `history_biography`, dll).

------------------------------------------------------

# API Endpoint

1. `GET /health`: Memeriksa status kesehatan server, nama koleksi Qdrant yang aktif, dan model embedding yang digunakan.
2. `POST /index`: Membaca dataset `data.json`, membuat embedding, dan melakukan upsert poin ke koleksi Qdrant `books`.
3. `POST /search`: Menerima kueri pencarian teks dan nilai `top_k`, lalu mengembalikan daftar buku paling relevan beserta similarity score.
4. `GET /static/`: Menyediakan antarmuka web interaktif (HTML, CSS, JS) untuk memudahkan pencarian pengguna secara visual.

------------------------------------------------------

# Example Request

```json
{
  "query": "buku tentang kecerdasan buatan dan machine learning",
  "top_k": 3
}
```

------------------------------------------------------

# Example Response

```json
{
  "query": "buku tentang kecerdasan buatan dan machine learning",
  "top_k": 3,
  "results": [
    {
      "id": 6,
      "title": "Dasar-Dasar Kecerdasan Buatan",
      "text": "Dasar-Dasar Kecerdasan Buatan. Buku ini membahas konsep dasar Artificial Intelligence, implementasi machine learning, dan penggunaannya dalam aplikasi praktis menggunakan bahasa pemrograman Python.",
      "category": "science_tech_medicine",
      "score": 0.7816142618709726
    },
    {
      "id": 23,
      "title": "Introduction to Computational Linguistics",
      "text": "Introduction to Computational Linguistics. Explores how computers process, analyze, and understand human language semantics using NLP models.",
      "category": "language_linguistics",
      "score": 0.3732897696813101
    },
    {
      "id": 47,
      "title": "The Art of Comic Illustration",
      "text": "The Art of Comic Illustration. An instructional visual arts guide offering techniques on storyboarding and creating dynamic panels.",
      "category": "art_architecture",
      "score": 0.29428693788057575
    }
  ]
}
```

------------------------------------------------------

# Experiment 1 - Semantic Search

## Query 1

**Query:**

kebijakan moneter dan penanganan inflasi oleh bank sentral

**Top Result:**

```json
"title": "Monetary Policy and Central Banking",
"text": "Monetary Policy and Central Banking. A textbook evaluating currency valuation techniques, inflation targeting frameworks, and modern governance.",
"category": "business_finance"
```

**Similarity Score:**

0.8491186693127792

**Menurut kalian apakah hasilnya relevan? Kenapa?**

hasilnya cukup relevan karena membahas kebijakan moneter dan peran bank sentral dalam mengatasi inflasi. Skor similarity 0,849 juga menunjukkan kalau hasilnya punya kemiripan yang tinggi dengan query. meskipun judul buku nya dalam bahasa inggris tapi tetap relevan dengan kueri nya.

------------------------------------------------------

## Query 2

**Query:**

novel petualangan fantasi pangeran merebut kembali tahta kerajaan

**Top Result:**

```json
"title": "The Golden Crown",
"text": "The Golden Crown. An epic fantasy novel tracing the perilous journey of an exiled prince struggling to reclaim his lost kingdom.",
"category": "fiction_novel",
```

**Similarity Score:**

0.7378558196170093

**Menurut kalian apakah hasilnya relevan? Kenapa?**

relevan karena novel tersebut bercerita tentang seorang pangeran yang diasingkan dan berjuang untuk merebut kembali kerajaannya. Ceritanya sesuai dengan query tentang novel petualangan fantasi dan perebutan tahta. Skor similarity 0,738 cukup tinggi, bisa jadi itu adalah novel yang dicari.

------------------------------------------------------

## Query 3

**Query:**

buku referensi untuk pemula yang ingin belajar ngoding sistem komputer yang bisa berpikir sendiri

**Top Result:**

```json
"title": "Introduction to Computational Linguistics",
"text": "Introduction to Computational Linguistics. Explores how computers process, analyze, and understand human language semantics using NLP models.",
"category": "language_linguistics"
```

**Similarity Score:**

0.49684377126808155

**Menurut kalian apakah hasilnya relevan? Kenapa?**

hasilnya kurang relevan karena buku tersebut lebih fokus membahas cara komputer memahami bahasa manusia menggunakan NLP, bukan panduan dasar untuk belajar ngoding atau membuat sistem yang bisa berpikir sendiri seperti AI. Skor similarity 0,497 juga menunjukkan kemiripan yang tidak terlalu tinggi.

------------------------------------------------------

## Query 4

**Query:**

cerita dongeng fiksi tentang binatang yang berusaha mengakali dan melarikan diri dari pemangsanya

**Top Result:**

```json
"title": "The Three Little Pigs Tale",
"text": "The Three Little Pigs Tale. The story, adapted from the English folktale, of three little pigs who outwit a wolf.",
"category": "fiction_novel",
```

**Similarity Score:**

0.612426145916297

**Menurut kalian apakah hasilnya relevan? Kenapa?**

hasilnya relevan karena cerita tersebut menggambarkan tiga babi yang berhasil mengakali serigala sebagai pemangsanya. Ceritanya sesuai dengan query tentang dongeng binatang yang berusaha menyelamatkan diri. Skor similarity 0,612 menunjukkan kemiripan yang cukup.
------------------------------------------------------

## Query 5

**Query:**

literatur yang membahas taktik pertempuran dan negosiasi bangsa kita saat melawan penjajah tahun empat puluhan

**Top Result:**

```json
"title": "Sejarah Perang Kemerdekaan Indonesia",
"text": "Sejarah Perang Kemerdekaan Indonesia. Mengulas secara komprehensif taktik gerilya dan perjuangan diplomasi selama masa revolusi fisik kemerdekaan Indonesia.",
"category": "history_biography"
```

**Similarity Score:**

0.5069467257583746

**Menurut kalian apakah hasilnya relevan? Kenapa?**

hasilnya cukup relevan karena membahas taktik gerilya dan perjuangan diplomasi Indonesia saat melawan penjajah pada masa revolusi kemerdekaan. Topik tersebut sesuai dengan query tentang taktik pertempuran dan negosiasi pada tahun 1940-an. Skor similarity 0,507 memang tidak terlalu tinggi, tetapi isi bukunya masih berkaitan dengan informasi yang dicari.

------------------------------------------------------

# Experiment 2 - Top-K

Gunakan query yang sama.

### Query

buku tentang kecerdasan buatan dan machine learning

------------------------------------------------------

## Top-K = 1

Actual Result:
```json
{
  "query": "buku tentang kecerdasan buatan dan machine learning",
  "top_k": 1,
  "results": [
    {
      "id": 6,
      "title": "Dasar-Dasar Kecerdasan Buatan",
      "text": "Dasar-Dasar Kecerdasan Buatan. Buku ini membahas konsep dasar Artificial Intelligence, implementasi machine learning, dan penggunaannya dalam aplikasi praktis menggunakan bahasa pemrograman Python.",
      "category": "science_tech_medicine",
      "score": 0.7816142618709726
    }
  ]
}
```
------------------------------------------------------

## Top-K = 3

Actual Result:
```json
{
  "query": "buku tentang kecerdasan buatan dan machine learning",
  "top_k": 3,
  "results": [
    {
      "id": 6,
      "title": "Dasar-Dasar Kecerdasan Buatan",
      "text": "Dasar-Dasar Kecerdasan Buatan. Buku ini membahas konsep dasar Artificial Intelligence, implementasi machine learning, dan penggunaannya dalam aplikasi praktis menggunakan bahasa pemrograman Python.",
      "category": "science_tech_medicine",
      "score": 0.7816142618709726
    },
    {
      "id": 23,
      "title": "Introduction to Computational Linguistics",
      "text": "Introduction to Computational Linguistics. Explores how computers process, analyze, and understand human language semantics using NLP models.",
      "category": "language_linguistics",
      "score": 0.3732897696813101
    },
    {
      "id": 47,
      "title": "The Art of Comic Illustration",
      "text": "The Art of Comic Illustration. An instructional visual arts guide offering techniques on storyboarding and creating dynamic panels.",
      "category": "art_architecture",
      "score": 0.29428693788057575
    }
  ]
}
```
------------------------------------------------------

## Top-K = 5

Actual Result:
```json
{
  "query": "buku tentang kecerdasan buatan dan machine learning",
  "top_k": 5,
  "results": [
    {
      "id": 6,
      "title": "Dasar-Dasar Kecerdasan Buatan",
      "text": "Dasar-Dasar Kecerdasan Buatan. Buku ini membahas konsep dasar Artificial Intelligence, implementasi machine learning, dan penggunaannya dalam aplikasi praktis menggunakan bahasa pemrograman Python.",
      "category": "science_tech_medicine",
      "score": 0.7816142618709726
    },
    {
      "id": 23,
      "title": "Introduction to Computational Linguistics",
      "text": "Introduction to Computational Linguistics. Explores how computers process, analyze, and understand human language semantics using NLP models.",
      "category": "language_linguistics",
      "score": 0.3732897696813101
    },
    {
      "id": 47,
      "title": "The Art of Comic Illustration",
      "text": "The Art of Comic Illustration. An instructional visual arts guide offering techniques on storyboarding and creating dynamic panels.",
      "category": "art_architecture",
      "score": 0.29428693788057575
    },
    {
      "id": 30,
      "title": "Demokrasi dalam Praktik",
      "text": "Demokrasi dalam Praktik. Buku ini mengevaluasi sistem pemilu modern, perlindungan hak sipil, dan dinamika partisipasi politik masyarakat.",
      "category": "politics_law_government",
      "score": 0.2862120205976285
    },
    {
      "id": 3,
      "title": "Milk, Meat Biscuits, and the Terraqueous Machine",
      "text": "Milk, Meat Biscuits, and the Terraqueous Machine. A biography of the inventor, businessmen, surveyor, and philanthropist who, among other accomplishments, was the first to develop a method to condense milk and founded the dairy company bearing his name.",
      "category": "history_biography",
      "score": 0.2801068308532235
    }
  ]
}
```
------------------------------------------------------

### Apa perubahan yang kalian lihat ketika nilai Top-K diperbesar?

Hanya menampilkan lebih banyak best result berdasarkan similarity score dengan query yang di uji.

### Apakah menambah Top-K selalu membuat hasil pencarian menjadi lebih baik? Berikan pendapat kalian berdasarkan hasil eksperimen.

Tidak selalu, karena menambah top K itu hanya menampilkan lebih banyak best result yang diurutkan berdasarkan similarity score dengan query yang di uji. Bahkan buku-buku yang similarity score ny dibawah 0.3 terlihat tidak relevan dengan query yang di uji.

------------------------------------------------------

# Experiment 3 - Bad Retrieval

Cari satu query yang menghasilkan retrieval yang menurut kalian kurang relevan.

### Query

resep memasak rendang daging sapi padang yang empuk dan gurih


### Actual Results

```json
{
  "query": "resep memasak rendang daging sapi padang yang empuk dan gurih",
  "top_k": 1,
  "results": [
    {
      "id": 3,
      "title": "Milk, Meat Biscuits, and the Terraqueous Machine",
      "text": "Milk, Meat Biscuits, and the Terraqueous Machine. A biography of the inventor, businessmen, surveyor, and philanthropist who, among other accomplishments, was the first to develop a method to condense milk and founded the dairy company bearing his name.",
      "category": "history_biography",
      "score": 0.29340913368484084
    }
  ]
}
```

### Similarity Score

0.29340913368484084

### Kenapa menurut kalian hasil tersebut kurang relevan?

hasilnya kurang relevan karena query membahas resep rendang daging sapi Padang, sedangkan hasil yang muncul membahas biografi seorang penemu yang berkaitan dengan industri susu. Topiknya cukup jauh berbeda. Skor similarity 0,293 juga menunjukkan tingkat kemiripan yang rendah.

### Menurut kalian apa yang mungkin menyebabkan hasil tersebut?

Penyebabnya adalah dataset yang digunakan terlalu sedikit dan tidak ada data buku yang membahas tentang resep makanan. Sistemnya hanya mengambil nilai yang mendekati dengan query yang diberikan. Itulah kenapa hasil nya menjadi tidak relevan dengan informasi yang dicari.

------------------------------------------------------

# Personal Reflection

Jawab berdasarkan pengalaman kalian sendiri setelah menjalankan project.

### 1. Sebelum mengerjakan tugas ini, bagaimana kalian membayangkan sebuah search engine bekerja? Apakah ada perbedaan setelah mempelajari semantic search?

saya bayangin ya search engine itu mencari data atau kalimat yang paling mendekati dengan apa yang di inputkan, tapi setelah mempelajari semantic search ternyata search engine itu bisa mencari data atau kalimat yang memiliki makna yang mirip dengan apa yang di inputkan termasuk perbedaan bahasa dan gaya bahasa. 

### 2. Menurut kalian apa perbedaan terbesar antara keyword search dan semantic search?

perbedaan terbesar antara keyword search dan semantic search adalah keyword search hanya mencari kecocokan kata, sedangkan semantic search mencari kecocokan makna. dengan kata lain keyword search itu hanya mencocokkan teksnya saja, sedangkan semantic search mencocokkan makna dari teks tersebut.

### 3. Menurut kalian apa fungsi embedding di dalam semantic search?

embedding adalah representasi vektor dari teks yang digunakan untuk mencari kecocokan makna antara teks. 

### 4. Kenapa embedding tidak cukup hanya disimpan di list Python jika jumlah data menjadi sangat banyak?

karena menyimpan embedding di list python hanya bisa digunakan untuk data yang sedikit, jika data menjadi sangat banyak maka akan memakan banyak memori dan juga akan lambat dalam pencarian.

### 5. Bagian project mana yang paling sulit kalian pahami?

bagian menghubungkan main.py ke frontend.

### 6. Bagian kode mana yang paling banyak dibantu oleh AI?

Static dan kode di main.py buat menghubungkan ke frontend.

### 7. Jelaskan dengan bahasa kalian sendiri bagaimana bagian kode tersebut bekerja.

Static berisi file html, css, dan javascript yang digunakan untuk membuat frontend aplikasi. file main.py berisi kode untuk membuat backend aplikasi.

### 8. Menurut kalian, aplikasi semantic search yang kalian buat bisa dikembangkan menjadi aplikasi apa jika project ini dilanjutkan?

bisa dikembangin jadi aplikasi peminjamaan buku perpustakaan digital, bisa rekomendasi buku berdasarkan preferensi pengguna.

------------------------------------------------------

# AI Usage

### AI tools yang digunakan

gemini

### AI digunakan untuk membantu bagian apa?

membuat frontend dan menghubungkan main.py ke frontend (http://127.0.0.1:8000/static/index.html)

### Bagian apa yang kalian ubah atau tentukan sendiri setelah mendapatkan hasil dari AI?

- menambahkan id, text, category, dan score ke hasil pencarian.
- frontend bagian tata letak
- endpoint dan class
------------------------------------------------------

