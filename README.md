# stabilizing_drone_movies



## 1. Motivation

I realized that footage captured with toy drones or lightweight drones (under 100g) was often too shaky to enjoy or use effectively. While looking for a solution, I discovered the concept of "Video Stabilization" through the following resources:



* [vidstab Documentation](https://adamspannbauer.github.io/python_video_stab/html/index.html)

* [vidstab on GitHub](https://github.com/AdamSpannbauer/python_video_stab)



After building a prototype to verify the functionality, I was amazed by its effectiveness. It functions essentially as a **"software gimbal."**



I developed this code using an "Antigravity" agent to handle both camera stabilization and the rolling shutter distortion typical of inexpensive CMOS sensors. I am sharing it here for others to use.



---



# Video Stabilizer (Antigravity) Processing Flow



This script automates rolling shutter correction and image stabilization for drone footage using **FFmpeg** (specifically the `deshake` and `vidstab` filters).



## 0. Prerequisites

* **Environment Setup:** Create a `.env` file based on `.env.sample` (see Section 4 for details).

* **Install Dependencies:** Install the required libraries using the provided requirements file:

&nbsp; `pip install -r requirements.txt`



## 1. Process Overview

The program performs a 3-step process (2-pass processing) for each input file.



## 2. Step-by-Step Details



### Step 1: Rolling Shutter Correction (Pass 1)

Corrects the vertical distortion (jello effect) characteristic of CMOS sensors during high-speed movement.

* **Filter Used:** `deshake`

* **Key Setting:** `edge=0` (zero-fill)

&nbsp;   * Any empty space at the edges created by the correction is filled with **black** rather than mirroring surrounding pixels.

* **Output:** Generates an intermediate file: `global_*.mp4`.



### Step 2: Shake Analysis (Pass 2a - Detection)

Mathematically analyzes the video jitter and extracts motion data.

* **Filter Used:** `vidstabdetect`

* **Key Setting:** `pad_filter`

&nbsp;   * The canvas is **expanded to 1.5x** its original size during analysis. This allows the motion to be tracked even during severe shakes without losing the frame.

* **Output:** Generates a transform data file: `*_transform.trf`.



### Step 3: Apply Stabilization (Pass 2b - Transform)

Stabilizes the actual video frames based on the analysis data.

* **Filter Used:** `vidstabtransform`

* **Key Setting:** `optzoom=0` (Zoom disabled)

&nbsp;   * Standard stabilization often "zooms in" to hide black edges. This script intentionally **disables zooming to visualize exactly how the camera moved**, leaving the black borders visible in the output.



## 3. Tech Stack

* **Python 3.x**

* **FFmpeg** (via `imageio-ffmpeg`)

* **VidStab**: High-performance video stabilization library.



## 4. Configuration

Copy `.env.sample` to `.env` and update the following variables with your local paths:



* **INPUT_DIR**: Path to the folder containing your source videos.

* **OUTPUT_DIR**: Path where the processed videos will be saved.



## 5. Execution Samples

*Input (Original) on the left, Output (Processed & Stabilized) on the right.
https://github.com/user-attachments/assets/9735ee90-0748-4327-97fd-1367d398c19a

| :--- | :--- |

| <video src="original01.mp4" controls muted width="400"></video> | <video src="stabilized01.mp4" controls muted width="400"></video> |

