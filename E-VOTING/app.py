
from collections import Counter
from pathlib import Path

import plotly.express as px
import streamlit as st

from blockchain import Blockchain


# =====================================================
# KONFIGURASI
# =====================================================

st.set_page_config(
    page_title="E-Voting UINSSC",
    page_icon="🗳️",
    layout="wide"
)

NAMA_KAMPUS = "Universitas Islam Negeri Siber Syekh Nurjati Cirebon"

TOTAL_PEMILIH = 100  # Angka simulasi

KANDIDAT = [
    {
        "id": "01",
        "nama": "Pasangan Calon 01",
        "foto": "",
        "visi": "Mewujudkan organisasi mahasiswa yang aktif, terbuka, dan kolaboratif.",
        "misi": [
            "Meningkatkan komunikasi dan aspirasi mahasiswa.",
            "Mengembangkan program kerja yang bermanfaat.",
            "Mendorong kolaborasi antarmahasiswa."
        ]
    },
    {
        "id": "02",
        "nama": "Pasangan Calon 02",
        "foto": "",
        "visi": "Membangun lingkungan kampus yang inovatif, inklusif, dan berdaya saing.",
        "misi": [
            "Mendorong kegiatan akademik dan nonakademik.",
            "Meningkatkan transparansi program kerja.",
            "Memperluas ruang kreativitas mahasiswa."
        ]
    },
    {
        "id": "03",
        "nama": "Pasangan Calon 03",
        "foto": "",
        "visi": "Mewujudkan kepemimpinan mahasiswa yang responsif dan bertanggung jawab.",
        "misi": [
            "Menyediakan ruang aspirasi yang mudah diakses.",
            "Mengembangkan kegiatan yang berdampak.",
            "Memperkuat solidaritas mahasiswa."
        ]
    }
]

NAMA_KANDIDAT = [k["nama"] for k in KANDIDAT]



# =====================================================
# CSS / DESAIN UI
# =====================================================

st.markdown("""
<style>
.header-container {
    background: linear-gradient(135deg, #111827, #1e293b);
    padding: 30px;
    border-radius: 16px;
    margin-bottom: 25px;
    text-align: center;
}

.header-container h1 {
    color: #ffffff !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    margin-bottom: 12px;
}

.header-container p {
    color: #cbd5e1 !important;
    font-size: 15px !important;
    margin: 5px 0;
}
</style>

<div class="header-container">
    <h1>🗳️ E-Voting UNSSC</h1>
    <p>Universitas Islam Negeri Siber Syekh Nurjati Cirebon</p>
    <p>Sistem Pemungutan Suara Berbasis Blockchain</p>
</div>
""", unsafe_allow_html=True)
# =====================================================
# INISIALISASI BLOCKCHAIN
# =====================================================

if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = NAMA_KANDIDAT[0]

blockchain = st.session_state.blockchain
votes = blockchain.chain[1:]


# =====================================================
# FUNGSI SISTEM
# =====================================================

def sudah_memilih(id_pemilih):

    return any(
        block.data.get("id_pemilih") == id_pemilih
        for block in blockchain.chain[1:]
    )


def hitung_suara():

    return Counter(
        block.data.get("kandidat", "Tidak diketahui")
        for block in blockchain.chain[1:]
    )


def simpan_suara(id_pemilih, kandidat):

    blockchain.add_block({
        "id_pemilih": id_pemilih,
        "kandidat": kandidat,
        "pemilihan": "Pemilihan Ketua"
    })


# =====================================================
# HEADER
# =====================================================

# =====================================================
# SIDEBAR / NAVIGASI
# =====================================================

with st.sidebar:

    st.title("🗳️ E-Voting UIN")

    st.caption("Prototype Akademik")

    st.divider()

    halaman = st.radio(
        "NAVIGASI",
        [
            "Dashboard",
            "Candidate List",
            "Voting Page",
            "Voting Results",
            "Voter Verification"
        ]
    )

    st.divider()

    st.markdown("### Informasi Sistem")

    st.caption("Python")
    st.caption("Streamlit")
    st.caption("Blockchain")
    st.caption("Local Prototype")


# =====================================================
# DIALOG KONFIRMASI
# =====================================================

@st.dialog("Konfirmasi Pilihan")
def dialog_konfirmasi(id_pemilih, kandidat):

    st.warning(
        "Pastikan pilihan kamu sudah benar sebelum melanjutkan."
    )

    st.write("**ID Pemilih:**", id_pemilih)
    st.write("**Pilihan:**", kandidat)

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Kembali", use_container_width=True):
            st.rerun()

    with col2:

        if st.button(
            "Konfirmasi Vote",
            type="primary",
            use_container_width=True
        ):

            if sudah_memilih(id_pemilih):

                st.error("ID pemilih sudah memberikan suara.")

            else:

                simpan_suara(id_pemilih, kandidat)

                st.session_state.last_vote_status = True

                st.success("Suara berhasil dicatat!")

                st.rerun()


# =====================================================
# HALAMAN 1 — DASHBOARD
# =====================================================

if halaman == "Dashboard":

    st.subheader("📊 Dashboard Pemilihan")

    st.caption(
        "Ringkasan kondisi pemungutan suara saat ini."
    )

    total_suara = len(votes)

    status_chain = (
        "Valid"
        if blockchain.is_valid()
        else "Tidak Valid"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Pemilih Terdaftar",
        TOTAL_PEMILIH
    )

    col2.metric(
        "Jumlah Kandidat",
        len(KANDIDAT)
    )

    col3.metric(
        "Total Suara Masuk",
        total_suara
    )

    col4.metric(
        "Status Pemilihan",
        "Aktif"
    )

    st.divider()

    st.subheader("🔗 Status Blockchain")

    if blockchain.is_valid():

        st.success("Blockchain valid dan terhubung.")

    else:

        st.error("Blockchain tidak valid.")

    st.divider()

    st.subheader("📋 Aktivitas Terbaru")

    if votes:

        recent = list(reversed(votes[-5:]))

        st.dataframe(
            [
                {
                    "Blok": block.index,
                    "ID Pemilih": block.data.get("id_pemilih"),
                    "Kandidat": block.data.get("kandidat"),
                    "Waktu": block.timestamp
                }
                for block in recent
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Belum ada aktivitas voting.")


# =====================================================
# HALAMAN 2 — CANDIDATE LIST
# =====================================================

elif halaman == "Candidate List":

    st.subheader("👥 Candidate List")

    st.caption(
        "Kenali kandidat, visi, dan misi sebelum memberikan suara."
    )

    kolom = st.columns(3)

    for i, kandidat in enumerate(KANDIDAT):

        with kolom[i]:

            with st.container(border=True):

                st.markdown(
                    f'<div class="candidate-number">'
                    f'NOMOR URUT {kandidat["id"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if kandidat["foto"] and Path(kandidat["foto"]).is_file():

                    st.image(
                        kandidat["foto"],
                        use_container_width=True
                    )

                else:

                    st.markdown(
                        """
                        <div style="
                            background:#e6f4ed;
                            border-radius:12px;
                            padding:35px;
                            text-align:center;
                            font-size:52px;">
                            👤
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(f"### {kandidat['nama']}")

                st.markdown("**Visi**")

                st.write(kandidat["visi"])

                st.markdown("**Misi**")

                for misi in kandidat["misi"]:

                    st.markdown(f"- {misi}")

                if st.button(
                    "Pilih Kandidat",
                    key=f"pilih_{kandidat['id']}",
                    use_container_width=True
                ):

                    st.session_state.selected_candidate = kandidat["nama"]

                    st.success(
                        "Kandidat dipilih. Lanjutkan ke Voting Page."
                    )


# =====================================================
# HALAMAN 3 — VOTING PAGE
# =====================================================

elif halaman == "Voting Page":

    st.subheader("🗳️ Voting Page")

    st.caption(
        "Masukkan ID pemilih dan tentukan pilihan kandidat."
    )

    with st.container(border=True):

        id_pemilih = st.text_input(
            "ID Pemilih",
            placeholder="Contoh: IF-2026-001"
        )

        pilihan_default = (
            NAMA_KANDIDAT.index(
                st.session_state.selected_candidate
            )
            if st.session_state.selected_candidate in NAMA_KANDIDAT
            else 0
        )

        kandidat_dipilih = st.selectbox(
            "Pilih Kandidat",
            NAMA_KANDIDAT,
            index=pilihan_default
        )

        st.info(
            f"Pilihan kamu: **{kandidat_dipilih}**"
        )

        if st.button(
            "Lanjutkan ke Konfirmasi",
            type="primary",
            use_container_width=True
        ):

            id_bersih = id_pemilih.strip()

            if not id_bersih:

                st.error("ID pemilih wajib diisi.")

            elif sudah_memilih(id_bersih):

                st.error(
                    "ID pemilih ini sudah memberikan suara."
                )

            else:

                dialog_konfirmasi(
                    id_bersih,
                    kandidat_dipilih
                )

    if st.session_state.get("last_vote_status"):

        st.success("Transaksi berhasil dicatat.")


# =====================================================
# HALAMAN 4 — VOTING RESULTS
# =====================================================

elif halaman == "Voting Results":

    st.subheader("📈 Voting Results")

    st.caption(
        "Grafik dan rekapitulasi perolehan suara kandidat."
    )

    totals = hitung_suara()

    data_grafik = [
        {
            "Kandidat": kandidat,
            "Jumlah Suara": totals.get(kandidat, 0)
        }
        for kandidat in NAMA_KANDIDAT
    ]

    total_suara = sum(
        item["Jumlah Suara"]
        for item in data_grafik
    )

    st.metric(
        "Total Suara Masuk",
        total_suara
    )

    if total_suara > 0:

        fig = px.bar(
            data_grafik,
            x="Kandidat",
            y="Jumlah Suara",
            color="Kandidat",
            text="Jumlah Suara",
            title="Perolehan Suara Kandidat"
        )

        fig.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_title="Jumlah Suara",
            xaxis_title="Kandidat"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        st.subheader("Persentase Suara")

        for item in data_grafik:

            persen = (
                item["Jumlah Suara"] / total_suara
            ) * 100

            st.write(
                f"**{item['Kandidat']}** — "
                f"{item['Jumlah Suara']} suara "
                f"({persen:.1f}%)"
            )

            st.progress(persen / 100)

    else:

        st.info(
            "Grafik akan muncul setelah ada suara masuk."
        )

    st.divider()

    st.subheader("Rekapitulasi Suara")

    st.dataframe(
        data_grafik,
        use_container_width=True,
        hide_index=True
    )


# =====================================================
# HALAMAN 5 — VOTER VERIFICATION
# =====================================================

elif halaman == "Voter Verification":

    st.subheader("🔐 Voter Verification")

    st.caption(
        "Periksa status pemilih berdasarkan ID."
    )

    id_verifikasi = st.text_input(
        "Masukkan ID Pemilih",
        placeholder="Contoh: IF-2026-001"
    )

    if st.button(
        "Periksa Status",
        type="primary"
    ):

        id_bersih = id_verifikasi.strip()

        if not id_bersih:

            st.error(
                "Masukkan ID pemilih terlebih dahulu."
            )

        else:

            sudah = sudah_memilih(id_bersih)

            col1, col2 = st.columns(2)

            col1.metric(
                "Status Wallet",
                "Simulasi Aktif"
            )

            col2.metric(
                "Status Voting",
                "Sudah Memilih" if sudah else "Belum Memilih"
            )

            if sudah:

                st.success(
                    "ID ditemukan dalam catatan voting."
                )

            else:

                st.warning(
                    "Belum ditemukan suara untuk ID ini."
                )

            st.info(
                "Wallet masih berupa simulasi dan belum "
                "terhubung ke wallet blockchain sungguhan."
            )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "E-Voting UIN Siber Syekh Nurjati Cirebon"
)

st.caption(
    "Prototype akademik berbasis Python Blockchain. "
    "Data tersimpan selama sesi aplikasi berjalan."
)
