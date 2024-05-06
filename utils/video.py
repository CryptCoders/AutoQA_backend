import io
import whisper
import moviepy.editor as mp

def extract_from_video(file):
    file_obj = io.BytesIO(file.read())
    video_path = r'./video_mp4.mp4'

    with open(video_path, 'wb') as f:
        f.write(file_obj.getvalue())

    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(r'.\audio_mp3.wav')

    model = whisper.load_model('tiny')
    result = model.transcribe(r'./audio_mp3.wav')
    return result['text']

if __name__ == "__main__":
    with open(r'F:\autoQA\video1.mp4', 'rb+') as f:
        print(extract_from_video(f))