from blockchain import Blockchain
from block import Block
from pos import proof_of_stake
from pow import proof_of_work

blockchain = Blockchain()

blockchain.add_block({
    "id_pemilih": "Irwansyah-001",
    "kandidat": "Paslon-02",
    "pemilihan": "Pemilihan Ketua",
    "location": "Informatika-A"
})

blockchain.add_block({
    "id_pemilih": "Akbar-002",
    "kandidat": "Paslon-01",
    "pemilihan": "Pemilihan Ketua",
    "location": "Informatika-B"
})

blockchain.add_block({
    "id_pemilih": "Akbar-003",
    "kandidat": "Paslon-02",
    "pemilihan": "Pemilihan Ketua",
    "location": "Informatika-A"
})


blockchain.add_block({
    "id_pemilih": "Nazwa-004",
    "kandidat": "Paslon-01",
    "pemilihan": "Pemilihan Ketua",
    "location": "Informatika-B"
})

for block in blockchain.chain:

    print("=" * 50)
    print("INDEX :", block.index)
    print("DATA  :", block.data)
    print("PREV  :", block.previous_hash)
    print("HASH  :", block.hash)

print("\nBlockchain valid:", blockchain.is_valid())

print("\n====== proof of work ======")
block = Block(
    index=1, 
    data="Evoting Pemilihan Ketua", 
    previous_hash="0")

difficulty = 5

print("Data Block       :", block.data)
print("Difficulty       :", difficulty)

proof_of_work(block, difficulty)

print("Nonce        :", block.nonce)
print("Hash         :", block.hash)

print("\n====== proof of stake ======")
validators = {
    "Validator_1": 100,
    "Validator_2": 50,
    "Validator_3": 500,
    "Validator_4": 75
}
print("\nValidators:")
for v, stake in validators.items():
    print(f"- {v}: {stake} stake")

selected = proof_of_stake(validators)
print("\nValidator Terpilih:", selected)
