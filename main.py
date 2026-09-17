from block import EVotingBlockchain
import os

BOLD = "\033[1m"
RESET = "\033[0m"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def header():
    print(CYAN + BOLD)
    print("=" * 60)
    print("              E-VOTING PEMILIHAN KETUA HIMPUNAN")
    print("        Sistem Pemungutan Suara Digital")
    print("=" * 60)
    print(RESET)


def pause():
    input("\nTekan ENTER untuk melanjutkan...")


def show_menu():
    print(YELLOW + BOLD)
    print("MENU UTAMA")
    print(YELLOW + "-" * 60)
    print(RESET)

    print("1. Daftar Pemilih")
    print("2. Lihat Daftar Pemilih")
    print("3. Pilih Kandidat")
    print("4. Lihat Hasil Voting")
    print("5. Lihat Blockchain")
    print("6. Validasi Blockchain")
    print("7. Simulasi Manipulasi Block")
    print("0. Keluar")

    print()


#TAB 1  Daftar Pemilih
def register_voter(e_voting):
    clear_screen()
    header()

    print(BOLD + "DAFTAR PEMILIH" + RESET)
    print("-" * 60)

    voter_id = input("Masukkan ID Pemilih : ").strip()
    name = input("Masukkan Nama        : ").strip()

    if not voter_id or not name:
        print(RED + "\nID dan nama tidak boleh kosong!" + RESET)
        pause()
        return

    success, message = e_voting.register_voter(voter_id, name)

    if success:
        print(GREEN + "\n✓ " + message + RESET)
    else:
        print(RED + "\n✗ " + message + RESET)

    pause()


# =========================
# LIHAT PEMILIH
# =========================
def show_voters(e_voting):
    clear_screen()
    header()

    print(BOLD + "DAFTAR PEMILIH" + RESET)
    print("-" * 60)

    if not e_voting.voters:
        print(YELLOW + "Belum ada pemilih yang terdaftar." + RESET)
    else:
        for i, (voter_id, voter) in enumerate(
            e_voting.voters.items(), start=1
        ):
            status = (
                "Sudah memilih"
                if voter["has_voted"]
                else "Belum memilih"
            )

            print(f"{i}. ID     : {voter_id}")
            print(f"   Nama   : {voter['name']}")
            print(f"   Status : {status}")
            print()

    pause()


# =========================
# MEMILIH KANDIDAT
# =========================
def cast_vote(e_voting):
    clear_screen()
    header()

    print(BOLD + "PEMUNGUTAN SUARA" + RESET)
    print("-" * 60)

    voter_id = input("Masukkan ID Pemilih : ").strip()

    if voter_id not in e_voting.voters:
        print(RED + "\n✗ Pemilih belum terdaftar." + RESET)
        pause()
        return

    voter = e_voting.voters[voter_id]

    if voter["has_voted"]:
        print(RED + "\n✗ Pemilih sudah pernah memilih!" + RESET)
        pause()
        return

    print("\nPilihan Kandidat:")

    for i, candidate in enumerate(e_voting.candidates, start=1):
        print(f"{i}. {candidate}")

    try:
        choice = int(input("\nPilih kandidat (1-2): "))

        candidate_index = choice - 1

        if candidate_index < 0 or candidate_index >= len(e_voting.candidates):
            print(RED + "\n✗ Pilihan kandidat tidak valid." + RESET)
            pause()
            return

    except ValueError:
        print(RED + "\n✗ Masukkan angka." + RESET)
        pause()
        return

    success, result = e_voting.cast_vote(
        voter_id,
        candidate_index
    )

    if success:
        print(GREEN + "\n✓ Suara berhasil disimpan ke blockchain!" + RESET)

        print("\nInformasi Block:")
        print(f"Block Index : {result['block_index']}")
        print(f"Kandidat    : {result['candidate']}")
        print(f"Nonce       : {result['nonce']}")
        print(f"Voter Hash  : {result['voter_hash']}")
        print(f"Block Hash  : {result['block_hash']}")

    else:
        print(RED + "\n✗ " + result + RESET)

    pause()


# =========================
# HASIL VOTING
# =========================
def show_results(e_voting):
    clear_screen()
    header()

    print(BOLD + "HASIL PEMUNGUTAN SUARA" + RESET)
    print("-" * 60)

    result = e_voting.tally_votes()

    print(f"Total Pemilih Terdaftar : {result['total_registered']}")
    print(f"Total Suara             : {result['total_votes']}")
    print(
        f"Tingkat Partisipasi    : "
        f"{result['participation_rate']:.2f}%"
    )

    print("\nPerolehan Suara:")

    for candidate, votes in result["tally"].items():
        print(f"- {candidate}: {votes} suara")

    pause()


# =========================
# LIHAT BLOCKCHAIN
# =========================
def show_blockchain(e_voting):
    clear_screen()
    header()

    print(BOLD + "BLOCKCHAIN" + RESET)
    print("-" * 60)

    for block in e_voting.chain:
        print(f"\nBlock #{block.index}")
        print(f"Timestamp     : {block.timestamp}")
        print(f"Data          : {block.data}")
        print(f"Previous Hash : {block.previous_hash}")
        print(f"Nonce         : {block.nonce}")
        print(f"Hash          : {block.hash}")

    pause()


# =========================
# VALIDASI BLOCKCHAIN
# =========================
def validate_blockchain(e_voting):
    clear_screen()
    header()

    print(BOLD + "VALIDASI BLOCKCHAIN" + RESET)
    print("-" * 60)

    valid, message = e_voting.is_chain_valid()

    if valid:
        print(GREEN + "\n✓ " + message + RESET)
    else:
        print(RED + "\n✗ " + message + RESET)

    pause()


# =========================
# SIMULASI MANIPULASI
# =========================
def tamper_block(e_voting):
    clear_screen()
    header()

    print(BOLD + "SIMULASI MANIPULASI BLOCK" + RESET)
    print("-" * 60)

    if len(e_voting.chain) <= 1:
        print(YELLOW + "\nBelum ada block voting." + RESET)
        pause()
        return

    print("\nBlock yang tersedia:")

    for block in e_voting.chain:
        print(f"Block #{block.index}")

    try:
        block_index = int(
            input("\nMasukkan index block yang ingin dimanipulasi: ")
        )

    except ValueError:
        print(RED + "\n✗ Index harus berupa angka." + RESET)
        pause()
        return

    fake_candidate = input(
        "Masukkan kandidat palsu: "
    ).strip()

    success, message = e_voting.tamper_block(
        block_index,
        fake_candidate
    )

    if success:
        print(RED + "\n⚠ " + message + RESET)
        print(
            YELLOW +
            "Sekarang coba gunakan menu Validasi Blockchain."
            + RESET
        )
    else:
        print(RED + "\n✗ " + message + RESET)

    pause()


# =========================
# PROGRAM UTAMA
# =========================
def main():

    # difficulty = 3 berarti hash harus diawali 000
    e_voting = EVotingBlockchain(difficulty=3)

    while True:
        clear_screen()
        header()
        show_menu()

        choice = input("Pilih menu: ").strip()

        if choice == "1":
            register_voter(e_voting)

        elif choice == "2":
            show_voters(e_voting)

        elif choice == "3":
            cast_vote(e_voting)

        elif choice == "4":
            show_results(e_voting)

        elif choice == "5":
            show_blockchain(e_voting)

        elif choice == "6":
            validate_blockchain(e_voting)

        elif choice == "7":
            tamper_block(e_voting)

        elif choice == "0":
            clear_screen()
            print(GREEN + "\nTerima kasih telah menggunakan E-Voting Blockchain!" + RESET)
            break

        else:
            print(RED + "\n✗ Menu tidak tersedia." + RESET)
            pause()


if __name__ == "__main__":
    main()