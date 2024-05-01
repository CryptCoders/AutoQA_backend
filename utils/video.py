import io

import whisper
import moviepy.editor as mp

def extract_from_video(file):
    file_obj = io.BytesIO(file.read())

    video_path = 'F:\\autoQA\\autoQA_backend\\video_mp4.mp4'
    with open(video_path, 'wb') as f:
        f.write(file_obj.getvalue())

    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile('F:\\autoQA\\autoQA_backend\\audio_mp3.wav')
    model = whisper.load_model('tiny')
    result = model.transcribe('../audio_mp3.wav')

    return result['text']