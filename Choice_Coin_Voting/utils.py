from typing import List
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    phrase = mnemonic.from_private_key(private_key)
    print("Generated address: {}".format(address))
    print("Generated private key: {}".format(private_key))
    print("Generated mnemonic: {}".format(phrase))
    return address, phrase


def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo


#   Utility function used to print asset holding for account and assetid
def print_asset_holding(algodclient, account, assetid):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1        
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            break

def asset_optin(client, accounts: List, asset_id: str):
    params = client.suggested_params()
    for account in accounts:
        account_info = client.account_info(account['addr'])
        holding = None
        idx = 0
        for my_account_info in account_info['assets']:
            scrutinized_asset = account_info['assets'][idx]
            idx = idx + 1    
            if (scrutinized_asset['asset-id'] == asset_id):
                holding = True
                break

        if not holding:
            # Use the AssetTransferTxn class to transfer assets and opt-in
            txn = AssetTransferTxn(
                sender=account['addr'],
                sp=params,
                receiver=account['addr'],
                amt=0,
                index=asset_id)
            stxn = txn.sign(account['key'])
            txid = client.send_transaction(stxn)
            print(txid)
            # Wait for the transaction to be confirmed
            wait_for_confirmation(client, txid)
    # Now check the asset holding for that account.
    # This should now show a holding with a balance of 0.
        print_asset_holding(client, account['addr'], asset_id)