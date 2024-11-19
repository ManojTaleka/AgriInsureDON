// SPDX-License-Identifier:MIT

pragma solidity >=0.7.0 <0.9.0;


contract DecentralizedOracle{
    address admin;
    address [] oraclearr;
    int256 indexedRFVal;  // indexed Risk Factor Value
    string  flocation;
    string  indexedRF; // Requesting indexed Risk Factor
    string cropName;


  constructor() {
        admin = msg.sender;
    }

    modifier onlyAdmin{
        require(admin == msg.sender, "Admin can Add Oracles");
         _;
    }

     // function for adding new oracle contracts
    function createOracleContract(address _oracleAddr) public onlyAdmin{
        oraclearr.push(_oracleAddr);
        emit OracleCreated(_oracleAddr,msg.sender);
    }

  
    function initiateOracleContract(address _oracleAddr, string memory _flocation, string memory _indexedRF,string memory _cropName) external  {
        for(uint256 i=0; i<oraclearr.length;i++){
            if(_oracleAddr == oraclearr[i])
            {
                 flocation = _flocation;
                 indexedRF = _indexedRF;
                 cropName = _cropName;
            }
        }
    }

    function queryDONRFAttribs() public view returns(string memory , string memory,string memory){
        return(flocation,indexedRF,cropName);
    }

    function getAggRFData(int256 _indexedRFVal) public
    {
        indexedRFVal = _indexedRFVal;
    }

    function callbackFromOracleContract() external view returns(int256){
        return indexedRFVal;
    }


     
     
     
     
     
     
     /* *********Events ****** */
    event OracleCreated(address _oracleAddr, address _admin);


}