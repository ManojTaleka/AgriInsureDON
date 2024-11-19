// SPDX-License-Identifier:MIT

pragma solidity >=0.7.0 <0.9.0;
import "./DecentralizedOracle.sol";

contract IndexedInsurance{

   struct IndexedInsuranceProduct{
        string coverageType; // weather indexed or area-yield indexed
        uint256 farmID;
        string farmLocation;
        string cropName;
        string indexedRF;
        uint256 sumInsured;
        bool premiumPaid;
    }

    address [] admins ; // array to store the addresses of admins
    address []  public farmers ; // array to store the addresses of farmers
    address owner; // owner of the contract is the first admin
    IndexedInsuranceProduct [] public insuranceProducts;
    mapping (address => IndexedInsuranceProduct[]) farmerToInsuranceProduct;
    mapping (address => bool) public validClaimRequest;
    mapping (string => int256) public cbval; // mapping from indexParameter to value during callback
    address oracleDeployAddr; 

    constructor(address addr) {
        admins.push(msg.sender); // creator of the contract
        owner = msg.sender;
        oracleDeployAddr = addr;
    }


    modifier onlyAdmin{
        bool admin = false;
        for(uint256 i=0;i<admins.length;i++){
            if(admins[i] == msg.sender){
                admin = true;
                break;
            }
        }
        require(admin,"Only Admin can Modify/Change");
        _;
    }

    modifier onlyFarmer{
        bool customer = false;
        for(uint256 i=0;i<farmers.length;i++){
            if(farmers[i] == msg.sender){
                customer = true;
                break;
            }
        }
        require(customer,"Only Customer can Make Claim Request");
        _;
    }

    // function for adding new administrators
    function createAdmin(address _newAdmin) public onlyAdmin{
        admins.push(_newAdmin);
        emit AdminCreated(_newAdmin,msg.sender);
    }


    // function to and verify and register new farmers who satisfy KYC requirements
    function verifyAndRegisterFarmer(address _newFarmer) public onlyAdmin{
        farmers.push(_newFarmer);
        emit FarmerRegistered(_newFarmer,msg.sender);
    }


    function underwritePolicy(string memory _covType, uint256 _fid, string memory _flocation, string memory _cropName ,string memory _indexedRF, uint256 _sumInsured, bool _premiumPaid) public onlyAdmin{
        insuranceProducts.push(IndexedInsuranceProduct(_covType,_fid,_flocation,_cropName,_indexedRF,_sumInsured,_premiumPaid));
        emit IndexedInsuranceProductAdded(msg.sender);
    }

    function registerToIndexedInsurance(address _farmerAddr, uint256 _assignIndex) public onlyAdmin{ 
         // map the farmer address to specific index for underwritten insurance product
         for(uint256 i=0;i<farmers.length;i++){
           if(farmers[i] == _farmerAddr){
            farmerToInsuranceProduct[_farmerAddr].push(insuranceProducts[_assignIndex]);
            break;
           }  
        }
    }

    function requestClaimSettlement(uint256 _fid, string memory _flocation, string memory _indexedRF,string memory _cropName) public onlyFarmer {
        if(farmerToInsuranceProduct[msg.sender][0].premiumPaid == true)
        {
            if((_fid == farmerToInsuranceProduct[msg.sender][0].farmID) && (keccak256(abi.encodePacked(_flocation)) == keccak256(abi.encodePacked(farmerToInsuranceProduct[msg.sender][0].farmLocation)))
            && (keccak256(abi.encodePacked(_indexedRF)) == keccak256(abi.encodePacked(farmerToInsuranceProduct[msg.sender][0].indexedRF)))
            && (keccak256(abi.encodePacked(_cropName)) == keccak256(abi.encodePacked(farmerToInsuranceProduct[msg.sender][0].cropName)))){
                   validClaimRequest[msg.sender] = true;
            }
        }
    }

    function forwardRequestToOracleContract(address _oracleAddr, address _farmerAddr) public {
            if(validClaimRequest[_farmerAddr] == true){
            DecentralizedOracle DO = DecentralizedOracle(oracleDeployAddr);
            DO.initiateOracleContract(_oracleAddr,farmerToInsuranceProduct[_farmerAddr][0].farmLocation,farmerToInsuranceProduct[_farmerAddr][0].indexedRF,farmerToInsuranceProduct[_farmerAddr][0].cropName);
            }
    }

    function receiveResponseFromOracleContract(address _farmerAddr) public {
        if(validClaimRequest[_farmerAddr] == true){
            DecentralizedOracle DO = DecentralizedOracle(oracleDeployAddr);
            int256  indexedRFValue = DO.callbackFromOracleContract(); // Get the aggregated value for RF Data from Oracle contract
            cbval[farmerToInsuranceProduct[_farmerAddr][0].indexedRF] = indexedRFValue; // Assign the value to the mapping
        }
    }

    function triggerPayout(address _farmerAddr, int256 indexedRFThresholdVal) public view returns(string memory message){
        if(validClaimRequest[_farmerAddr] == true){
            if(cbval[farmerToInsuranceProduct[_farmerAddr][0].indexedRF] > indexedRFThresholdVal){
                message = "Payout is trigerred for a farmer";
                return message;
            }
            else{
                 message = "Payout is not trigerred as conditions are not met";
                 return message;
            }
        }
    }



    /*--------------Events------------*/
    event AdminCreated(address _newAdmin, address _actualAdmin);
    event FarmerRegistered(address _newFarmer, address _admin);
    event IndexedInsuranceProductAdded(address _admin);
}    