from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import random
import time

num_clients = eval(input("Enter the no of client shares for debugging \n"))

# Mask the secret for each participant
masked_secrets = []
masks = []  # Store masks for each participant

data = [num for num in range(1,num_clients+1)]

# Mask generation for num_clients
for i in range(num_clients):
    parameters_client = dh.generate_parameters(generator=2, key_size=512)
    private_key_client = parameters_client.generate_private_key()
    peer_public_key_client = parameters_client.generate_private_key().public_key()
    shared_key_client = private_key_client.exchange(peer_public_key_client)
    # Perform key derivation for client 
    derived_key_client = HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=b'handshake data').derive(shared_key_client)
    
    rng_client = random.Random(derived_key_client)
  
    # Generate a random mask using the derived secret for client 1
    mask = rng_client.randint(0,100)
    masks.append(mask)
    # Mask the secret for client
    masked_secret = data[i] + mask
    masked_secrets.append(masked_secret)

# Secure Aggregation
start_time = time.perf_counter()
aggregated_mask = sum(masks)  # Aggregate the masks
aggregated_secret = sum(masked_secrets)  # Aggregate the masked secrets
# Compute the average of the original secret values
original_secret_average = (aggregated_secret - aggregated_mask) / len(masked_secrets)

print("Average of original secret values:", original_secret_average)
end_time = time.perf_counter()
time_taken = end_time - start_time
print("Time Duration for secure aggregation",time_taken)