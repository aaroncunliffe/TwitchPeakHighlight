import math
import librosa
import librosa.display
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip, TextClip, concatenate_videoclips, CompositeVideoClip
import time

# Start variables
clip_offset = 0#12960.0 #12980.0
clip_offset_timestamp = time.strftime('%H:%M:%S', time.gmtime(clip_offset))
offset = clip_offset
video_file_path = "resources/hob1.mp4"

# Load audio data
audio_data, sr = librosa.load(video_file_path, sr=None, offset=offset, duration=120.0)

print(len(audio_data))
exit()
# Other variables
threshold = 0.70                    # Sound threshold
clip_bounds = 2.0                   # Time either side of the loud portion
min_frame_size = (1.0 / 60.0) * 0.5 # Half a second minimum size
frame_duration = 1.0 / 60.0         # Time of single frame
samples_in_frame = frame_duration * sr

# Draw base data
librosa.display.waveplot(audio_data, sr=sr)

# Calculate the number of frames in the audio file
num_of_frames = math.floor(len(audio_data) / samples_in_frame)
print('Number of frames: ', num_of_frames)

over_threshold_frames = []
for frame_num in range(int(num_of_frames)):
    # Get the start and end of the frame
    start = int(frame_num * samples_in_frame)
    stop = int((frame_num + 1) * samples_in_frame)

    # Get the absolute values in each frame
    abs_frame = map(abs, audio_data[start:stop])

    # Get the maximum value in the frame
    cur_max_val = max(abs_frame)

    # Frame is above the threshold
    if cur_max_val > threshold:
        over_threshold_frames.append(frame_num)


over_threshold_frame_times = [i * frame_duration for i in over_threshold_frames]

# Turn the over threshold indexes to a start and end frame value
# This will symbolise the blocks for the new clips
clip_starts_and_stop_times = []

start_time = 0.0
previous_time = 0.0
for index, time in enumerate(over_threshold_frame_times):
    if(start_time == 0.0): 
        start_time = time
        previous_time = time
    
    # Difference between current time and previous time is greater than the bounds
    # clip_bounds * 2 if clips are too close together?
    difference = time - (previous_time + clip_bounds)
    if(difference > clip_bounds or index == (len(over_threshold_frame_times) - 1)):
        start = clip_offset + (start_time - clip_bounds)
        end = clip_offset + (previous_time + clip_bounds)
        clip_starts_and_stop_times.append([start, end])
        start_time = time
        print(time)
        
    previous_time = time

print(clip_starts_and_stop_times)
# Plot the blocks that will become new clips
for start, stop in clip_starts_and_stop_times:
    plt.axvspan(start - clip_offset, stop - clip_offset, -1, 1, alpha=0.5, color='r')

# Mark thresholds horizontally
plt.plot([threshold] * len(audio_data), color='g')
plt.plot([threshold * -1] * len(audio_data), color='g')

# Uncomment to show or save graph
#plt.savefig('output/waveform.png')
#plt.show()


# Generate clips

# Load original Clip
video_clip = VideoFileClip(video_file_path)

sub_clips = []
# For each frame, convert the start and end indexes of the frame
# to the location in time in the clip and subclip it
for index, frame in enumerate(clip_starts_and_stop_times):
    start, end = frame

    # Convert start and end frame indexes to 
    sub_clip = video_clip.subclip(start, end)
    sub_clips.append(sub_clip)

# Save each video clip
if(len(sub_clips) != 0):
    all_clips = concatenate_videoclips(sub_clips)
    all_clips.write_videofile('output/output2.mp4', audio_codec='aac')

plt.show()
print('Done')
