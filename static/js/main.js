document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const qualitySlider = document.getElementById('quality');
    const qualityValue = document.getElementById('qualityValue');
    const previewContainer = document.querySelector('.preview-container');
    const originalPreview = document.getElementById('originalPreview');
    const compressedPreview = document.getElementById('compressedPreview');
    const originalSize = document.getElementById('originalSize');
    const compressedSize = document.getElementById('compressedSize');
    const downloadBtn = document.getElementById('downloadBtn');

    let currentCompressedFile = null;

    // 更新质量显示
    qualitySlider.addEventListener('input', function() {
        qualityValue.textContent = this.value;
    });

    // 点击上传区域触发文件选择
    dropZone.addEventListener('click', () => fileInput.click());

    // 处理拖放
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#007AFF';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#DEDEDE';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#DEDEDE';
        const files = e.dataTransfer.files;
        if (files.length) handleFile(files[0]);
    });

    // 处理文件选择
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    // 处理文件上传和压缩
    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('请上传图片文件');
            return;
        }

        // 显示原始图片预览
        const reader = new FileReader();
        reader.onload = (e) => {
            originalPreview.src = e.target.result;
            originalSize.textContent = formatFileSize(file.size);
            previewContainer.hidden = false;
        };
        reader.readAsDataURL(file);

        // 上传并压缩图片
        const formData = new FormData();
        formData.append('file', file);
        formData.append('quality', qualitySlider.value);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            // 显示压缩后的图片
            compressedPreview.src = `/compressed/${data.compressed.filename}`;
            compressedSize.textContent = formatFileSize(data.compressed.size);
            currentCompressedFile = data.compressed.filename;

            // 计算压缩率
            const compressionRate = ((1 - data.compressed.size / data.original.size) * 100).toFixed(1);
            compressedSize.textContent = `${formatFileSize(data.compressed.size)} (减小 ${compressionRate}%)`;
        })
        .catch(error => {
            alert('压缩失败: ' + error.message);
        });
    }

    // 下载压缩后的图片
    downloadBtn.addEventListener('click', () => {
        if (currentCompressedFile) {
            window.location.href = `/download/${currentCompressedFile}`;
        }
    });

    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}); 