from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx

app = Flask(__name__)

# Folder upload untuk menyimpan file yang diunggah
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Fungsi untuk mengizinkan ekstensi file yang di-upload


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk membaca file teks


def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Fungsi untuk membaca file PDF


def read_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ''  # Menangani halaman kosong
    return text

# Fungsi untuk membaca file DOCX


def read_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

# Fungsi untuk membaca file berdasarkan ekstensi


def read_file(file_path, extension):
    if extension == 'txt':
        return read_txt(file_path)
    elif extension == 'pdf':
        return read_pdf(file_path)
    elif extension == 'docx':
        return read_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

# Fungsi untuk mengekstrak kata majemuk dari teks


def extract_compound_words(text):
    words = text.split()
    compounds = [word for word in words if '-' in word]
    return compounds

# Route untuk halaman utama


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Pastikan file ada di dalam request
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded")

        file = request.files['file']
        # Cek jika tidak ada file yang dipilih
        if file.filename == '':
            return render_template('index.html', error="No file selected")

        # Cek apakah file yang diunggah memiliki ekstensi yang diperbolehkan
        if file and allowed_file(file.filename):
            # Simpan file di folder upload
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Menentukan ekstensi file untuk dibaca
            extension = filename.rsplit('.', 1)[1].lower()

            try:
                # Membaca file berdasarkan ekstensi
                text = read_file(file_path, extension)
                compound_words = extract_compound_words(text)

                # Menyiapkan hasil untuk dikembalikan
                details = [
                    {
                        "word": word,
                        "article": "die",  # Artikel bahasa Jerman, bisa disesuaikan
                        "class": "Substantiv",  # Kelas kata, sesuaikan jika perlu
                        "root": word.split('-'),  # Kata dasar
                        "formation": " + ".join(word.split('-')),
                        "example": f"Beispiel für {word}"  # Contoh kalimat
                    }
                    for word in compound_words
                ]
                return render_template('index.html', results=details)

            except Exception as e:
                # Menangani error dalam proses pembacaan atau ekstraksi
                return render_template('index.html', error=f"Error processing file: {str(e)}")

        else:
            # Menangani file yang tidak valid
            return render_template('index.html', error="Invalid file type")

    # Jika metode GET, tampilkan halaman upload
    return render_template('index.html')


if __name__ == '__main__':
    # Buat folder upload jika belum ada
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Jalankan aplikasi di port 5000
    app.run(debug=True, port=5000)
