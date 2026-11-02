import streamlit as st
import streamlit.components.v2 as components
from web3 import Web3

# =========================================================
# KONFIGURASI
# =========================================================

RPC_URL = "http://127.0.0.1:8545"

st.set_page_config(
    page_title="E-Voting Inventaris",
    page_icon="🗳️",
    layout="centered",
)

st.title("🗳️ E-Voting Inventaris")
st.caption(
    "Aplikasi Blockchain untuk Pencatatan Voting Berbasis NFT"
)

# =========================================================
# KOMPONEN JAVASCRIPT UNTUK METAMASK
# =========================================================

WALLET_HTML = """
<div>
  <button id="connect-wallet" type="button">
    Connect Wallet
  </button>
  <p id="wallet-status">Wallet belum terhubung.</p>
</div>
"""

WALLET_CSS = """
button {
    padding: 0.7rem 1rem;
    border: none;
    border-radius: 8px;
    background: var(--st-primary-color);
    color: white;
    font-weight: 600;
    cursor: pointer;
}

p {
    color: var(--st-text-color);
    overflow-wrap: anywhere;
}
"""

WALLET_JS = """
export default function(component) {
    const { parentElement, setStateValue } = component;

    const button = parentElement.querySelector("#connect-wallet");
    const status = parentElement.querySelector("#wallet-status");

    let mounted = true;

    async function readWallet() {
        if (!window.ethereum) {
            return;
        }

        const accounts = await window.ethereum.request({
            method: "eth_accounts"
        });

        const chainId = await window.ethereum.request({
            method: "eth_chainId"
        });

        if (!mounted) return;

        if (accounts && accounts.length > 0) {
            setStateValue("wallet", {
                address: accounts[0],
                chainId: chainId,
                connected: true
            });
            status.textContent = "Wallet terhubung: " + accounts[0];
        } else {
            setStateValue("wallet", {
                address: "",
                chainId: chainId,
                connected: false
            });
            status.textContent = "Wallet belum terhubung.";
        }
    }

    async function connectWallet() {
        if (!window.ethereum) {
            status.textContent =
                "MetaMask tidak ditemukan. Pasang ekstensi MetaMask.";
            return;
        }

        try {
            status.textContent =
                "Menunggu persetujuan akses akun...";

            await window.ethereum.request({
                method: "eth_requestAccounts"
            });

            await readWallet();
        } catch (error) {
            status.textContent =
                "Koneksi gagal: " +
                (error.message || "Kesalahan tidak diketahui");
        }
    }

    function onAccountsChanged(accounts) {
        if (!mounted) return;

        window.ethereum.request({ method: "eth_chainId" })
            .then((chainId) => {
                if (!mounted) return;

                if (accounts && accounts.length > 0) {
                    setStateValue("wallet", {
                        address: accounts[0],
                        chainId: chainId,
                        connected: true
                    });
                    status.textContent =
                        "Wallet terhubung: " + accounts[0];
                } else {
                    setStateValue("wallet", {
                        address: "",
                        chainId: chainId,
                        connected: false
                    });
                    status.textContent = "Akun tidak terhubung.";
                }
            })
            .catch(() => {});
    }

    function onChainChanged(chainId) {
        if (!mounted) return;

        window.ethereum.request({ method: "eth_accounts" })
            .then((accounts) => {
                if (!mounted) return;

                setStateValue("wallet", {
                    address: accounts && accounts.length > 0
                        ? accounts[0]
                        : "",
                    chainId: chainId,
                    connected: Boolean(accounts && accounts.length > 0)
                });
            })
            .catch(() => {});
    }

    button.addEventListener("click", connectWallet);

    if (window.ethereum) {
        window.ethereum.on("accountsChanged", onAccountsChanged);
        window.ethereum.on("chainChanged", onChainChanged);

        // Baca koneksi yang sudah pernah diberikan izin.
        readWallet().catch(() => {});
    }

    return () => {
        mounted = false;
        button.removeEventListener("click", connectWallet);

        if (window.ethereum && window.ethereum.removeListener) {
            window.ethereum.removeListener(
                "accountsChanged", onAccountsChanged
            );
            window.ethereum.removeListener(
                "chainChanged", onChainChanged
            );
        }
    };
}
"""

wallet_component = components.component(
    name="coffee_metamask_wallet",
    html=WALLET_HTML,
    css=WALLET_CSS,
    js=WALLET_JS,
)

# =========================================================
# 1. KONEKSI KE HARDHAT RPC
# =========================================================

st.subheader("1. Status Blockchain Lokal")

w3 = Web3(
    Web3.HTTPProvider(
        RPC_URL,
        request_kwargs={"timeout": 5},
    )
)

rpc_connected = w3.is_connected()

if rpc_connected:
    st.success("Blockchain Hardhat berhasil dihubungkan.")

    col1, col2 = st.columns(2)

    col1.metric(
        "Chain ID RPC",
        w3.eth.chain_id,
    )

    col2.metric(
        "Block Terbaru",
        w3.eth.block_number,
    )

    st.code(RPC_URL)
else:
    st.error(
        "Hardhat RPC tidak dapat diakses. "
        "Jalankan 'npx hardhat node' pada terminal lain."
    )

# =========================================================
# 2. KONEKSI METAMASK
# =========================================================

st.divider()
st.subheader("2. Hubungkan MetaMask")

wallet_result = wallet_component(
    key="coffee_metamask",
    default={
        "wallet": {
            "address": "",
            "chainId": "",
            "connected": False,
        }
    },
    on_wallet_change=lambda: None,
)

wallet = wallet_result.wallet

# =========================================================
# 3. INFORMASI WALLET DAN SALDO
# =========================================================

st.divider()
st.subheader("3. Informasi Wallet")

if wallet and wallet.get("connected") and wallet.get("address"):
    address = Web3.to_checksum_address(wallet["address"])

    st.success("Wallet berhasil terhubung.")

    st.write("Alamat wallet:")
    st.code(address)

    try:
        wallet_chain_id = int(wallet["chainId"], 16)
        st.metric("Chain ID MetaMask", wallet_chain_id)

        if not rpc_connected:
            st.warning(
                "Wallet terhubung, tetapi RPC tidak tersedia. "
                "Saldo belum dapat dibaca."
            )

        elif wallet_chain_id != w3.eth.chain_id:
            st.warning(
                "Jaringan MetaMask berbeda dengan jaringan RPC Python. "
                "Pilih jaringan Hardhat Local pada MetaMask."
            )

        else:
            st.success("Jaringan wallet sesuai dengan RPC.")

            if st.button("Periksa Saldo ETH", type="primary"):
                try:
                    balance_wei = w3.eth.get_balance(address)
                    balance_eth = w3.from_wei(
                        balance_wei,
                        "ether",
                    )

                    st.metric(
                        "Saldo ETH",
                        f"{float(balance_eth):.6f} ETH",
                    )

                    st.caption(
                        "Saldo dibaca oleh Web3.py dari Hardhat RPC."
                    )

                except Exception as error:
                    st.error("Gagal membaca saldo wallet.")
                    st.caption(str(error))

    except (ValueError, TypeError) as error:
        st.error("Data Chain ID dari MetaMask tidak valid.")
        st.caption(str(error))

else:
    st.info(
        "Klik Connect Wallet, kemudian setujui akses akun di MetaMask."
    )

# =========================================================
# CATATAN
# =========================================================

st.divider()

st.caption(
    "Praktikum ini hanya membaca informasi blockchain dan saldo. "
    "Tidak ada transaksi transfer atau perubahan smart contract."
)