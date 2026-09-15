from block import EVotingBlockchain


evoting = EVotingBlockchain(difficulty=4)


while True:

    print("\n" + "=" * 50)
    print("        SISTEM E-VOTING BLOCKCHAIN")
    print("=" * 50)
    print("1. Daftar Pemilih")
    print("2. Voting") 
    print("3. Lihat Hasil Voting")
    print("4. Lihat Blockchain")
    print("5. Cek Validitas Blockchain")
    print("0. Keluar")
    print("=" * 50)

    pilihan = input("Pilih menu: ")

    # =========================
    # 1. DAFTAR PEMILIH
    # =========================
    if pilihan == "1":

        print("\n--- DAFTAR PEMILIH ---")

        voter_id = input("Masukkan ID pemilih : ")
        nama = input("Masukkan nama        : ")

        berhasil, pesan = evoting.register_voter(
            voter_id,
            nama
        )

        print(pesan)

    # =========================
    # 2. VOTING
    # =========================
    elif pilihan == "2":

        print("\n--- PEMUNGUTAN SUARA ---")

        voter_id = input("Masukkan ID pemilih : ")

        # Cek apakah pemilih terdaftar
        if voter_id not in evoting.voters:
            print("Pemilih belum terdaftar!")
            continue

        # Cek apakah sudah memilih
        if evoting.voters[voter_id]["has_voted"]:
            print("Pemilih sudah pernah memilih!")
            continue

        print("\nDaftar Kandidat:")

        for i, kandidat in enumerate(evoting.candidates):
            print(f"{i + 1}. {kandidat}")

        try:
            pilihan_kandidat = int(
                input("Pilih kandidat (1-2): ")
            )

            candidate_index = pilihan_kandidat - 1

            if candidate_index < 0 or candidate_index >= len(
                evoting.candidates
            ):
                print("Pilihan kandidat tidak tersedia!")
                continue

            berhasil, hasil = evoting.cast_vote(
                voter_id,
                candidate_index
            )

            if berhasil:
                print("\nVoting berhasil!")
                print("Kandidat :", hasil["candidate"])
                print("Block    :", hasil["block_index"])
                print("Hash     :", hasil["block_hash"])
                print("Nonce    :", hasil["nonce"])

            else:
                print("Voting gagal:", hasil)

        except ValueError:
            print("Input harus berupa angka!")

    # =========================
    # 3. HASIL VOTING
    # =========================
    elif pilihan == "3":

        print("\n--- HASIL VOTING ---")

        hasil = evoting.tally_votes()

        for kandidat, jumlah in hasil["tally"].items():
            print(f"{kandidat}: {jumlah} suara")

        print("-" * 40)
        print("Total pemilih :", hasil["total_registered"])
        print("Total suara   :", hasil["total_votes"])
        print(
            "Partisipasi   :",
            f"{hasil['participation_rate']:.2f}%"
        )

    # =========================
    # 4. LIHAT BLOCKCHAIN
    # =========================
    elif pilihan == "4":

        print("\n--- BLOCKCHAIN ---")

        for block in evoting.chain:

            print("=" * 60)
            print("INDEX :", block.index)
            print("DATA  :", block.data)
            print("PREV  :", block.previous_hash)
            print("HASH  :", block.hash)
            print("NONCE :", block.nonce)

    # =========================
    # 5. VALIDASI BLOCKCHAIN
    # =========================
    elif pilihan == "5":

        valid, pesan = evoting.is_chain_valid()

        print("\nBlockchain valid:", valid)
        print("Status:", pesan)

    # =========================
    # 0. KELUAR
    # =========================
    elif pilihan == "0":

        print("\nProgram selesai.")
        break

    else:
        print("Menu tidak tersedia!")
