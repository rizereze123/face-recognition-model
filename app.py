import base64
from io import BytesIO
from flask import Flask, request, jsonify
import face_recognition
from PIL import UnidentifiedImageError

app = Flask(__name__)

def compare_face(registered_image, attendance_image):
    # Membuat encoding wajah
    registered_encoding = face_recognition.face_encodings(registered_image)[0]
    attendance_encodings = face_recognition.face_encodings(attendance_image)

    # Membandingkan wajah di gambar absensi dengan referensi
    for attendance_encoding in attendance_encodings:
        match = face_recognition.compare_faces([registered_encoding], attendance_encoding)
        if match[0]:
            return jsonify({"status": "success", "message": "Match found", "is_match": True})

    return jsonify({"status": "failed", "message": "No match found", "is_match": False})

@app.route('/verify', methods=['POST'])
def verify_face():
    try:
        # Mendapatkan request body dan memuat data JSON
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

        # Attempt to retrieve the base64-encoded images from the JSON data
        if 'registered_image' not in data or 'attendance_image' not in data:
            return jsonify({"status": "error", "message": "Missing required image data"}), 400

        # Mendapatkan data gambar base64 dari request body
        registered_image_data = data['registered_image']
        attendance_image_data = data['attendance_image']

        # Hapus header base64 jika ada (misalnya 'data:image/jpeg;base64,')
        if ',' in registered_image_data:
            registered_image_data = registered_image_data.split(',')[1]
        if ',' in attendance_image_data:
            attendance_image_data = attendance_image_data.split(',')[1]

        # Mendekode data base64 menjadi bytes
        registered_image_bytes = base64.b64decode(registered_image_data)
        attendance_image_bytes = base64.b64decode(attendance_image_data)

        # Mengubah bytes menjadi file-like object agar dapat dibaca oleh face_recognition
        registered_image = face_recognition.load_image_file(BytesIO(registered_image_bytes))
        attendance_image = face_recognition.load_image_file(BytesIO(attendance_image_bytes))

        return compare_face(registered_image, attendance_image)

    except UnidentifiedImageError:
        return jsonify({"status": "error", "message": "Cannot identify image file"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
