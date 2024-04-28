import os
import random

SEED_GEN = random.randint(0, 2**32 - 1)  # Generate a random 32-bit seed

program_count = 0
new_program_path = "sample.c"
os.system(
    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=Flatten --Functions=?1 --FlattenDispatch=* --Transform=CleanUp  --out=dled_flat_{program_count}.c {new_program_path}",
)
os.system(
    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=InitOpaque --Functions=?1  --InitOpaqueCount=1 --InitOpaqueStructs=list,array,env,input,plugin --Transform=CleanUp  --out=dled_opqpred_{program_count}.c {new_program_path}",
)

os.system(
    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=Virtualize --Functions=?1 --VirtualizeDispatch=* --Transform=CleanUp   --out=dled_vir_{program_count}.c {new_program_path}",
)

os.system(
    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=EncodeArithmetic --Functions=?1 --Transform=CleanUp  --out=dled_encodea_{program_count}.c {new_program_path}",
)
