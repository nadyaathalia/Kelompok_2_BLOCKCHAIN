
# E-Voting UINSSC
## Tim Pengembang

- Much Mentari Irwansyah
- Akbar Fabiansyah
- Nadya Athalia Diva

## Panduan Penggunaan Aplikasi Berbasis Blockchain

E-Voting UINSSC merupakan aplikasi pemungutan suara berbasis blockchain yang memanfaatkan Ethereum Smart Contract, MetaMask, dan NFT sebagai bukti pencatatan partisipasi pemilih.

Aplikasi dikembangkan menggunakan Python, Streamlit, Solidity, dan Hardhat. Terdapat dua role utama, yaitu **Admin** dan **Pemilih**, serta dua mekanisme voting, yaitu simulasi Python dan voting melalui MetaMask.

---

## 1. Persiapan Sistem

Pastikan sudah tersedia:

- Python 3.10 atau lebih baru
- Node.js dan NPM
- MetaMask Extension
- Hardhat dan dependency proyek
- Smart Contract yang sudah di-deploy
- File `deployment.json` dengan alamat kontrak terbaru

## 2. Cara Menjalankan Aplikasi

**A. Clone Repository**

```bash
git clone <URL-REPOSITORY>
cd E-Voting-UINSSC
```

**B. Instalasi Dependency Python**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**C. Instalasi Dependency Hardhat**

```bash
npm install
```

**D. Jalankan Hardhat Node**

Buka terminal pertama:

```bash
npx hardhat node
```

Jaringan blockchain berjalan pada `http://127.0.0.1:8545`.

**E. Deploy Smart Contract**

Buka terminal kedua:

```bash
npx hardhat run scripts/deploy.js --network localhost
```

Pastikan alamat kontrak dan Chain ID diperbarui pada `deployment.json`.

**F. Konfigurasi MetaMask**

Tambahkan jaringan Hardhat Localhost:

| Pengaturan | Nilai |
|---|---|
| Network Name | Hardhat Localhost |
| RPC URL | http://127.0.0.1:8545 |
| Chain ID | 31337 |
| Currency Symbol | ETH |

Import akun administrator dari private key Hardhat.

**G. Jalankan Streamlit**

Buka terminal ketiga:

```bash
streamlit run app.py
```

Buka aplikasi melalui browser:

```text
http://localhost:8501
```

---

## 3. Memilih Role

Pada halaman awal, pengguna dapat memilih:

- **Admin:** Mengelola pendaftaran pemilih dan memantau hasil pemilihan.
- **Pemilih:** Melihat kandidat dan memberikan suara.

Hubungkan MetaMask melalui tombol Hubungkan MetaMask sebelum melakukan transaksi blockchain.

---

## 4. Alur Admin

Admin memiliki lima menu utama:

1. **Dashboard**

   Menampilkan jumlah pemilih (simulasi), jumlah kandidat, total suara on-chain, suara simulasi Python, dan status blockchain.

2. **Voter Registration**

   Digunakan untuk mendaftarkan ID pemilih ke Smart Contract.

   Langkah:
   - Hubungkan MetaMask menggunakan wallet admin.
   - Masukkan ID pemilih.
   - Klik Daftarkan Pemilih On-chain.
   - Konfirmasi transaksi melalui MetaMask.
   - Tunggu hingga transaksi berhasil.

   Hanya wallet administrator yang melakukan deployment kontrak yang dapat mendaftarkan pemilih.

3. **Candidate List**

   Menampilkan nomor urut, foto, nama kandidat, visi, dan misi.

4. **Voting Results**

   Menampilkan total suara on-chain, grafik perolehan suara, rekapitulasi, dan persentase suara setiap kandidat. Hasil simulasi Python ditampilkan secara terpisah.

5. **Voter Verification**

   Digunakan untuk memeriksa ID pemilih melalui Smart Contract, meliputi status pendaftaran, status voting, kandidat yang dipilih, dan Token ID NFT jika sudah memilih.

---

## 5. Alur Pemilih

Pemilih memiliki dua menu utama:

1. **Candidate List**

   Menampilkan informasi kandidat berupa nomor urut, foto, nama, visi, dan misi. Tombol Pilih Kandidat digunakan untuk menentukan pilihan sementara.

2. **Voting Page**

   Menyediakan dua mekanisme pemungutan suara:

   **A. Simulasi Python**
   - Masukkan ID pemilih.
   - Pilih kandidat.
   - Klik Lanjutkan ke Konfirmasi.
   - Periksa pilihan.
   - Klik Konfirmasi Vote.
   - Suara dicatat pada blockchain simulasi Python.

   **B. Voting melalui MetaMask**
   - Pastikan ID sudah didaftarkan admin.
   - Hubungkan MetaMask.
   - Masukkan ID pemilih.
   - Pilih kandidat.
   - Klik Kirim Vote via MetaMask.
   - Konfirmasi transaksi melalui MetaMask.
   - Tunggu hingga transaksi berhasil.
   - Suara dicatat pada Smart Contract.

---

## 6. Penerbitan NFT

Setelah voting melalui MetaMask berhasil:

1. Smart Contract memvalidasi ID pemilih.
2. Pilihan kandidat dicatat pada blockchain.
3. Smart Contract menerbitkan NFT melalui mekanisme ERC-721.
4. Token ID NFT disimpan pada data pemilih.
5. Informasi NFT dapat diperiksa melalui Voter Verification.

NFT berfungsi sebagai bukti pencatatan partisipasi pemilih.

---

## 7. Alur Kerja Sistem

```text
              MULAI
                |
                v
           Buka Aplikasi
                |
                v
             Pilih Role
            /         \
           v           v
         ADMIN       PEMILIH
           |             |
           v             v
       Dashboard    Candidate List
           |             |
           v             v
  Voter Registration Voting Page
           |             |
           v             v
     Hubungkan       Pilih Metode
     MetaMask         Voting
           |          /       \
           v         v         v
      Masukkan ID  Python    MetaMask
           |         |          |
           v         v          v
      Konfirmasi  Konfirmasi  Validasi
      Transaksi    Voting     Smart Contract
           |         |          |
           v         v          v
      ID Terdaftar Suara      Suara Dicatat
                   Dicatat        |
                                 v
                              Minting NFT
                                 |
                                 v
                          Verifikasi Pemilih
                                 |
                                 v
                           Hasil Voting
                                 |
                                 v
                              SELESAI
```

---

## 8. Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python | Bahasa pemrograman utama |
| Streamlit | Antarmuka aplikasi |
| Solidity | Pembuatan Smart Contract |
| Hardhat | Blockchain lokal dan deployment |
| MetaMask | Wallet dan konfirmasi transaksi |
| Ethereum EVM | Eksekusi Smart Contract |
| ERC-721 | Standar penerbitan NFT |
| Plotly | Visualisasi hasil voting |

---

## 9. Catatan Penting

- Hardhat Node harus tetap berjalan selama aplikasi digunakan.
- Pastikan `deployment.json` berisi alamat kontrak yang sesuai.
- Jika Hardhat Node di-reset, lakukan deployment ulang Smart Contract.
- Gunakan wallet admin yang sesuai dengan pemilik Smart Contract.
- ID pemilih harus didaftarkan sebelum melakukan voting on-chain.
- Setiap ID hanya dapat melakukan voting satu kali pada Smart Contract.
- Simulasi Python dan voting MetaMask memiliki penyimpanan serta hasil yang terpisah.
- ID pemilih dan pilihan kandidat pada Smart Contract dapat dibaca secara publik.

**Catatan:** Aplikasi ini merupakan prototype akademik dan belum ditujukan untuk pemilihan nyata yang membutuhkan kerahasiaan suara.

---

**Universitas Islam Negeri Siber Syekh Nurjati Cirebon**
