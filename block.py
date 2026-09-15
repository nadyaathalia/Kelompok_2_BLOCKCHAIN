import hashlib
import json
from datetime import datetime
class Block:

    def __init__(
        self,
        index: int,
        data: dict,
        previous_hash: str,
        timestamp: str = None,
        nonce: int = 0
    ):
        self.index = index
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    @property
    def vote_data(self):
        return self.data

    def calculate_hash(self) -> str:

        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }

        encoded = json.dumps(
            block_data,
            sort_keys=True
        ).encode()

        return hashlib.sha256(encoded).hexdigest()


class EVotingBlockchain:
    def __init__(self, difficulty=3):

        self.difficulty = difficulty

        self.chain = [
            self.create_genesis_block()
        ]

        self.voters = {}

        self.candidates = [
            "Kandidat 1",
            "Kandidat 2"
        ]

    def create_genesis_block(self):

        return Block(
            index=0,
            data={
                "message": "Genesis Block"
            },
            previous_hash="0"
        )

    def register_voter(self, voter_id, name):

        if voter_id in self.voters:
            return False, "Pemilih sudah terdaftar."

        self.voters[voter_id] = {
            "name": name,
            "has_voted": False
        }

        return True, "Pemilih berhasil didaftarkan."

    def cast_vote(self, voter_id, candidate_index):

        if voter_id not in self.voters:
            return False, "Pemilih belum terdaftar."

        if self.voters[voter_id]["has_voted"]:
            return False, "Pemilih sudah pernah memilih!"

        candidate = self.candidates[candidate_index]

        voter_hash = hashlib.sha256(
            voter_id.encode()
        ).hexdigest()

        vote_data = {
            "type": "VOTE",
            "voter_hash": voter_hash,
            "candidate": candidate
        }

        block = Block(
            index=len(self.chain),
            data=vote_data,
            previous_hash=self.chain[-1].hash
        )

        # Mining / Proof of Work
        target = "0" * self.difficulty

        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()

        self.chain.append(block)

        self.voters[voter_id]["has_voted"] = True

        return True, {
            "block_index": block.index,
            "candidate": candidate,
            "block_hash": block.hash,
            "nonce": block.nonce,
            "voter_hash": voter_hash
        }

    def tally_votes(self):

        tally = {
            candidate: 0
            for candidate in self.candidates
        }

        for block in self.chain:

            if block.data.get("type") == "VOTE":

                candidate = block.data["candidate"]

                tally[candidate] += 1

        total_votes = sum(tally.values())
        total_registered = len(self.voters)

        participation_rate = (
            total_votes / total_registered * 100
            if total_registered > 0
            else 0
        )

        return {
            "tally": tally,
            "total_votes": total_votes,
            "total_registered": total_registered,
            "participation_rate": participation_rate
        }

    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False, (
                    f"Block #{current.index} "
                    "telah dimanipulasi."
                )

            if current.previous_hash != previous.hash:
                return False, (
                    f"Block #{current.index} "
                    "tidak terhubung dengan block sebelumnya."
                )

        return True, "Blockchain valid dan aman."

    def tamper_block(self, block_index, fake_candidate):

        if block_index <= 0:
            return False, "Genesis Block tidak dapat diubah."

        if block_index >= len(self.chain):
            return False, "Block tidak ditemukan."

        self.chain[block_index].data["candidate"] = fake_candidate

        return True, (
            f"Block #{block_index} berhasil dimanipulasi."
        )