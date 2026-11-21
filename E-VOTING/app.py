
from collections import Counter
import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

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

DEPLOYMENT_PATH = Path(__file__).resolve().parent.parent / "deployment.json"
DEPLOYMENT = json.loads(DEPLOYMENT_PATH.read_text(encoding="utf-8"))
CONTRACT_ADDRESS = DEPLOYMENT["address"]
CONTRACT_CHAIN_ID = int(DEPLOYMENT["chainId"])

if "role" not in st.session_state:
    st.session_state.role = None


WALLET_COMPONENT_HTML = """
<div class="evm-wallet">
  <button class="evm-connect" type="button">Hubungkan MetaMask</button>
  <div class="evm-form" hidden>
    <label class="evm-id-label">ID Pemilih</label>
    <input class="evm-voter-id" type="text"
      placeholder="Contoh: IF-2026-001" />
    <div class="evm-candidate-field">
      <label>Kandidat</label>
      <select class="evm-candidate"></select>
    </div>
    <button class="evm-action" type="button"></button>
  </div>
  <p class="evm-status" aria-live="polite"></p>
</div>
"""

WALLET_COMPONENT_CSS = """
.evm-wallet {
  font-family: sans-serif;
  padding: 0.25rem 0;
}
.evm-wallet button {
  width: 100%;
  min-height: 2.5rem;
  border: 0;
  border-radius: 0.5rem;
  padding: 0.55rem 0.8rem;
  background: #f6851b;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}
.evm-wallet button:disabled {
  cursor: wait;
  opacity: 0.65;
}
.evm-wallet label {
  display: block;
  margin: 0.75rem 0 0.3rem;
  font-weight: 600;
}
.evm-wallet input, .evm-wallet select {
  box-sizing: border-box;
  width: 100%;
  min-height: 2.4rem;
  padding: 0.4rem;
}
.evm-wallet .evm-action {
  margin-top: 0.75rem;
}
.evm-wallet .evm-status {
  overflow-wrap: anywhere;
  margin-bottom: 0;
}
"""

WALLET_COMPONENT_JS = """
export default function(component) {
  const { parentElement: root, data, setStateValue } = component;
  const connectButton = root.querySelector(".evm-connect");
  const form = root.querySelector(".evm-form");
  const idInput = root.querySelector(".evm-voter-id");
  const candidateField = root.querySelector(".evm-candidate-field");
  const candidateSelect = root.querySelector(".evm-candidate");
  const actionButton = root.querySelector(".evm-action");
  const status = root.querySelector(".evm-status");
  const mode = data.mode;

  form.hidden = !["register", "vote", "verify"].includes(mode);
  candidateField.hidden = mode !== "vote";
  connectButton.textContent = data.account
    ? `MetaMask: ${data.account.slice(0, 6)}...${data.account.slice(-4)}`
    : "Hubungkan MetaMask";
  status.textContent = data.status || "";

  idInput.value = data.voter_id || "";
  idInput.disabled = false;
  if (mode === "register") {
    root.querySelector(".evm-id-label").textContent = "ID Pemilih yang akan didaftarkan";
    actionButton.textContent = "Daftarkan Pemilih On-chain";
  } else if (mode === "vote") {
    root.querySelector(".evm-id-label").textContent = "ID Pemilih";
    actionButton.textContent = "Kirim Vote via MetaMask";
    const candidates = data.candidates || [];
    if (candidateSelect.options.length !== candidates.length) {
      candidateSelect.replaceChildren();
      for (const candidate of candidates) {
        const option = document.createElement("option");
        option.value = candidate;
        option.textContent = candidate;
        candidateSelect.appendChild(option);
      }
    }
    if (candidates.includes(data.candidate)) {
      candidateSelect.value = data.candidate;
    }
  } else if (mode === "verify") {
    root.querySelector(".evm-id-label").textContent = "ID Pemilih untuk verifikasi";
    actionButton.textContent = "Periksa Status On-chain";
  }

  async function request(method, params = []) {
    return window.ethereum.request({ method, params });
  }

  function setStatus(message) {
    status.textContent = message;
    setStateValue("status", message);
  }

  function encodeStringCall(selector, values) {
    const head = [];
    const tail = [];
    let offset = values.length * 32;

    for (const value of values) {
      const bytes = new TextEncoder().encode(value);
      let encoded = BigInt(bytes.length).toString(16).padStart(64, "0");
      for (const byte of bytes) {
        encoded += byte.toString(16).padStart(2, "0");
      }
      const paddedLength = Math.ceil((encoded.length - 64) / 64) * 64;
      encoded = encoded.padEnd(64 + paddedLength, "0");
      head.push(BigInt(offset).toString(16).padStart(64, "0"));
      tail.push(encoded);
      offset += encoded.length / 2;
    }

    return selector + head.join("") + tail.join("");
  }

  function wordAt(encoded, index) {
    const start = 2 + index * 64;
    return BigInt(`0x${encoded.slice(start, start + 64)}`);
  }

  function stringAt(encoded, index) {
    const offset = Number(wordAt(encoded, index));
    const length = Number(wordAt(`0x${encoded.slice(2 + offset * 2)}`, 0));
    const start = 2 + (offset + 32) * 2;
    const value = encoded.slice(start, start + length * 2);
    const bytes = value
      ? new Uint8Array(value.match(/.{2}/g).map(byte => parseInt(byte, 16)))
      : new Uint8Array();
    return new TextDecoder().decode(bytes);
  }

  async function ensureWallet() {
    if (!window.ethereum) {
      throw new Error("MetaMask tidak ditemukan. Pasang ekstensi MetaMask terlebih dahulu.");
    }

    let accounts = await request("eth_accounts");
    if (!accounts.length) {
      accounts = await request("eth_requestAccounts");
    }
    if (!accounts.length) {
      throw new Error("Tidak ada akun MetaMask yang dipilih.");
    }

    const expectedChainId = `0x${Number(data.chain_id).toString(16)}`;
    let chainId = await request("eth_chainId");
    if (chainId.toLowerCase() !== expectedChainId.toLowerCase()) {
      try {
        await request("wallet_switchEthereumChain", [{ chainId: expectedChainId }]);
      } catch (error) {
        if (error.code !== 4902) {
          throw error;
        }
        await request("wallet_addEthereumChain", [{
          chainId: expectedChainId,
          chainName: "Hardhat Localhost",
          nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 },
          rpcUrls: ["http://127.0.0.1:8545"]
        }]);
        await request("wallet_switchEthereumChain", [{ chainId: expectedChainId }]);
      }
      chainId = await request("eth_chainId");
    }

    if (chainId.toLowerCase() !== expectedChainId.toLowerCase()) {
      throw new Error(`Pilih jaringan dengan chain ID ${data.chain_id}.`);
    }
    setStateValue("account", accounts[0]);
    return accounts[0];
  }

  async function contractCall(callData, account) {
    return request("eth_call", [
      { to: data.contract_address, from: account, data: callData },
      "latest"
    ]);
  }

  async function readVoter(voterId, account) {
    const result = await contractCall(
      encodeStringCall("0x68873682", [voterId]),
      account
    );
    return {
      id: stringAt(result, 0),
      candidate: stringAt(result, 1),
      voted: wordAt(result, 4) !== 0n,
      tokenId: wordAt(result, 5).toString()
    };
  }

  async function sendTransaction(account, callData) {
    const txHash = await request("eth_sendTransaction", [{
      from: account,
      to: data.contract_address,
      data: callData
    }]);
    setStateValue("tx_hash", txHash);
    setStatus(`Transaksi dikirim: ${txHash}. Menunggu konfirmasi blockchain...`);

    for (let attempt = 0; attempt < 90; attempt++) {
      const receipt = await request("eth_getTransactionReceipt", [txHash]);
      if (receipt) {
        if (BigInt(receipt.status) !== 1n) {
          throw new Error(`Transaksi gagal. Hash: ${txHash}`);
        }
        setStatus(`Transaksi terkonfirmasi di blok ${BigInt(receipt.blockNumber)}.`);
        return;
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    setStatus(`Transaksi masih menunggu konfirmasi. Hash: ${txHash}`);
  }

  connectButton.onclick = async () => {
    connectButton.disabled = true;
    try {
      const account = await ensureWallet();
      connectButton.textContent = `MetaMask: ${account.slice(0, 6)}...${account.slice(-4)}`;
      setStatus(`Terhubung ke ${account} pada chain ${data.chain_id}.`);
    } catch (error) {
      setStatus(error.code === 4001 ? "Permintaan MetaMask ditolak." : error.message);
    } finally {
      connectButton.disabled = false;
    }
  };

  actionButton.onclick = async () => {
    actionButton.disabled = true;
    try {
      const account = await ensureWallet();
      const voterId = idInput.value.trim();
      if (!voterId) {
        throw new Error("ID Pemilih wajib diisi.");
      }
      setStateValue("voter_id", voterId);

      if (mode === "register") {
        const adminResult = await contractCall("0xf851a440", account);
        const admin = `0x${adminResult.slice(-40)}`.toLowerCase();
        if (admin !== account.toLowerCase()) {
          throw new Error("Akun MetaMask ini bukan admin smart contract.");
        }
        const callData = encodeStringCall("0x8d2ed40d", [voterId]);
        await sendTransaction(account, callData);
      } else if (mode === "vote") {
        const voter = await readVoter(voterId, account);
        if (!voter.id) {
          throw new Error("ID belum didaftarkan oleh admin pada smart contract.");
        }
        if (voter.voted) {
          throw new Error(`ID ini sudah memilih on-chain (NFT #${voter.tokenId}).`);
        }
        const candidate = candidateSelect.value;
        const callData = encodeStringCall("0x234ee111", [
          voterId,
          candidate,
          "Pemilihan Ketua",
          "Online"
        ]);
        setStateValue("candidate", candidate);
        await sendTransaction(account, callData);
      } else if (mode === "verify") {
        const voter = await readVoter(voterId, account);
        if (!voter.id) {
          setStatus("ID tidak terdaftar pada smart contract.");
        } else if (voter.voted) {
          setStateValue("tx_hash", "");
          setStatus(`Sudah memilih on-chain. Kandidat: ${voter.candidate}. NFT #${voter.tokenId}.`);
        } else {
          setStateValue("tx_hash", "");
          setStatus("Terdaftar, tetapi belum memilih on-chain.");
        }
      }
    } catch (error) {
      setStatus(error.code === 4001 ? "Transaksi ditolak di MetaMask." : error.message);
    } finally {
      actionButton.disabled = false;
    }
  };
}
"""

evm_wallet_component = st.components.v2.component(
    "e_voting_metamask",
    html=WALLET_COMPONENT_HTML,
    css=WALLET_COMPONENT_CSS,
    js=WALLET_COMPONENT_JS
)


def render_evm_wallet(mode, key, voter_id="", candidate=""):
    component_state = st.session_state.get(key, {})
    defaults = {
        "account": "",
        "status": "",
        "tx_hash": "",
        "voter_id": voter_id,
        "candidate": candidate
    }
    defaults.update(component_state)
    data = {
        "mode": mode,
        "contract_address": CONTRACT_ADDRESS,
        "chain_id": CONTRACT_CHAIN_ID,
        "candidates": NAMA_KANDIDAT,
        "account": defaults["account"],
        "status": defaults["status"],
        "voter_id": voter_id or defaults["voter_id"],
        "candidate": candidate or defaults["candidate"]
    }
    result = evm_wallet_component(
        data=data,
        default=defaults,
        key=key,
        on_account_change=lambda: None,
        on_status_change=lambda: None,
        on_tx_hash_change=lambda: None,
        on_voter_id_change=lambda: None,
        on_candidate_change=lambda: None
    )
    if defaults["tx_hash"]:
        st.caption("Transaction hash")
        st.code(defaults["tx_hash"])
    return result



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
    <h1>🗳️ E-Voting UINSSC</h1>
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


class EVMRPCError(Exception):
    pass


def hitung_suara_onchain():

    request_data = json.dumps({
        "jsonrpc": "2.0",
        "method": "eth_getLogs",
        "params": [{
            "address": CONTRACT_ADDRESS,
            "fromBlock": "0x0",
            "toBlock": "latest",
            "topics": [
                "0x55073e5aae3ae81e4d5634220132a0aab9b2a4ccbcda83211ef0d9c476982517"
            ]
        }],
        "id": 1
    }).encode("utf-8")
    request = Request(
        "http://127.0.0.1:8545",
        data=request_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=10) as response:
            rpc_response = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise EVMRPCError(
            "Tidak dapat membaca hasil on-chain. Pastikan node Hardhat "
            "berjalan di http://127.0.0.1:8545."
        ) from error

    if "error" in rpc_response:
        raise EVMRPCError(
            f"Node EVM gagal membaca hasil: {rpc_response['error'].get('message', 'RPC error')}"
        )

    logs = rpc_response.get("result")
    if not isinstance(logs, list):
        raise EVMRPCError("Respons node EVM untuk hasil vote tidak valid.")

    totals = Counter()
    for log in logs:
        try:
            event_data = bytes.fromhex(log["data"][2:])
            candidate_offset = int.from_bytes(event_data[:32], "big")
            candidate_length = int.from_bytes(
                event_data[candidate_offset:candidate_offset + 32],
                "big"
            )
            candidate_start = candidate_offset + 32
            candidate_end = candidate_start + candidate_length
            candidate = event_data[candidate_start:candidate_end].decode("utf-8")
        except (KeyError, ValueError, UnicodeDecodeError, IndexError) as error:
            raise EVMRPCError(
                "Data event vote pada blockchain tidak dapat dibaca."
            ) from error

        totals[candidate] += 1

    return totals


def simpan_suara(id_pemilih, kandidat):

    blockchain.add_block({
        "id_pemilih": id_pemilih,
        "kandidat": kandidat,
        "pemilihan": "Pemilihan Ketua"
    })

# =====================================================
# SIDEBAR / NAVIGASI
# =====================================================

if st.session_state.role is None:

    st.subheader("Selamat datang di E-Voting")
    st.caption("Pilih role untuk melanjutkan.")

    st.info(
        f"Smart contract: `{CONTRACT_ADDRESS}` · "
        f"Jaringan: {DEPLOYMENT['network']} (chain ID {CONTRACT_CHAIN_ID})"
    )
    render_evm_wallet("connect", "evm_wallet")

    st.divider()

    col_admin, col_pemilih = st.columns(2)

    with col_admin:

        with st.container(border=True):

            st.markdown("### 🛡️ Admin")
            st.write(
                "Kelola pemilihan, pantau hasil, dan verifikasi status pemilih."
            )

            if st.button(
                "Masuk sebagai Admin",
                key="pilih_role_admin",
                type="primary",
                use_container_width=True
            ):

                st.session_state.role = "Admin"
                st.rerun()

    with col_pemilih:

        with st.container(border=True):

            st.markdown("### 🗳️ Pemilih")
            st.write(
                "Lihat informasi kandidat dan berikan suara."
            )

            if st.button(
                "Masuk sebagai Pemilih",
                key="pilih_role_pemilih",
                use_container_width=True
            ):

                st.session_state.role = "Pemilih"
                st.rerun()

    st.stop()

with st.sidebar:

    st.title("🗳️ E-Voting UIN")

    st.caption("Prototype Akademik")
    st.caption(f"Role: {st.session_state.role}")
    render_evm_wallet("connect", "evm_wallet")

    st.divider()

    halaman_role = {
        "Admin": [
            "Dashboard",
            "Voter Registration",
            "Candidate List",
            "Voting Results",
            "Voter Verification"
        ],
        "Pemilih": [
            "Candidate List",
            "Voting Page"
        ]
    }

    halaman = st.radio(
        "NAVIGASI",
        halaman_role[st.session_state.role]
    )

    st.divider()

    if st.button("Ganti Role", use_container_width=True):

        st.session_state.role = None
        st.rerun()

    st.divider()

    st.markdown("### KELOMPOK :")

    st.caption("Irwan")
    st.caption("Akbar")
    st.caption("Nadya")



# =====================================================
# DIALOG KONFIRMASI
# =====================================================

@st.dialog("Konfirmasi Pilihan")
def dialog_konfirmasi(id_pemilih, kandidat):

    st.caption("Ini adalah vote simulasi Python, bukan transaksi MetaMask.")

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

                st.success("Suara simulasi berhasil dicatat.")

                st.rerun()


# =====================================================
# HALAMAN 1 — DASHBOARD
# =====================================================

if halaman == "Dashboard":

    st.subheader("📊 Dashboard Pemilihan")

    st.caption(
        "Ringkasan kondisi pemungutan suara saat ini."
    )

    total_suara_simulasi = len(votes)
    try:
        total_suara_onchain = sum(hitung_suara_onchain().values())
        error_onchain = None
    except EVMRPCError as error:
        total_suara_onchain = None
        error_onchain = str(error)

    status_chain = (
        "Valid"
        if blockchain.is_valid()
        else "Tidak Valid"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Pemilih Terdaftar",
        TOTAL_PEMILIH
    )

    col2.metric(
        "Jumlah Kandidat",
        len(KANDIDAT)
    )

    col3.metric(
        "Total Suara Masuk (On-chain)",
        total_suara_onchain if total_suara_onchain is not None else "—"
    )

    col4.metric(
        "Suara Simulasi Python",
        total_suara_simulasi
    )

    col5.metric(
        "Status Pemilihan",
        "Aktif"
    )

    if error_onchain:
        st.error(error_onchain)

    st.divider()

    st.subheader("🔗 Status Blockchain")
    st.caption(
        f"Kontrak EVM: {CONTRACT_ADDRESS} · "
        f"{DEPLOYMENT['network']} (chain ID {CONTRACT_CHAIN_ID})"
    )

    if blockchain.is_valid():

        st.success("Blockchain valid dan terhubung.")

    else:

        st.error("Blockchain tidak valid.")

    st.divider()

    st.subheader("📋 Aktivitas Simulasi Python Terbaru")

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

elif halaman == "Voter Registration":

    st.subheader("🧾 Pendaftaran Pemilih On-chain")
    st.caption(
        "Pendaftaran ini menambahkan ID pemilih ke smart contract "
        "menggunakan transaksi yang ditandatangani MetaMask."
    )
    st.warning(
        "Hanya wallet admin yang digunakan saat deployment kontrak "
        "dapat mendaftarkan pemilih."
    )
    render_evm_wallet("register", "evm_register")


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

        st.success("Suara simulasi berhasil dicatat pada blockchain Python.")

    st.divider()
    st.subheader("Vote melalui MetaMask (Smart Contract)")
    st.caption(
        "Vote on-chain adalah alur terpisah dari simulasi Python di atas. "
        "ID pemilih harus didaftarkan admin pada kontrak terlebih dahulu."
    )
    st.warning(
        "Kontrak saat ini menyimpan ID pemilih dan kandidat secara publik "
        "di blockchain dan tidak mengikat ID ke wallet tertentu. Jangan "
        "gunakan untuk pemilu sungguhan atau yang membutuhkan kerahasiaan suara."
    )
    render_evm_wallet(
        "vote",
        "evm_vote",
        voter_id=id_pemilih,
        candidate=kandidat_dipilih
    )


# =====================================================
# HALAMAN 4 — VOTING RESULTS
# =====================================================

elif halaman == "Voting Results":

    st.subheader("📈 Voting Results")

    st.caption(
        f"Hasil vote dari event smart contract `{CONTRACT_ADDRESS}` "
        f"pada chain ID {CONTRACT_CHAIN_ID}."
    )

    st.button("Perbarui hasil on-chain", key="refresh_onchain_results")

    try:
        with st.spinner("Membaca hasil vote dari blockchain..."):
            totals_onchain = hitung_suara_onchain()
    except EVMRPCError as error:
        st.error(str(error))
    else:
        kandidat_lain = sorted(
            kandidat
            for kandidat in totals_onchain
            if kandidat not in NAMA_KANDIDAT
        )

        data_onchain = [
            {
                "Kandidat": kandidat,
                "Jumlah Suara": totals_onchain.get(kandidat, 0)
            }
            for kandidat in NAMA_KANDIDAT + kandidat_lain
        ]

        total_onchain = sum(totals_onchain.values())

        st.metric("Total Suara On-chain", total_onchain)

        if total_onchain:
            fig = px.bar(
                data_onchain,
                x="Kandidat",
                y="Jumlah Suara",
                color="Kandidat",
                text="Jumlah Suara",
                title="Perolehan Suara On-chain"
            )
            fig.update_layout(
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis_title="Jumlah Suara",
                xaxis_title="Kandidat"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada vote yang tercatat pada smart contract.")

        st.subheader("Rekapitulasi Suara On-chain")
        st.dataframe(
            data_onchain,
            use_container_width=True,
            hide_index=True
        )

        if total_onchain:
            st.subheader("Persentase Suara On-chain")
            for item in data_onchain:
                persen = item["Jumlah Suara"] / total_onchain * 100
                st.write(
                    f"**{item['Kandidat']}** — "
                    f"{item['Jumlah Suara']} suara ({persen:.1f}%)"
                )
                st.progress(persen / 100)

    with st.expander("Hasil simulasi Python (terpisah dari on-chain)"):
        totals_python = hitung_suara()
        data_simulasi = [
            {
                "Kandidat": kandidat,
                "Jumlah Suara": totals_python.get(kandidat, 0)
            }
            for kandidat in NAMA_KANDIDAT
        ]
        st.metric(
            "Total Suara Simulasi Python",
            sum(totals_python.values())
        )
        st.dataframe(
            data_simulasi,
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
                "Mode",
                "Simulasi Aktif"
            )

            col2.metric(
                "Status Simulasi Python",
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
                "Status di atas hanya berasal dari simulasi Python "
                "pada sesi aplikasi ini."
            )

    st.divider()
    st.subheader("Verifikasi pada Smart Contract")
    st.caption(
        "Pemeriksaan ini membaca status pemilih dari jaringan EVM "
        "menggunakan MetaMask."
    )
    render_evm_wallet(
        "verify",
        "evm_verify",
        voter_id=id_verifikasi
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
