# Image Resizer & Converter Web App

A simple web-based tool for resizing, cropping, and converting images (including AVIF) to JPG or PNG.
Built with Python, Flask, and Pillow — with AVIF support via CLI tools.

---

## 🧾 Features

- Upload multiple images (JPG, PNG, BMP, WEBP, GIF, TIFF, AVIF)
- Resize and center-crop to desired dimensions
- Convert all images to JPG or PNG
- Preview processed images in browser
- Download all as ZIP
- Supports AVIF files using `avifdec`

---

## 🧰 Requirements

Installation them using:
```
.venv\scripts\activate
pip install -r requirements.txt
```

### 🔧 System Tools

#### 1. `avifdec` (required for AVIF support)

Download from:  
👉 [https://github.com/AOMediaCodec/libavif/releases](https://github.com/AOMediaCodec/libavif/releases) 

Look for the latest release like:  
`libavif-vX.X.X-windows-x64.zip` (for Windows)

Extract to:
`C:\tools\avif`

Make sure \`avifdec.exe\` is inside that folder.

Update this line in app.py if needed:
`AVIFDEC_PATH = r'C:\tools\avif\avifdec.exe'`
> ❗ Do not skip this step if you want to process `.avif` files.

---

## 📁 Folder Structure

Your project should look like this:

```
image-resizer/
│
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── uploads/         # Uploaded original images
│   └── processed/       # Preview images shown on site
├── processed/           # Session folders with converted images
├── temp_zip/            # Downloadable zip if you don't want to download another zip after processed
└── start-h.bat
```

---

## ▶️ Launching the WebUI

Open `start-h.bat` inside the folder to run the WebUI.

---

## 💬 Having Trouble?

If you get errors processing AVIF files:
- Make sure `avifdec.exe` exists at the path specified in `app.py`
- Make sure it works in terminal:
```
avifdec --help
```

If you see:
`The term 'avifdec' is not recognized`
→ You need to add the AVIF tools folder to your system PATH or use full path in code.

---

## 🌸 Enjoy!
"@
