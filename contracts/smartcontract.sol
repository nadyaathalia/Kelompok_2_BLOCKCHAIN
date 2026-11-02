// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract EVotingInventaris is ERC721URIStorage {

    address public admin;

    uint256 private nextTokenId = 1;

    // ==============================
    // STRUCT PEMILIH
    // ==============================
    struct Pemilih {
        string idPemilih;
        string kandidat;
        string pemilihan;
        string location;
        bool sudahVoting;
        uint256 tokenId;
    }

    // ==============================
    // ERROR
    // ==============================
    error HanyaAdmin();
    error PemilihSudahVoting(string idPemilih);
    error PemilihTidakTerdaftar(string idPemilih);
    error AlamatTidakValid();

    // ==============================
    // MAPPING & ARRAY
    // ==============================
    mapping(string => Pemilih) public daftarPemilih;
    string[] public listIdPemilih;

    // ==============================
    // EVENT
    // ==============================
    event PemilihDitambahkan(
        string indexed idPemilih
    );

    event VotingBerhasil(
        string indexed idPemilih,
        string kandidat,
        string pemilihan,
        string location,
        uint256 tokenId
    );

    // ==============================
    // CONSTRUCTOR
    // ==============================
    constructor()
        ERC721("Voter Traceability", "VOTER")
    {
        admin = msg.sender;
    }

    // ==============================
    // MODIFIER
    // ==============================
    modifier onlyAdmin() {
        if (msg.sender != admin) {
            revert HanyaAdmin();
        }
        _;
    }

    // ==============================
    // TAMBAH PEMILIH
    // ==============================
    function tambahPemilih(
        string memory _idPemilih
    )
        external
        onlyAdmin
    {
        require(
            bytes(_idPemilih).length > 0,
            "ID pemilih kosong"
        );

        require(
            bytes(daftarPemilih[_idPemilih].idPemilih).length == 0,
            "Pemilih sudah terdaftar"
        );

        daftarPemilih[_idPemilih] = Pemilih({
            idPemilih: _idPemilih,
            kandidat: "",
            pemilihan: "",
            location: "",
            sudahVoting: false,
            tokenId: 0
        });

        listIdPemilih.push(_idPemilih);

        emit PemilihDitambahkan(_idPemilih);
    }

    // ==============================
    // CAST VOTE + MINT NFT
    // ==============================
    function castVote(
        string memory _idPemilih,
        string memory _kandidat,
        string memory _pemilihan,
        string memory _location
    )
        external
        returns (uint256)
    {
        Pemilih storage p = daftarPemilih[_idPemilih];

        if (bytes(p.idPemilih).length == 0) {
            revert PemilihTidakTerdaftar(_idPemilih);
        }

        if (p.sudahVoting) {
            revert PemilihSudahVoting(_idPemilih);
        }

        require(
            bytes(_kandidat).length > 0,
            "Kandidat kosong"
        );

        require(
            bytes(_pemilihan).length > 0,
            "Pemilihan kosong"
        );

        // ==============================
        // MINT NFT SATU KALI
        // ==============================
        uint256 tokenId = nextTokenId;
        nextTokenId++;

        _safeMint(msg.sender, tokenId);

        // ==============================
        // SET METADATA URI
        // ==============================
        string memory metadata = string(
            abi.encodePacked(
                "https://example.com/voter/",
                _idPemilih
            )
        );

        _setTokenURI(tokenId, metadata);

        // ==============================
        // UPDATE DATA VOTING
        // ==============================
        p.kandidat = _kandidat;
        p.pemilihan = _pemilihan;
        p.location = _location;
        p.sudahVoting = true;
        p.tokenId = tokenId;

        emit VotingBerhasil(
            _idPemilih,
            _kandidat,
            _pemilihan,
            _location,
            tokenId
        );

        return tokenId;
    }

    // ==============================
    // CEK PEMILIK NFT
    // ==============================
    function getOwner(
        uint256 tokenId
    )
        public
        view
        returns (address)
    {
        return ownerOf(tokenId);
    }

    // ==============================
    // CEK URI METADATA
    // ==============================
    function getMetadataURI(
        uint256 tokenId
    )
        public
        view
        returns (string memory)
    {
        return tokenURI(tokenId);
    }

    // ==============================
    // JUMLAH PEMILIH TERDAFTAR
    // ==============================
    function jumlahPemilih()
        external
        view
        returns (uint256)
    {
        return listIdPemilih.length;
    }

    // ==============================
    // CEK JUMLAH NFT
    // ==============================
    function jumlahNFT()
        external
        view
        returns (uint256)
    {
        return nextTokenId - 1;
    }

    // ==============================
    // REQUIRED OVERRIDE
    // ==============================
    function supportsInterface(
        bytes4 interfaceId
    )
        public
        view
        override(ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}