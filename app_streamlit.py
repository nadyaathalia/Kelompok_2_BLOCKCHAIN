import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from block import Block, EVotingBlockchain

# Set page configuration
st.set_page_config(
    page_title="E-Voting Berbasis Blockchain",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .block-card {
        background-color: #F8FAFC;
        border: 2px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        font-family: 'Courier New', monospace;
    }
    .block-header {
        font-weight: 700;
        color: #1E40AF;
        border-bottom: 1px solid #CBD5E1;
        padding-bottom: 6px;
        margin-bottom: 10px;
    }
    .hash-text {
        word-break: break-all;
        background: #EEF2FF;
        color: #3730A3;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .prev-hash-text {
        word-break: break-all;
        background: #F1F5F9;
        color: #475569;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Blockchain di Session State
if "evote" not in st.session_state:
    st.session_state.evote = EVotingBlockchain(difficulty=2)
    # Masukkan data sampel awal
    sample_voters = [
        ("NIM101", "Ahmad Fauzi"),
        ("NIM102", "Bella Safitri"),
        ("NIM103", "Candra Wijaya"),
        ("NIM104", "Dina Mariana"),
        ("NIM105", "Eko Prasetyo")
    ]
    for vid, name in sample_voters:
        st.session_state.evote.register_voter(vid, name)
    # Masukkan suara awal
    st.session_state.evote.cast_vote("NIM101", 0)
    st.session_state.evote.cast_vote("NIM102", 1)
    st.session_state.evote.cast_vote("NIM103", 0)

evote = st.session_state.evote

# Sidebar
with st.sidebar:
    st.title("🗳️ E-Voting Blockchain")
    st.markdown("**Kelompok 2 - Blockchain Project**")
    st.info("""
    Sistem pemilihan elektronik yang memanfaatkan teknologi **Blockchain**:
    - 🔒 **Kriptografi SHA-256**
    - ⛏️ **Proof of Work Consensus**
    - 👤 **Anonimitas Pemilih**
    - 🛡️ **Pencegahan Double-Voting**
    - 🔗 **Immutability (Anti Manipulasi)**
    """)
    
    st.divider()
    st.write(f"⚙️ **Target Kesulitan (PoW):** `{evote.difficulty} digit nol ('00')`")
    st.write(f"📦 **Jumlah Blok:** `{len(evote.chain)} blok`")
    st.write(f"👥 **Pemilih Terdaftar:** `{len(evote.voters)} orang`")
    
    st.divider()
    if st.button("🔄 Reset ke Kondisi Awal"):
        st.session_state.clear()
        st.rerun()

# Header Halaman
st.markdown('<p class="main-header">Sistem E-Voting Berbasis Blockchain</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Pemilihan Umum Ketua Organisasi • Aman, Transparan, dan Terdesentralisasi</p>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🗳️ Bilik Suara (Voting)",
    "📊 Hasil Perhitungan (Tally)",
    "⛓️ Blockchain Explorer",
    "🛡️ Audit & Demo Keamanan"
])

# =============================================================================
# TAB 1: BILIK SUARA
# =============================================================================
with tab1:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("1. Identitas Pemilih")
        st.caption("Masukkan NIM/NIK Anda untuk verifikasi hak suara.")

        voter_id = st.text_input("NIM / NIK Pemilih", placeholder="Contoh: NIM104")
        voter_name = st.text_input("Nama Lengkap (Khusus jika belum terdaftar)", placeholder="Contoh: Dina Mariana")

        # Cek status pemilih
        status_box = st.empty()
        if voter_id:
            vid_clean = voter_id.strip()
            if vid_clean in evote.voters:
                info = evote.voters[vid_clean]
                if info["has_voted"]:
                    status_box.error(f"⚠️ Pemilih **{info['name']}** sudah pernah menggunakan hak suara!")
                else:
                    status_box.success(f"✔ Terdaftar atas nama: **{info['name']}** (Belum Memilih)")
            else:
                status_box.info("ℹ️ ID belum terdaftar di DPT. Anda akan didaftarkan otomatis saat mencoblos jika nama diisi.")

    with col_right:
        st.subheader("2. Pilih Pasangan Kandidat")
        candidate_choice = st.radio(
            "Tentukan pilihan Anda:",
            options=range(len(evote.candidates)),
            format_func=lambda i: evote.candidates[i],
            index=0
        )

        st.write("")
        submit_vote = st.button("🗳️ Coblos Sekarang (Kirim ke Blockchain)", type="primary", use_container_width=True)

        if submit_vote:
            if not voter_id.strip():
                st.error("Harap masukkan NIM/NIK Pemilih terlebih dahulu!")
            else:
                vid_clean = voter_id.strip()
                # Daftarkan jika belum terdaftar
                if vid_clean not in evote.voters:
                    if not voter_name.strip():
                        st.error("ID belum terdaftar! Silakan isi Nama Lengkap untuk pendaftaran DPT baru.")
                        st.stop()
                    evote.register_voter(vid_clean, voter_name)

                with st.spinner("⛏️ Menjalankan Konsensus Proof of Work (Mining Block)..."):
                    time.sleep(0.4) # Animasi mining
                    start_t = time.time()
                    success, result = evote.cast_vote(vid_clean, candidate_choice)
                    duration = time.time() - start_t

                if success:
                    st.balloons()
                    st.success("🎉 **Suara Anda Berhasil Dicatat ke Dalam Blockchain!**")
                    st.json({
                        "Nomor Blok": f"#{result['block_index']}",
                        "Kandidat Pilihan": result['candidate'],
                        "Hash Blok": result['block_hash'],
                        "Proof of Work Nonce": result['nonce'],
                        "Waktu Mining": f"{duration:.4f} detik",
                        "Token Anonim (Voter Hash)": result['voter_hash']
                    })
                else:
                    st.error(f"❌ {result}")

# =============================================================================
# TAB 2: HASIL PERHITUNGAN SUARA (TALLY)
# =============================================================================
with tab2:
    st.subheader("📊 Rekapitulasi Suara Real-Time")
    st.caption("Hasil dihitung langsung dari seluruh blok yang tercatat di Blockchain secara transparan.")

    stats = evote.tally_votes()

    # Metrics Bar
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Pemilih Terdaftar (DPT)", f"{stats['total_registered']} Orang")
    m2.metric("Total Suara Sah Masuk", f"{stats['total_votes']} Suara")
    m3.metric("Tingkat Partisipasi", f"{stats['participation_rate']:.1f}%")

    st.divider()

    chart_col, table_col = st.columns([1.5, 1])

    with chart_col:
        df_tally = pd.DataFrame(list(stats['tally'].items()), columns=["Kandidat", "Jumlah Suara"])
        st.bar_chart(df_tally.set_index("Kandidat"), color="#2563EB")

    with table_col:
        st.write("**Rincian Perolehan:**")
        for cand, count in stats['tally'].items():
            persen = (count / stats['total_votes'] * 100) if stats['total_votes'] > 0 else 0
            st.write(f"**{cand}**")
            st.progress(persen / 100)
            st.caption(f"{count} suara ({persen:.1f}%)")

# =============================================================================
# TAB 3: BLOCKCHAIN EXPLORER
# =============================================================================
with tab3:
    st.subheader("⛓️ Rantai Blok (Ledger Publik)")
    st.caption("Setiap blok menyimpan riwayat transaksi suara yang saling mengunci dengan hash kriptografi SHA-256.")

    for i, block in enumerate(evote.chain):
        is_genesis = (block.index == 0)
        badge_color = "🟢 GENESIS BLOCK" if is_genesis else f"🗳️ BLOK SUARA #{block.index}"

        with st.container():
            st.markdown(f"""
            <div class="block-card">
                <div class="block-header">
                    <span>{badge_color}</span> | 🕒 <span>{block.timestamp}</span> | ⛏️ Nonce: <b>{block.nonce}</b>
                </div>
                <div><b>Data Payload:</b></div>
                <pre style="background:#FFFFFF; padding:8px; border-radius:6px; border:1px solid #E2E8F0; font-size:0.85rem;">{json.dumps(block.vote_data, indent=2, ensure_ascii=False)}</pre>
                <div style="margin-top:8px;">
                    <div><b>Previous Hash:</b></div>
                    <div class="prev-hash-text">{block.previous_hash}</div>
                </div>
                <div style="margin-top:8px;">
                    <div><b>Block Hash (SHA-256):</b></div>
                    <div class="hash-text">{block.hash}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if i < len(evote.chain) - 1:
                st.markdown("<div style='text-align:center; color:#2563EB; font-size:1.5rem; margin:-5px 0 10px 0;'>🔗 ▼ Terhubung secara kriptografis</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 4: AUDIT & DEMO KEAMANAN
# =============================================================================
with tab4:
    st.subheader("🛡️ Audit Integritas & Simulasi Peretasan Data")
    st.caption("Buktikan bahwa data suara di blockchain tidak dapat diubah (immutable). Sekali diubah, rantai akan langsung rusak!")

    # Cek Status Validitas Saat Ini
    is_valid, validation_msg = evote.is_chain_valid()
    if is_valid:
        st.success(f"✅ **STATUS BLOCKCHAIN: VALID & AMAN**\n\n{validation_msg}")
    else:
        st.error(f"🚨 **STATUS BLOCKCHAIN: TERDETEKSI KECURANGAN / MANIPULASI!**\n\n{validation_msg}")

    st.divider()

    st.subheader("🧪 Simulasi Peretasan (Tamper Demonstration)")
    st.markdown("""
    Coba ubah isi suara pada salah satu blok tanpa melalui konsensus penambangan (mining), 
    lalu perhatikan bagaimana algoritma kriptografi mendeteksi kecurangan tersebut seketika.
    """)

    if len(evote.chain) <= 1:
        st.info("Belum ada blok suara yang dapat dimanipulasi. Silakan masukkan suara terlebih dahulu di Tab Bilik Suara.")
    else:
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            target_block_idx = st.selectbox(
                "Pilih Blok yang Ingin Direkayasa:",
                options=list(range(1, len(evote.chain))),
                format_func=lambda idx: f"Blok #{idx} (Saat ini: {evote.chain[idx].vote_data.get('candidate')})"
            )
        
        with col_t2:
            fake_candidate = st.text_input(
                "Ganti Pilihan Suara Menjadi:",
                value="Kandidat 99 - Rekayasa Hacker (Ilegal)"
            )

        if st.button("⚠️ Lakukan Manipulasi Data Suara", type="secondary"):
            ok, msg = evote.tamper_block(target_block_idx, fake_candidate)
            st.warning(msg)
            st.rerun()

