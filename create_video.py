import os
from PIL import Image
from moviepy.editor import ImageSequenceClip, AudioFileClip

def create_video_from_images(image_folder, audio_file, output_file):
    # Get sorted list of image files
    images = sorted([img for img in os.listdir(image_folder) if img.lower().endswith(('.jpg', '.jpeg', '.png'))])
    if not images:
        raise ValueError("No images found in the folder.")

    # Load audio
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

    # Load and resize images
    image_paths = []
    resized_folder = os.path.join(image_folder, "resized_tmp")
    os.makedirs(resized_folder, exist_ok=True)

    # Get size of the first image
    first_image_path = os.path.join(image_folder, images[0])
    base_size = Image.open(first_image_path).size

    for i, img_name in enumerate(images):
        img_path = os.path.join(image_folder, img_name)
        with Image.open(img_path) as img:
            resized_img = img.resize(base_size)
            save_path = os.path.join(resized_folder, f"frame_{i:03d}.png")
            resized_img.save(save_path)
            image_paths.append(save_path)

    # Calculate duration per image
    duration_per_image = audio_duration / len(image_paths)

    # Create video
    clip = ImageSequenceClip(image_paths, durations=[duration_per_image] * len(image_paths))
    clip = clip.set_audio(audio)

    clip.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=24)

    print(f"✅ Video created successfully: {output_file}")

# Example usage:
create_video_from_images("/home/tst/comfy-ui/ComfyUI/output", "/home/tst/Downloads/my.mp3", "output_video.mp4")

