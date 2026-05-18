# SPK Pemilihan Kendaraan Listrik

## Deskripsi Proyek

Proyek ini merupakan Sistem Pendukung Keputusan (SPK) berbasis web untuk membantu pengguna memilih kendaraan listrik (Electric Vehicle / EV) berdasarkan beberapa kriteria tertentu.

Aplikasi dibangun menggunakan:

* Python
* Streamlit
* Pandas
* NumPy
* Matplotlib

Metode yang digunakan dalam sistem ini adalah metode Weighted Product (WP), di mana pengguna dapat menentukan prioritas kriteria secara interaktif, lalu sistem akan melakukan proses perhitungan dan menampilkan ranking kendaraan listrik terbaik.

---

## Fitur Utama

### 1. Dashboard Data EV

Halaman dashboard digunakan untuk:

* Menampilkan dataset kendaraan listrik
* Melakukan filter berdasarkan brand
* Melihat seluruh data kendaraan yang tersedia

File terkait:

* `dashboard.py`

---

### 2. Proses SPK (Weighted Product)

Halaman process merupakan inti utama aplikasi.

Fitur yang tersedia:

* Filter data kendaraan berdasarkan brand
* Filter data numerik menggunakan dataframe explorer
* Pengurutan prioritas kriteria secara drag-and-drop
* Perhitungan bobot prioritas
* Perhitungan nilai S
* Perhitungan nilai V
* Ranking kendaraan listrik
* Visualisasi grafik menggunakan Matplotlib

File terkait:

* `process.py`
* `EVChoose.py`

---

### 3. Profil Developer

Menampilkan informasi anggota tim pengembang aplikasi.

File terkait:

* `profile.py`


## Penjelasan Setiap File

### `main.py`

Berfungsi sebagai entry point aplikasi Streamlit.

Mengatur:

* Navigasi halaman
* Konfigurasi aplikasi
* Routing antar halaman

---

### `dashboard.py`

Digunakan untuk:

* Menampilkan dataset EV
* Filter berdasarkan brand
* Menampilkan tabel data kendaraan listrik

---

### `process.py`

Berisi proses utama Sistem Pendukung Keputusan.

Fitur utama:

* Pengaturan prioritas kriteria
* Filtering dataset
* Perhitungan metode Weighted Product
* Visualisasi hasil ranking
* Grafik nilai S dan V

---

### `EVChoose.py`

Berisi seluruh fungsi utama perhitungan.

Fungsi yang tersedia:

* `hitung_prioritas()` → Menghitung bobot prioritas
* `computeSValue()` → Menghitung nilai S
* `computeVValue()` → Menghitung nilai V
* `computeRank()` → Menghasilkan ranking kendaraan
* `prepare_data()` → Membersihkan dan menyiapkan dataset

Selain itu file ini juga menyimpan:

* Mapping kriteria
* Kriteria benefit dan cost

---

### `extractDataset.py`

Digunakan untuk mengambil dan membersihkan kolom penting dari dataset mentah.

Output:

* `clean_ev_spec_dataset.csv`

---

### `default_ev_spec_dataset.csv`

Dataset mentah kendaraan listrik.
Sumber Dataset : https://www.kaggle.com/datasets/urvishahir/electric-vehicle-specifications-dataset-2025
---

### `clean_ev_spec_dataset.csv`

Dataset hasil cleaning yang digunakan dalam proses SPK.

Kolom yang digunakan:

* Brand
* Model
* Range
* Efficiency
* Acceleration
* Charging Power
* Seats
* Cargo Volume

---

## Kriteria Penilaian

Sistem menggunakan beberapa kriteria berikut:

| Kriteria              | Tipe    |
| --------------------- | ------- |
| Range                 | Benefit |
| Efficiency            | Cost    |
| Acceleration          | Cost    |
| Charging Time / Power | Benefit |
| Seats                 | Benefit |
| Cargo Space           | Benefit |

Keterangan:

* Benefit → semakin besar nilainya semakin baik
* Cost → semakin kecil nilainya semakin baik

---

## Cara Menjalankan Program

### 1. Clone Repository

```bash
git clone <repository-url>
cd spk-pemilihan-ev-main
```

---

### 2. Install Dependency

```bash
pip install streamlit pandas numpy matplotlib streamlit-extras streamlit-sortables
```

---

### 3. Jalankan Aplikasi

```bash
streamlit run main.py
```

---

## Alur Sistem

1. Dataset kendaraan listrik dibaca
2. Data dibersihkan dan diproses
3. User menentukan prioritas kriteria
4. Sistem menghitung bobot prioritas
5. Dilakukan perhitungan metode Weighted Product
6. Nilai preferensi dihitung
7. Sistem menghasilkan ranking kendaraan listrik terbaik

---

## Teknologi yang Digunakan

| Teknologi  | Fungsi                   |
| ---------- | ------------------------ |
| Python     | Bahasa pemrograman utama |
| Streamlit  | Framework GUI web        |
| Pandas     | Pengolahan data          |
| NumPy      | Perhitungan numerik      |
| Matplotlib | Visualisasi grafik       |


## Developer

### Backend Developer

* Nicolaus Narindra L

### Frontend Developer

* Muthia Umairah

---

## Catatan

Project ini dibuat untuk kebutuhan pembelajaran dan implementasi Sistem Pendukung Keputusan menggunakan metode Weighted Product berbasis Streamlit.
