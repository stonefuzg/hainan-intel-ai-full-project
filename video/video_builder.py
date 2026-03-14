
from moviepy.editor import TextClip, CompositeVideoClip

def build_video(text, output="intel_video.mp4"):

    clip = TextClip(text, fontsize=50)
    video = CompositeVideoClip([clip.set_duration(5)])

    video.write_videofile(output, fps=24)
