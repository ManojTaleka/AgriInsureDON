from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import random

masked_secrets = [] # store masked secrets of each participant
masks = []  # Store masks for each participant

def generate_pairedmasks_clients():
    parameters_client1 = dh.generate_parameters(generator=2, key_size=512)
    # Generate a private key for use in the exchange.
    private_key_client1 = parameters_client1.generate_private_key()
    peer_public_key_client1 = parameters_client1.generate_private_key().public_key()
    shared_key_client1 = private_key_client1.exchange(peer_public_key_client1)
    # Perform key derivation.
    derived_key_client1 = HKDF(algorithm=hashes.SHA256(),length=32,
    salt=None,
    info=b'handshake data').derive(shared_key_client1)
    rng_client1 = random.Random(derived_key_client1)
    # Risk Factor Data Temperature value
    temp1 = 36
    # Generate random masks using the derived secret
    mask1 = rng_client1.randint(0, 100)
    masks.append(mask1)
    # Mask the secret for client 1
    masked_secret_1 = temp1 + mask1
    masked_secrets.append(masked_secret_1)
    
    # Client2
    parameters_client2 = dh.generate_parameters(generator=2, key_size=512)
    private_key_client2 = parameters_client2.generate_private_key()
    peer_public_key_client2 = parameters_client2.generate_private_key().public_key()
    shared_key_client2 = private_key_client2.exchange(peer_public_key_client2)
    # Perform key derivation.
    derived_key_client2 = HKDF(algorithm=hashes.SHA256(),
    length=32,salt=None,info=b'handshake data').derive(shared_key_client2)

    rng_client2 = random.Random(derived_key_client2)
    # Risk Factor Data Temperature value
    temp2 = 37
    # Generate random masks using the derived secret
    mask2 = rng_client2.randint(0, 100)
    masks.append(mask2)
    # Mask the secret for client 2
    masked_secret_2 = temp2 + mask2
    masked_secrets.append(masked_secret_2)

    # client3
    parameters_client3 = dh.generate_parameters(generator=2, key_size=512)
    private_key_client3 = parameters_client3.generate_private_key()
    peer_public_key_client3 = parameters_client3.generate_private_key().public_key()
    shared_key_client3 = private_key_client3.exchange(peer_public_key_client3)
    # Perform key derivation.
    derived_key_client3 = HKDF(algorithm=hashes.SHA256(),
    length=32,salt=None,info=b'handshake data').derive(shared_key_client3)

    rng_client3 = random.Random(derived_key_client3)
    # Risk Factor Data Temperature value
    temp3 = 38
    # Generate random masks using the derived secret
    mask3 = rng_client3.randint(0, 100)
    masks.append(mask3)
    # Mask the secret for client 2
    masked_secret_3 = temp3 + mask3
    masked_secrets.append(masked_secret_3)
    return (masks,masked_secrets)

def secure_aggegration_server(masks,masked_secrets):
    t = 2  # Specify the number of participants required for secure aggregation
    if len(masked_secrets) >= t:  # 't' out of 'n' participants
        # Server aggregation
        aggregated_mask = sum(masks)  # Aggregate the masks
        aggregated_secret = sum(masked_secrets)  # Aggregate the masked secrets
        # Compute the average of the original secret values
        original_secret_average = (aggregated_secret - aggregated_mask) / len(masked_secrets)
        print("Average of original secret values:", original_secret_average)
    return original_secret_average

