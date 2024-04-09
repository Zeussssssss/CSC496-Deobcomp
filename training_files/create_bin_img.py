import os
import cv2
import subprocess
import numpy as np


def compile_c_program(program_path, output_path):
    try:
        subprocess.run(["clang", "-w", program_path, "-o", output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed for '{program_path}': {e}")
        return False


def generate_binary_image(program_path, image_path):
    try:
        with open(program_path, "rb") as f:
            binary_data = f.read()

        img_data = np.frombuffer(binary_data, dtype=np.uint8)
        width = 128
        height = len(img_data) // width
        extra_bytes = len(img_data) % width
        img_data = img_data[: (len(img_data) - extra_bytes)]
        img_data = img_data.reshape(height, width)
        img_data = cv2.resize(img_data, (64, 64))
        cv2.imwrite(image_path, img_data)
        print(f"Binary image saved to '{image_path}'")
    except FileNotFoundError:
        print(f"Error: File '{program_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")


def process_programs_in_folder(folder_path):
    img_folder = os.path.join(folder_path, "img")
    os.makedirs(img_folder, exist_ok=True)
    programs = [f for f in os.listdir(folder_path) if f.endswith(".c")]
    for program in programs:
        program_path = os.path.join(folder_path, program)
        output_path = os.path.join(folder_path, "img", os.path.splitext(program)[0])
        if compile_c_program(program_path, output_path):
            image_path = os.path.join(
                folder_path, "img", f"{os.path.splitext(program)[0]}.png"
            )
            generate_binary_image(output_path, image_path)
            os.remove(output_path)


if __name__ == "__main__":
    folder_path = "progs"
    process_programs_in_folder(folder_path)
