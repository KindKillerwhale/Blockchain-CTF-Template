# Blockchain CTF Template

This repository provides a template for building Capture The Flag (CTF) challenges focused on blockchain technology. It leverages Flask for the backend and Web3.py to interact with Ethereum-based smart contracts.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/KindKillerwhale/Blockchain-CTF-Template.git
   ```

2. Set the ```Example.sol``` in the ```contacts``` folder.

3. Set the ```docker-compose.yml``` and ```Dockerfile```.

4. Set the ex.py.

5. Docker RUN and TEST~!

※ Transaction must conform to the legacy format (including ```gasPrice``` option)

## Things that need to be fixed

- Currently, an account is created through ganache in ```docker-compose.yml``` and files containing account information are shared in docker volume, but there is a limitation in that the number of accounts is finite. This is inefficient both in terms of performance and capacity. Therefore, when you are asked for the ```/info``` method at ```app.py``` , you should change it to create an account immediately.
- The code of ```app.py``` needs to be neatly overhauled.
- When requested, it is necessary to adopt a method of setting a time limit so that the request cannot be made indefinitely. It is necessary to implement a PoW or a method of hanging timeout.
