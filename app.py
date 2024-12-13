from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
import os
import io
import uuid

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 确保上传和压缩文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

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
            # 生成唯一文件名
            original_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            compressed_filename = 'compressed_' + original_filename
            
            # 保存原始文件
            original_path = os.path.join(UPLOAD_FOLDER, original_filename)
            file.save(original_path)
            
            # 压缩图片
            with Image.open(original_path) as img:
                # 保持EXIF信息
                if 'exif' in img.info:
                    exif = img.info['exif']
                else:
                    exif = None
                    
                # 转换为RGB模式（如果是RGBA）
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                # 压缩图片
                compressed_path = os.path.join(COMPRESSED_FOLDER, compressed_filename)
                img.save(compressed_path, 'JPEG', quality=quality, optimize=True)
            
            # 获取文件大小
            original_size = os.path.getsize(original_path)
            compressed_size = os.path.getsize(compressed_path)
            
            return jsonify({
                'original': {
                    'filename': original_filename,
                    'size': original_size
                },
                'compressed': {
                    'filename': compressed_filename,
                    'size': compressed_size
                }
            })
        
        return jsonify({'error': '不支持的文件类型'}), 400
    
    except Exception as e:
        print(f"上传处理时出错: {str(e)}")
        return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(COMPRESSED_FOLDER, filename),
        as_attachment=True
    )

if __name__ == '__main__':
    # 开发环境使用 Flask 开发服务器
    if app.debug:
        app.run(debug=True)
    # 生产环境使用 Gunicorn
    else:
        app.run(host='0.0.0.0', port=8000) 