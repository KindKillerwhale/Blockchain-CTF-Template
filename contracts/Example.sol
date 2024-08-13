// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

contract Example {
    address YOUR_WALLET_ADDRESS;
    constructor(address _wallet) {
        YOUR_WALLET_ADDRESS = _wallet;
    }


    function isChallSolved() public view returns (bool solved) {
        require(msg.sender == YOUR_WALLET_ADDRESS, "Please use the wallet provided to you");
        if(SOME_CONDITION) return false;
        return true;
    }
}
