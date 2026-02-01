import os
import glob
import subprocess
import imageio_ffmpeg
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

# Fetch directory paths from environment variables. 
# Fallback to default placeholders if variables are not set.
INPUT_DIR = os.getenv("INPUT_DIR", "your_input_path")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "your_output_path")

def get_ffmpeg_path():
    return imageio_ffmpeg.get_ffmpeg_exe()

def process_video(input_path, ffmpeg_path):
    print(f"Processing: {input_path}")
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    
    # Define output filenames
    global_output = os.path.join(OUTPUT_DIR, f"global_{filename}")
    stabilized_output = os.path.join(OUTPUT_DIR, f"stabilized_global_{filename}")
    
    # trf file (relative filename for use in cwd)
    trf_filename = f"{base_name}_transform.trf"
    trf_file_abs = os.path.join(OUTPUT_DIR, trf_filename)
    
    # --- Pass 1: Rolling Shutter Correction (using deshake) ---
    # Modified: edge=0 to zero-fill (black) instead of mirroring
    print(f"  [Pass 1] Correcting rolling shutter (Deshake) -> {global_output}")
    cmd_pass1 = [
        ffmpeg_path,
        "-y",
        "-i", input_path,
        "-vf", "deshake=edge=0", 
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "copy",
        global_output
    ]
    
    try:
        subprocess.run(cmd_pass1, check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [Error] Pass 1 failed for {filename}: {e}")
        return

    # --- Pass 2: Stabilization (using vidstab) ---
    print(f"  [Pass 2] Stabilizing (VidStab) -> {stabilized_output}")
    
    # Step 2a: Detection
    # Modified: Add padding to background (1.5x size) to include all movement
    pad_filter = "pad=w=iw*1.5:h=ih*1.5:x=(ow-iw)/2:y=(oh-ih)/2:color=black"
    
    # Run in OUTPUT_DIR to avoid path issues with trf_filename
    cmd_detect = [
        ffmpeg_path,
        "-y",
        "-i", global_output,
        "-vf", f"{pad_filter},vidstabdetect=stepsize=32:shakiness=10:accuracy=15:result={trf_filename}",
        "-f", "null", "-"
    ]
    
    try:
        subprocess.run(cmd_detect, check=True, cwd=OUTPUT_DIR)
    except subprocess.CalledProcessError as e:
        print(f"  [Error] Pass 2 (Detection) failed for {filename}: {e}")
        return

    # Step 2b: Transform
    # Modified: Apply same padding, then transform
    # optzoom=0: Do not zoom
    cmd_transform = [
        ffmpeg_path,
        "-y",
        "-i", global_output,
        # Note: input={trf_filename} works because we set cwd=OUTPUT_DIR
        "-vf", f"{pad_filter},vidstabtransform=input={trf_filename}:optzoom=0:smoothing=30",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "copy",
        stabilized_output
    ]
    
    try:
        subprocess.run(cmd_transform, check=True, cwd=OUTPUT_DIR)
    except subprocess.CalledProcessError as e:
        print(f"  [Error] Pass 2 (Transform) failed for {filename}: {e}")
        return
        
    # Cleanup trf file
    if os.path.exists(trf_file_abs):
        try:
            os.remove(trf_file_abs)
        except:
            pass
            
    print(f"  [Done] Finished {filename}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
        except OSError as e:
            print(f"Error creating output directory: {e}")
            return

    ffmpeg_path = get_ffmpeg_path()
    print(f"Using ffmpeg: {ffmpeg_path}")
    
    mp4_files = glob.glob(os.path.join(INPUT_DIR, "*.mp4"))
    
    if not mp4_files:
        print(f"No .mp4 files found in {INPUT_DIR}")
        return
        
    print(f"Found {len(mp4_files)} files.")
    
    for mp4 in mp4_files:
        process_video(mp4, ffmpeg_path)

if __name__ == "__main__":
    main()
