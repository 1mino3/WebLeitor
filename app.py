import cv2
import mediapipe as mp
from flask import Flask, request, jsonify, send_from_directory
from keras.models import load_model
import numpy as np
import os

app = Flask(__name__)

# Configurações do modelo e Mediapipe
hands = mp.solutions.hands.Hands(max_num_hands=1)
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
classes = ['A', 'B', 'C', 'D', 'E']


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')


@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
    frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    hand_landmarks = results.multi_hand_landmarks
    h, w, _ = img.shape

    if hand_landmarks:
        for hand in hand_landmarks:
            x_max, y_max, x_min, y_min = 0, 0, w, h
            for lm in hand.landmark:
                x, y = int(lm.x * w), int(lm.y * h)
                x_max, x_min = max(x_max, x), min(x_min, x)
                y_max, y_min = max(y_max, y), min(y_min, y)

            try:
                img_crop = img[y_min - 50:y_max + 50, x_min - 50:x_max + 50]
                img_crop = cv2.resize(img_crop, (224, 224))
                img_array = np.asarray(img_crop)
                normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
                data[0] = normalized_image_array
                prediction = model.predict(data)
                index_val = np.argmax(prediction)
                return jsonify({'prediction': classes[index_val]})
            except Exception as e:
                print(f"Error in processing frame: {e}")
                return jsonify({'error': str(e)})

    return jsonify({'prediction': 'Nenhuma mão detectada'})


if __name__ == '__main__':
    app.run(debug=True)
