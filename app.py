import os
import uuid
from datetime import datetime
import shutil
import subprocess
from flask import Flask, render_template, request, send_file, flash, get_flashed_messages
from PIL import Image
from zipfile import ZipFile

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Folder paths
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_PREVIEW_FOLDER = 'static/processed'
PROCESSED_FINAL_FOLDER = 'processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_PREVIEW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FINAL_FOLDER, exist_ok=True)

# Store latest session folder globally
LATEST_SESSION = {}

def get_latest_session_folder(create_new=False):
    if 'folder' not in LATEST_SESSION or create_new:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        session_dir = os.path.join(PROCESSED_FINAL_FOLDER, timestamp)
        os.makedirs(session_dir, exist_ok=True)
        LATEST_SESSION['folder'] = session_dir
    return LATEST_SESSION['folder']

@app.route('/', methods=['GET', 'POST'])
def index():
    processed_images = []
    current_year = datetime.now().year
    width, height = 300, 300
    selected_format = 'png'

    if request.method == 'POST':
        files = request.files.getlist('images')
        width = int(request.form.get('width', 300))
        height = int(request.form.get('height', 300))
        selected_format = request.form.get('format', 'png').lower()
        target_size = (width, height)

        session_dir = get_latest_session_folder(create_new=True)

        for file in files:
            if file.filename != '':
                unique_id = str(uuid.uuid4())
                ext = os.path.splitext(file.filename)[1].lower()
                input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_original{ext}")
                output_name = f"{unique_id}_converted.{selected_format}"
                output_path = os.path.join(session_dir, output_name)
                preview_path = os.path.join(PROCESSED_PREVIEW_FOLDER, output_name)

                file.save(input_path)

                try:
                    process_image(input_path, output_path, target_size, selected_format)
                    shutil.copy(output_path, preview_path)
                    processed_images.append(os.path.basename(preview_path))
                except Exception as e:
                    flash(f"⚠️ Could not process: {file.filename} ({str(e)})")

    return render_template('index.html',
                           images=processed_images,
                           current_year=current_year,
                           width=width,
                           height=height,
                           selected_format=selected_format,
                           messages=get_flashed_messages())

@app.route('/download_all')
def download_all():
    session_dir = get_latest_session_folder()
    files = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f))]

    if not files:
        return "No files found to download", 400

    zip_dir = 'temp_zip'
    if os.path.exists(zip_dir):
        shutil.rmtree(zip_dir)
    os.makedirs(zip_dir, exist_ok=True)

    zip_path = os.path.join(zip_dir, 'processed_images.zip')

    with ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(os.path.join(session_dir, file), file)

    return send_file(zip_path, download_name='processed_images.zip', as_attachment=True)

def convert_avif_to_png_with_cli(avif_path, png_path):
    """Convert AVIF to PNG using avifdec CLI"""
    AVIFDEC_PATH = r'C:\tools\avif\avifdec.exe'  # Change this to your actual path
    result = subprocess.run([
        AVIFDEC_PATH,
        avif_path,
        png_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(f"avifdec failed: {result.stderr.decode()}")

def process_image(input_path, output_path, target_size, output_format='png'):
    src_img = None
    temp_png_path = None

    # Try with Pillow first
    try:
        with Image.open(input_path) as img:
            src_img = img.convert('RGBA') if img.mode != 'RGBA' else img
    except Exception as e:
        print(f"[PIL] Failed to open {input_path}: {e}")

    if src_img is None:
        if input_path.lower().endswith('.avif'):
            # Fallback: Use avifdec
            temp_png_path = input_path + ".fallback.png"
            try:
                convert_avif_to_png_with_cli(input_path, temp_png_path)
                src_img = Image.open(temp_png_path).convert('RGBA')
            except Exception as e:
                raise RuntimeError(f"Could not decode AVIF file: {e}")
            finally:
                if temp_png_path and os.path.exists(temp_png_path):
                    os.remove(temp_png_path)
        else:
            # For other formats, try opening via PIL again without context manager
            try:
                src_img = Image.open(input_path).convert('RGBA')
            except Exception as e:
                raise RuntimeError(f"Could not open image: {e}")

    src_width, src_height = src_img.size
    target_width, target_height = target_size

    scale_w = target_width / src_width
    scale_h = target_height / src_height
    scale = max(scale_w, scale_h)

    new_size = (int(src_width * scale), int(src_height * scale))
    img = src_img.resize(new_size, Image.Resampling.LANCZOS)

    left = (img.width - target_width) // 2
    top = (img.height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    img = img.crop((left, top, right, bottom))

    # Format conversion
    if output_format.lower() == 'jpg':
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(output_path, format='JPEG', optimize=True, quality=95)
    elif output_format.lower() == 'png':
        img = img.convert('RGBA') if img.mode != 'RGBA' else img
        img.save(output_path, format='PNG')
    else:
        img.save(output_path, format=output_format or 'PNG')

if __name__ == '__main__':
    app.run(debug=True)