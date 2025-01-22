from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def clear_download_folder():
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {file_path}, {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        video_url = request.form['url']

        clear_download_folder()

        output_path = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')

        ydl_opts = {
            'outtmpl': output_path,
            'format': 'best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error removing file: {e}")
            return response

        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
