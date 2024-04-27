from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import InputLayer
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import anthropic
import sys
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense

def create_model():
    model = Sequential()
    model.add(Conv2D(30, (3,3), 1, activation='relu', input_shape=(64,64,1)))
    model.add(MaxPooling2D())

    model.add(Conv2D(15, (3,3), 1, activation='relu'))
    model.add(MaxPooling2D())

    model.add(Dropout(0.3))
    model.add(Flatten())

    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.4))

    model.add(Dense(50, activation='relu'))
    model.add(Dense(5, activation='softmax'))
    return model


def process_user_inpt(model, executable, path):
    with open(executable, "rb") as f:
        binary_data = f.read()
    img_data = np.frombuffer(binary_data, dtype=np.uint8)
    width = 64
    height = len(img_data) // width
    extra_bytes = len(img_data) % width
    img_data = img_data[: (len(img_data) - extra_bytes)]
    img_data = img_data.reshape(height, width)
    img_data = img_data[~np.all(img_data == 0, axis=1)]
    img_data = cv2.resize(img_data, (64, 64))
    cv2.imwrite(path + "/user_inpt.png", img_data)

    img = cv2.imread(path + '/user_inpt.png', cv2.IMREAD_GRAYSCALE)
    plt.imshow(img)
    yhat = model.predict(np.expand_dims(img/255, 0))
    highest_index = yhat.argmax(axis=-1)
    obfus = ""
    if(highest_index == 0):
        obfus = "Clean"
    elif(highest_index == 1):
        obfus = "EncodeArithmetic"
    elif(highest_index == 2):
        obfus = "Flatten"
    elif(highest_index == 3):
        obfus = "InitOpaque"
    elif(highest_index == 4):
        obfus = "Virtualize"

    print(obfus)
    
    api_call(executable, obfus)

def api_call(executable, obfus):
    with open(executable, "rb") as f:
        binary_data = f.read()
    client = anthropic.Anthropic(api_key="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")
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        temperature=1,
        system= f"Your task is to take this executable that has been obfuscated using the tigress transform {obfus} and return its standard C source code",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{binary_data}"
                    }
                ]
            }
        ]
    )
    print(message.content.text)


if __name__ == "__main__":
    model = create_model()
    model.load_weights('/Users/prasiddhigyawali/CSC496-Deobcomp-main/models/obf_classifier.keras')
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['F1Score', 'accuracy'])
    print(sys.argv[0])
    process_user_inpt(model, sys.argv[1], sys.argv[2])
