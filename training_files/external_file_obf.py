import os
import shutil
import random


def process_and_obf(folder_path):
    program_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".c"):
                SEED_GEN = random.randint(0, 2**32 - 1)  # Generate a random 32-bit seed

                program_path = os.path.join(root, file)
                new_program_name = f"dled_clean_{program_count}.c"
                new_program_path = os.path.join("progs/clean_progs", new_program_name)
                shutil.copy2(program_path, new_program_path)

                os.system(
                    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=Flatten --Functions=?1 --FlattenDispatch=* --Transform=CleanUp  --out=progs/flat_progs/dled_flat_{program_count}.c {new_program_path}",
                )

                os.system(
                    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=InitOpaque --Functions=?1  --InitOpaqueCount=1 --InitOpaqueStructs=list,array,env,input,plugin --Transform=CleanUp  --out=progs/opqpred_progs/dled_opqpred_{program_count}.c {new_program_path}",
                )

                os.system(
                    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=Virtualize --Functions=?1 --VirtualizeDispatch=* --Transform=CleanUp   --out=progs/vir_progs/dled_vir_{program_count}.c {new_program_path}",
                )

                os.system(
                    f"tigress --Verbosity=1 --Seed={SEED_GEN} --Environment=x86_64:Darwin:Clang:5.1 --Transform=EncodeArithmetic --Functions=?1 --Transform=CleanUp  --out=progs/encodea_progs/dled_encodea_{program_count}.c {new_program_path}",
                )

                program_count += 1


def add_includes_and_main(folder_path, all_includes):
    main_function = "\nint main() {\n    return 0;\n}\n"

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".c"):
                program_path = os.path.join(root, file)
                with open(program_path, "r") as f:
                    lines = f.readlines()

                # Remove existing includes from the includes list
                existing_includes = [
                    line for line in lines if line.startswith("#include")
                ]
                includes = [
                    include
                    for include in all_includes
                    if include not in existing_includes
                ]
                print(existing_includes)
                print(includes)
                # Find the index of the first #include statement
                first_include_index = next(
                    (i for i, line in enumerate(lines) if line.startswith("#include")),
                    None,
                )

                if first_include_index is not None:
                    # Insert new includes before the first #include statement
                    lines = (
                        lines[:first_include_index]
                        + includes
                        + lines[first_include_index:]
                    )
                else:
                    # If no #include statement is found, add new includes at the beginning
                    lines = includes + lines

                # Check if main function already exists
                has_main_function = any(
                    line.strip().startswith("int main(") for line in lines
                )

                if not has_main_function:
                    # Find the index of the last include statement
                    last_include_index = max(
                        (
                            i
                            for i, line in enumerate(lines)
                            if line.startswith("#include")
                        ),
                        default=-1,
                    )

                    # Insert main function after the last include statement
                    lines.insert(last_include_index + 1, main_function)

                with open(program_path, "w") as f:
                    f.writelines(lines)
                print(f"{program_path} includes and main function added")


if __name__ == "__main__":
    input_files_loc = "../C-master"
    includes = [
        '#include "tigress.h"\n',
        "#include <stdlib.h>\n",
        "#include <stdio.h>\n",
        "#include <time.h>\n",
        "#include <pthread.h>\n",
        "#include <string.h>\n",
    ]
    add_includes_and_main(input_files_loc, includes)
    print("___TIGRESS ADDED___")
    process_and_obf(input_files_loc)
