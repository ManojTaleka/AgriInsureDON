from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend 
import random
import time


num_clients = eval(input("Enter the no of clients for the test \n"))

mask_gen_timings = []
total_time = 0 

data = [num for num in range(1,num_clients+1)]

# Get the default backend
backend = default_backend()

for i in range(num_clients):
    start_time = time.perf_counter()
    parameters_client = dh.generate_parameters(generator=2, key_size=512,backend=backend)
    private_key_client = parameters_client.generate_private_key()
    peer_public_key_client = parameters_client.generate_private_key().public_key()
    shared_key_client = private_key_client.exchange(peer_public_key_client)
    # Perform key derivation for client 
    derived_key_client = HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=b'handshake data',backend=backend).derive(shared_key_client)
    
    rng_client = random.Random(derived_key_client)
  
    # Generate a random mask using the derived secret for client 1
    mask = rng_client.randint(0,100)
    # Mask the secret for client
    masked_secret = data[i] + mask

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    mask_gen_timings.append(elapsed_time)
    print("Time Duration for each mask generation",elapsed_time)
    total_time += elapsed_time

print(f"Total Time Taken for {num_clients} Mask Generation is {total_time}")
print(f"Minimum Time for Mask Generation is {min(mask_gen_timings)}")
print(f"Average Time taken for generating {num_clients} masks is {total_time/num_clients}")
print(f"Maximum Time for Mask Generation is {max(mask_gen_timings)}")




