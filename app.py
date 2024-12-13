from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import os
import io
import uuid

app = Flask(__name__)

# 配置文件夹
UPLOAD_FOLDER = '/tmp'
COMPRESSED_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        quality = int(request.form.get('quality', 85))
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 读取图片数据
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({'error': '无法读取图片文件'}), 400
            
            # 生成文件名
            compressed_filename = f'compressed_{str(uuid.uuid4())}.jpg'
            compressed_path = os.path.join(COMPRESSED_FOLDER, compressed_filename)
            
            # 压缩并保存
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, encoded_img = cv2.imencode('.jpg', img, encode_param)
            
            # 保存到临时文件
            with open(compressed_path, 'wb') as f:
                f.write(encoded_img.tobytes())
            
            # 获取文件大小
            compressed_size = os.path.getsize(compressed_path)
            
            return jsonify({
                'compressed': {
                    'filename': compressed_filename,
                    'size': compressed_size
                }
            })
            
        return jsonify({'error': '不支持的文件类型'}), 400
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(COMPRESSED_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel 需要的入口点
app.debug = False

if __name__ == '__main__':
    app.run() 