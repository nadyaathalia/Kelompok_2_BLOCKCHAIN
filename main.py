from blockchain import Blockchain

blockchain = Blockchain()

blockchain.add_block({
    "batch_id": "BATCH-001",
    "product": "Coffee Arabica",
    "actor": "Petani",
    "location": "Kuningan"
})

blockchain.add_block({
    "batch_id": "BATCH-001",
    "product": "Coffee Arabica",
    "actor": "Distributor",
    "location": "Cirebon"
})

for block in blockchain.chain:
    print("=" * 50)
    print("INDEX :", block.index)
    print("DATA  :", block.data)
    print("PREV  :", block.previous_hash)
    print("HASH  :", block.hash)

print("\nBlockchain valid:", blockchain.is_valid())