"""
Unit test dan verifikasi untuk Sistem E-Voting Berbasis Blockchain
"""

from block import EVotingBlockchain

def run_tests():
    print(">>> Memulai Pengujian Sistem E-Voting Blockchain...")
    evote = EVotingBlockchain(difficulty=2)

    # 1. Test Genesis Block
    assert len(evote.chain) == 1, "Genesis block harus terbentuk."
    assert evote.chain[0].index == 0, "Index genesis block harus 0."
    assert evote.chain[0].hash.startswith("00"), "Hash genesis block harus memenuhi PoW difficulty 2."
    print("[OK] Test 1: Genesis Block valid.")

    # 2. Test Registrasi Pemilih
    ok, msg = evote.register_voter("V001", "Budi Santoso")
    assert ok is True, f"Registrasi V001 gagal: {msg}"
    
    # Registrasi ganda ID yang sama harus ditolak
    ok_dup, _ = evote.register_voter("V001", "Budi Duplikat")
    assert ok_dup is False, "Registrasi ID duplikat harus ditolak."
    print("[OK] Test 2: Registrasi Pemilih & Pencegahan ID Duplikat valid.")

    # 3. Test Voting Pertama
    ok_vote, res = evote.cast_vote("V001", 0)
    assert ok_vote is True, f"Voting gagal: {res}"
    assert len(evote.chain) == 2, "Jumlah blok harus menjadi 2."
    assert evote.chain[1].hash.startswith("00"), "Hash blok voting harus memenuhi difficulty."
    assert evote.chain[1].previous_hash == evote.chain[0].hash, "Previous hash harus cocok dengan hash genesis."
    print("[OK] Test 3: Pencoblosan suara & Mining Proof-of-Work valid.")

    # 4. Test Pencegahan Double Voting
    ok_double, res_double = evote.cast_vote("V001", 1)
    assert ok_double is False, "Double voting harus ditolak sistem!"
    assert "Pencegahan Double-Voting" in res_double or "sudah" in res_double, "Pesan penolakan harus sesuai."
    print("[OK] Test 4: Pencegahan Double-Voting berhasil memblokir pemilih curang.")

    # 5. Test Integritas Rantai (Chain Validity)
    is_valid, val_msg = evote.is_chain_valid()
    assert is_valid is True, f"Rantai harus valid: {val_msg}"
    print("[OK] Test 5: Integritas Rantai Blockchain valid.")

    # 6. Test Rekapitulasi Suara
    stats = evote.tally_votes()
    assert stats["total_votes"] == 1, "Total suara harus 1."
    assert stats["tally"][evote.candidates[0]] == 1, "Kandidat 0 harus memiliki 1 suara."
    print("[OK] Test 6: Rekapitulasi Suara (Tallying) akurat.")

    # 7. Test Deteksi Peretasan / Tampering
    ok_tamper, tamper_msg = evote.tamper_block(1, "Kandidat 99 - Hacker")
    assert ok_tamper is True, "Fungsi tamper harus berhasil memanipulasi blok untuk simulasi."
    is_valid_after_tamper, msg_tamper = evote.is_chain_valid()
    assert is_valid_after_tamper is False, "Blockchain harus mendeteksi manipulasi data!"
    print(f"[OK] Test 7: Simulasi Deteksi Peretasan berhasil: {msg_tamper}")

    print("\n==========================================")
    print("SELURUH 7 PENGUJIAN OTOMATIS BERHASIL (PASSED)!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
