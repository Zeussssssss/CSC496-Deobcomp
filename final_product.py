import os
import cv2
import sys
import json
import argparse
import anthropic
import subprocess
import numpy as np
import tensorflow as tf


def get_args():
    parser = argparse.ArgumentParser(
        description="Deobfuscator and Decompiler (Supports Flattening, Virtualization, Encoded Arithmetic, Opaque Predicates)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input",
        help="Path of the obfuscated executable to be decompiled.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path of the decompiled C file. (default=code displayed on the screen)",
        const="stdout",
        nargs="?",
        type=str,
        required=False,
    )
    return parser.parse_args()


def generate_binary_image(program_path, image_path):
    try:
        with open(program_path, "rb") as f:
            binary_data = f.read()
        img_data = np.frombuffer(binary_data, dtype=np.uint8)
        width = 64
        height = len(img_data) // width
        extra_bytes = len(img_data) % width
        img_data = img_data[: (len(img_data) - extra_bytes)]
        img_data = img_data.reshape(height, width)
        img_data = img_data[~np.all(img_data == 0, axis=1)]
        img_data = cv2.resize(img_data, (64, 64))
        cv2.imwrite(image_path, img_data)
        print(f"==> Binary image saved to '{image_path}'")
    except FileNotFoundError:
        print(f"Error: File '{program_path}' not found.")
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(0)


def get_prediction(input_image):
    obfuscations = [
        "None",
        "Encoded Arithmetic",
        "Flattening",
        "Opaque Predicates",
        "Virtualization",
    ]
    model = tf.keras.models.load_model("models/obf_classifier.keras")
    img = cv2.imread(input_image, cv2.IMREAD_GRAYSCALE)
    prediction = model.predict(np.expand_dims(img / 255, 0), verbose=0)
    predicted_class = prediction.argmax(axis=-1)
    confidence = np.max(prediction, axis=-1)
    return (obfuscations[predicted_class[0]], confidence)


def attempt_decompilation(binary_loc, obfuscation, confidence):
    process = subprocess.run(
        ["objdump", "-D", binary_loc],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if process.returncode == 0:
        LLM_Translator = {
            "None": "nothing",
            "Encoded Arithmetic": "Encoded Arithmetics (Arithmetic Obfuscation)",
            "Flattening": "Code Flattening",
            "Opaque Predicates": "Opaque Predicates",
            "Virtualization": "Virtualization",
        }
        disassembled = process.stdout
        client = anthropic.Anthropic(
            api_key="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"
        )
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            temperature=0.6,
            system=f"""Your task is to do your best attempt at decompiling the provided assembly code of a C executable obfuscated using {LLM_Translator[obfuscation]} ({confidence}% confidence). The code should be correct and ready to compile. You will do this by performing the following actions: \n\n1 - Decompile the provided assembly code to C language.  \n2 - Optimize and simplify the code created in step 1 to the best of your ability. Use the provided obfuscation type as a hint. \n3 - Generating a few line summary of what you think the optimized code does. (Should NOT exceed 5 lines) \n4 - Output a JSON object that contains the following fields: \ntransl, optim, summ. JUST OUTPUT THIS JSON, NOTHING ELSE! DO NOT ADD EXTRA TEXT. \n\nUse the following format: \ntransl: <Decompiled C code generated in step 1>\noptim: <simpler version generated in step 2>\nsumm: <summary generated in step 3>""",
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": f"{disassembled}"}],
                }
            ],
        )
        response = message.content[0].text
        return parse_response(response)
    else:
        print("!! ERROR getting the disassembled code using UNIX's objdump !!")
        exit(0)


def parse_response(response):
    start_index = response.find("```json")
    end_index = response.find("```", start_index + 7)
    return json.loads(response[start_index:end_index])


def main():
    args = get_args()
    print("\n === STARTING ===\n")
    print(f"==> Creating binary image of {args.input.split('/')[-1]}")
    generate_binary_image(args.input, f"{args.input.split('/')[-1].split('.')[0]}.png")
    print(f"==> Predicting the obfuscation using CNN")
    pred_class, confidence = get_prediction(
        f"{args.input.split('/')[-1].split('.')[0]}.png"
    )
    print(
        f"==> Detected Obfuscation: {pred_class} ({round(confidence[0]*100, 2)}% confidence)"
    )
    print(f"==> Contacting ClaudeAI for a decompiled version")
    decoded_json = attempt_decompilation(
        args.input, pred_class, round(confidence[0] * 100, 2)
    )
    print("----------- DECOMPILATION OUTPUT -----------")
    print(" DIRECT DECOMPILATION ")
    print(decoded_json["transl"] + "\n")
    print(" OPTIMIZED DECOMPILATION ")
    print(decoded_json["optim"] + "\n")
    print(" SUMMARY ")
    print(decoded_json["summ"] + "\n")
    if args.output == "stdout":
        print(f"===> Saving the optimized version of the decompiled file ")
        with open(args.output, "w") as file:
            # Write the contents of the variable to the file
            file.write(decoded_json["optim"])


if __name__ == "__main__":
    main()
