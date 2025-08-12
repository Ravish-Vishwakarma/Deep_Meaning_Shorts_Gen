import os
import ffmpeg

# Folders
source_folder = 'input'
processed_folder = 'images'
audio_path = 'music.mp3'
output_folder = 'output'

# Create necessary folders
os.makedirs(processed_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Step 1: Resize images to fit width 1080px while maintaining aspect ratio
source_images = [f for f in os.listdir(source_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
source_images.sort()

for i, filename in enumerate(source_images, start=1):
    input_path = os.path.join(source_folder, filename)
    output_path = os.path.join(processed_folder, f'image{i}.jpg')

    (
        ffmpeg
        .input(input_path)
        .filter('scale', 'if(gt(a,9/16),1080,-1)', 'if(gt(a,9/16),-1,1920)')  # Fit within 1080x1920 based on aspect
        .filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2', color='black')  # Center the image
        .output(output_path, vframes=1)
        .run()
    )

    print(f'📐 Resized: {output_path}')

# Step 2: Create individual videos for each image
# Get music duration
audio_info = ffmpeg.probe(audio_path)
duration = float(audio_info['format']['duration'])

# Process each image individually and create a video
processed_images = sorted(os.listdir(processed_folder))

for idx, image_file in enumerate(processed_images, start=1):
    image_path = os.path.join(processed_folder, image_file)
    output_video_path = os.path.join(output_folder, f'video{idx}.mp4')

    # Create the video with the current image and add the audio
    video_input = ffmpeg.input(image_path, loop=1, t=duration)  # Loop the image for the duration of the audio
    audio_input = ffmpeg.input(audio_path)

    # Create the final video for each image
    (
        ffmpeg
        .output(video_input, audio_input, output_video_path, vcodec='h264_nvenc', acodec='aac', shortest=None)
        .run()
    )
    print(f'🎬 Created: {output_video_path}')

# Step 3: Clean up resized images
for file in os.listdir(processed_folder):
    file_path = os.path.join(processed_folder, file)
    try:
        os.remove(file_path)
        print(f'🧹 Deleted: {file_path}')
    except Exception as e:
        print(f'⚠️ Failed to delete {file_path}: {e}')
