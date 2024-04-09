import os
import random

NUM = 10
DIR = "./progs"

# Create the directory if it doesn't exist
os.makedirs(DIR, exist_ok=True)

for i in range(NUM):
    SEED_GEN = random.randint(0, 2**32 - 1)  # Generate a random 32-bit seed
    NEW_FILE = os.path.join(DIR, f"prog_{i}.c")

    # Call the tigress command
    os.system(
        f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=RandomFuns --out={NEW_FILE} empty.c",
    )
