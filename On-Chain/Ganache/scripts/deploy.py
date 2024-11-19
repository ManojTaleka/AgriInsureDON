from brownie import accounts,config, IndexedInsurance, DecentralizedOracle
import os
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
from .mss import generate_pairedmasks_clients,secure_aggegration_server

def get_account(key):
    account = accounts.add(config['wallets'][key])
    print(f"Account :{account}")
    return account

# account1 is used for Admin account2,account3 for farmers
def deploy_insurancetransactions(insurance_deploy,actualadmin_account):
    account1 = get_account('account1_key') # Get the address of the account from ganache-local 
    createAdmin_transaction = insurance_deploy.createAdmin(account1,{"from":actualadmin_account})
    createAdmin_transaction.wait(1)
    account2 = get_account('account2_key')
    print(f'Farmer1 account:{account2}')
    verifyAndRegisterFarmer_transaction1 = insurance_deploy.verifyAndRegisterFarmer(account2,{"from":account1})
    verifyAndRegisterFarmer_transaction1.wait(1)
    account3 = get_account('account3_key')
    print(f'Farmer2 account:{account3}')
    verifyAndRegisterFarmer_transaction2 = insurance_deploy.verifyAndRegisterFarmer(account3,{"from":account1})
    verifyAndRegisterFarmer_transaction2.wait(1)
    underwritePolicy_transaction = insurance_deploy.underwritePolicy("WeatherIndex",100,"Puttur","Paddy","Temperature",100000,True,{"from":account1})
    underwritePolicy_transaction.wait(1)
    registerToIndexedInsurance_transaction = insurance_deploy.registerToIndexedInsurance(account2,0,{"from":account1})
    registerToIndexedInsurance_transaction.wait(1)
    requestClaimSettlement_transaction = insurance_deploy.requestClaimSettlement(100,"Puttur","Temperature","Paddy",{"from":account2}) # transaction is deployed from farmer's account2
    requestClaimSettlement_transaction.wait(1)
    validCR = insurance_deploy.validClaimRequest(account2)
    print(f"The client claim request is valid:{validCR}")

def deploy_oracletransactions(insurance_deploy,oracle_deploy):
    account1 = get_account('account1_key') # Admin Account
    print(f'Admin account:{account1}')
    account2 = get_account('account2_key') # Farmer's account
    print(f'Farmer1 account:{account2}')
    account4 = get_account('account4_key')
    print(f'Decentralized Oracle Contract Deploying account:{account4}')
    createOracleContract_transaction = oracle_deploy.createOracleContract(account4)
    createOracleContract_transaction.wait(1)
    forwardRequestToOracleContract_transaction = insurance_deploy.forwardRequestToOracleContract(account4,account2)
    forwardRequestToOracleContract_transaction.wait(1)
    farmlocation,indexedRF,cropName = oracle_deploy.queryDONRFAttribs()
    print(f"Insured Farm location is {farmlocation}")
    print(f"Requested indexed Risk Factor is {indexedRF}")
    print(f"Insured Crop Name is {cropName}")
    # Retrieve masks and masked secrets for indexedRF
    masks,masked_secrets = generate_pairedmasks_clients()
    # Ask the server to aggregate the masked shares
    aggRFValue = secure_aggegration_server(masks,masked_secrets)
    
    getAggRFData_transaction = oracle_deploy.getAggRFData(aggRFValue,{"from":account4})
    getAggRFData_transaction.wait(1)
    receiveResponseFromOracleContract_transaction = insurance_deploy.receiveResponseFromOracleContract(account2,{"from":account1})    
    receiveResponseFromOracleContract_transaction.wait(1)
    tempval = insurance_deploy.cbval("Temperature")
    print("Temperature Value",tempval)
    payout_message = insurance_deploy.triggerPayout(account2,30)
    print(f"Payment Trigger Message is: {payout_message}")
    
def main():
    actualadmin_account = get_account('account_admin')
    print(f'Actual Admin Account is {actualadmin_account}')
    # Deploy the Oracle Contract
    oracle_deploy = DecentralizedOracle.deploy({"from":actualadmin_account})
    print(f"Oracle deploy address is {oracle_deploy}")
    insurance_deploy = IndexedInsurance.deploy(oracle_deploy,{"from":actualadmin_account})
    deploy_insurancetransactions(insurance_deploy,actualadmin_account)
    deploy_oracletransactions(insurance_deploy,oracle_deploy)
