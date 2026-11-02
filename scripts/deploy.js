const hre = require("hardhat");

async function main() {
    const ContracFactory =
        await hre.ethers.getContractFactory("EVotingInventaris");

    const contract = await ContracFactory.deploy();

    await contract.waitForDeployment();

    console.log("Deployment Berhasil");
    console.log("Alamat kontrak:", await contract.getAddress());
}

    main().catch((error) => {
        console.error(error);
        process.exitCode = 1;
    });