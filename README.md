# 🤖 MCP Data Assistant (Local AI)

**MCP Data Assistant** adalah aplikasi asisten pintar berbasis AI yang berjalan sepenuhnya di jaringan lokal (on-premise). Aplikasi ini menghubungkan **LLM Lokal (via LM Studio)** dengan data privat Anda, baik dalam bentuk file flat (Excel/CSV) maupun database relasional (**SQL Server**), menggunakan standar **Model Context Protocol (MCP)**.

## 🌟 Fitur Utama
* **Privacy-First:** Data Anda tidak pernah keluar ke internet. Proses inferensi dilakukan 100% lokal.
* **Smart Data Retrieval:** AI mampu menentukan kapan harus membaca file atau kapan harus melakukan query ke database berdasarkan pertanyaan user.
* **MCP Integration:** Menggunakan library `FastMCP` untuk standarisasi pemanggilan tool (function calling).
* **Interactive UI:** Tampilan chat yang modern dengan kemampuan menampilkan hasil data dalam bentuk tabel interaktif.

---

## 🏗️ Struktur Folder & File

```text
mcp-data-assistant/
├── backend/                # Logika Server & AI
│   ├── core/
│   │   ├── config.py       # Manajemen Environment (.env)
│   │   └── logger.py       # Sistem Logging
│   ├── mcp/
│   │   ├── server.py       # Inisialisasi FastMCP Server
│   │   └── tools/          # Definisi Kemampuan AI
│   │       ├── __init__.py
│   │       ├── file_tool.py  # Logika baca Excel/CSV
│   │       └── db_tool.py    # Logika query SQL Server
│   ├── main.py             # Entry point FastAPI
│   └── .env                # Kredensial & API Keys
├── frontend/               # Antarmuka Pengguna
│   ├── components/
│   │   ├── chat_ui.py      # Tampilan pesan & tabel
│   │   └── sidebar.py      # Panel pengaturan
│   ├── api_client.py       # Konektor ke Backend
│   └── app.py              # Entry point Streamlit
├── data/                   # Penyimpanan file Excel/CSV lokal
├── requirements.txt        # Daftar library Python
└── README.md               # Dokumentasi Proyek
```

---

## 🛠️ Langkah Persiapan (Step-by-Step)

### 1. Persiapan Infrastruktur Lokal
- **LM Studio:** Download dan instal LM Studio. Pilih model (misal: Llama-3.1-8B-Instruct), lalu aktifkan Local Server pada port 1234.
- **ODBC Driver:** Instal Microsoft ODBC Driver for SQL Server agar Python bisa terhubung ke database.

### 2. Instalasi Library
Buka terminal di root project dan jalankan:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Konfigurasi Environment (backend/.env)
Buat file `.env` di dalam folder `backend/` dan sesuaikan nilainya:

```env
AI_BASE_URL=http://localhost:1234/v1
AI_API_KEY=lm-studio
DB_SERVER=NAMA_SERVER_ANDA\SQLEXPRESS
DB_NAME=NAMA_DATABASE
DB_USER=sa
DB_PASSWORD=PASSWORD_ANDA
```

### 4. Implementasi Kode Utama
Aplikasi ini bekerja dengan alur berikut:

1. **FastMCP Server** mendaftarkan fungsi `read_excel_csv` dan `query_sql`.
2. **FastAPI** bertindak sebagai perantara yang mengirimkan pesan user ke LM Studio.
3. Jika AI membutuhkan data, AI akan memberikan instruksi pemanggilan fungsi ke FastAPI.
4. **FastAPI** menjalankan fungsi tersebut melalui MCP Server dan mengembalikan hasilnya ke AI untuk dirangkum.

---

## 🚀 Cara Menjalankan Aplikasi

### Metode 1: Single Command (Recommended)

Jalankan backend dan frontend sekaligus dengan satu perintah:

```bash
python run.py
```

**Opsi lainnya:**

```bash
# Backend saja
python run.py --backend

# Frontend saja
python run.py --frontend
```

### Metode 2: Manual (Dua Terminal)

**Terminal 1: Backend (FastAPI)**

```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2: Frontend (Streamlit)**

```bash
streamlit run frontend/app.py
```

### Akses Aplikasi

Setelah berjalan, buka browser:
- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

---

## 💡 Contoh Pertanyaan untuk AI

Setelah aplikasi berjalan, Anda bisa mencoba pertanyaan seperti:

- "Sebutkan nama file apa saja yang tersedia di folder data?"
- "Tampilkan 5 baris pertama dari file penjualan_2024.csv."
- "Berapa total stok barang untuk kategori 'Elektronik' di database SQL?"
- "Bandingkan total penjualan di file CSV dengan data yang ada di SQL Server."

---

## 🔒 Catatan Keamanan

- **Akses Database:** Pastikan user database yang digunakan di `.env` hanya memiliki izin `SELECT` (Read-Only) untuk mencegah penghapusan data yang tidak disengaja oleh AI.
- **Local Only:** Aplikasi ini dirancang untuk penggunaan internal. Jika ingin di-deploy ke server publik, pastikan menambahkan sistem autentikasi (OAuth2/API Key) pada FastAPI.
