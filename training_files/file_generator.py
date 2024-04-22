import os
import random

NUM = 1024
CLEAN_DIR = "./progs/clean_progs"
FLAT_DIR = "./progs/flat_progs"
OPQ_DIR = "./progs/opqpred_progs"
VIR_DIR = "./progs/vir_progs"
ENCODEA_DIR = "./progs/encodea_progs"
ENCODED_DIR = "./progs/encoded_progs"
# JIT_DIR = "./jit_progs"


# Create the directory if it doesn't exist
os.makedirs("./progs", exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(FLAT_DIR, exist_ok=True)
os.makedirs(OPQ_DIR, exist_ok=True)
os.makedirs(VIR_DIR, exist_ok=True)
os.makedirs(ENCODEA_DIR, exist_ok=True)
# os.makedirs(ENCODED_DIR, exist_ok=True)
# os.makedirs(JIT_DIR, exist_ok=True)

for i in range(200, NUM):
    SEED_GEN = random.randint(0, 2**32 - 1)  # Generate a random 32-bit seed

    # generate clean random files
    NEW_FILE = os.path.join(CLEAN_DIR, f"prog_clean_{i}.c")
    os.system(
        f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=RandomFuns --RandomFunsName=SECRET --RandomFunsFunctionCount=2 --Verbosity=5  --out={NEW_FILE} empty.c",
    )

    # generate flattened
    NEW_FLAT_FILE = os.path.join(FLAT_DIR, f"prog_flat_{i}.c")
    os.system(
        f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=Flatten --Functions=SECRET_1,SECRET_2 --FlattenDispatch=* --Transform=CleanUp  --out={NEW_FLAT_FILE} {NEW_FILE}",
    )

    # generate opaque predicates
    NEW_OPQ_FILE = os.path.join(OPQ_DIR, f"prog_opqpred_{i}.c")
    os.system(
        f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=InitOpaque --Functions=main  --InitOpaqueCount=1 --InitOpaqueStructs=list,array,env,input,plugin --Transform=CleanUp  --out={NEW_OPQ_FILE} {NEW_FILE}",
    )

    # generate virtualized code
    NEW_VIR_FILE = os.path.join(VIR_DIR, f"prog_vir_{i}.c")
    os.system(
        f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=Virtualize --Functions=SECRET_1,SECRET_2 --VirtualizeDispatch=* --Transform=CleanUp   --out={NEW_VIR_FILE} {NEW_FILE}",
    )

    # generate encode arithmetic code
    NEW_ENCODEA_FILE = os.path.join(ENCODEA_DIR, f"prog_encodea_{i}.c")
    os.system(
        f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=EncodeArithmetic --Functions=SECRET_1,SECRET_2 --Transform=CleanUp  --out={NEW_ENCODEA_FILE} {NEW_FILE}",
    )

    # # generate encode literal
    # NEW_ENCODED_FILE = os.path.join(ENCODED_DIR, f"prog_encoded_{i}.c")
    # os.system(
    #     f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=EncodeData --Functions=SECRET_1 --Transform=CleanUp  --out={NEW_ENCODED_FILE} {NEW_FILE}",
    # )
