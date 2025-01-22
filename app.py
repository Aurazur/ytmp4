from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"

# Ensure the downloads folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        # Get the YouTube URL from the form
        video_url = request.form['url']

        # Set the output path for downloaded videos
        output_path = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')

        # Set download options for yt-dlp
        ydl_opts = {
            'outtmpl': output_path,  # Save to the downloads folder
            'format': 'best',  # Best quality video and audio
        }

        # Download the video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        # Schedule the file for deletion after sending it
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error removing file: {e}")
            return response

        # Send the file to the client for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
