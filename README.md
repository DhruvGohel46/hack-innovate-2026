![WhatsApp Image 2026-01-09 at 7 48 40 AM](https://github.com/user-attachments/assets/11054792-f77f-4b24-9935-a04602b62a3d)# RailVision AI - Advanced Wagon Monitoring System

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/backend-Python%203.9+-yellow.svg) ![React](https://img.shields.io/badge/frontend-React%2018-blue.svg) ![Pytorch](https://img.shields.io/badge/AI-Pytorch%20%7C%20OpenCV-orange.svg)


![WhatsApp Image 2026-01-09 at 7 48 40 AM](https://github.com/user-attachments/assets/dc7be402-22c1-45fd-b4c4-3407b7350aad)

![WhatsApp Image 2026-01-09 at 7 50 15 AM](https://github.com/user-attachments/assets/c60e5145-ea9d-4ddd-80ec-e641ae0b7e10)

![WhatsApp Image 2026-01-09 at 7 50 15 AM](https://github.com/user-attachments/assets/f9a535dd-8993-48db-ae76-c9e5f315e94f)

![WhatsApp Image 2026-01-09 at 7 53 16 AM](https://github.com/user-attachments/assets/43db052f-b7ef-4649-bdd9-ac9c144220ec)

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/24dbd811-301f-4fbb-81a7-6e2f6f7fd70c" />




**RailVision AI** is a state-of-the-art automated video restoration and Optical Character Recognition (OCR) pipeline designed for high-speed railway logistics. It specializes in extracting wagon identifiers from noisy, blurry, and low-light footage captured by trackside cameras.

---



🎯 Problem Statement

Modern railway logistics depend on accurate wagon number detection in real time.
However, trackside surveillance cameras face major challenges:

Motion Blur – fast-moving trains

Low Light & Noise – night operations

Camera Vibration – unstable mounts

Real-Time Constraints – limited processing time per frame


Traditional OCR systems fail because they operate directly on degraded frames.

🔥 RailVision AI Solution

RailVision AI solves this by introducing an intelligent, real-time video restoration pipeline:

1. Analyze every frame quality


2. Conditionally restore only degraded frames


3. Enhance visual clarity


4. Run OCR at controlled intervals



This ensures high accuracy with low latency, making the system suitable for real-time deployment.


---

🚀 Key Features

🧠 Intelligent Frame Processing

Blur Detection (Laplacian Variance)
Each frame is classified as:

Low Blur

Medium Blur

High Blur


Conditional Deblurring (NAFNet)
Only medium and high blur frames are passed to the deep deblurring model, reducing unnecessary compute.

Super-Resolution Enhancement (Real-ESRGAN)
All frames (deblurred + low-blur frames) are enhanced to improve text clarity.

Frame Ordering & Synchronization
Processed frames are reordered to maintain video integrity.

Throttled OCR (EasyOCR)
OCR runs on every 5th–6th frame, sufficient for video text while reducing latency.



---

⚡ Performance Optimizations

Selective Model Invocation
Heavy models run only when needed.

Frame Sampling for OCR
OCR runs at lower frequency without losing meaningful information.

Real-Time Friendly Design
Suitable for live or near-real-time railway monitoring.



---

🏗️ System Architecture (Updated)

Input Video
   ↓
Frame Extraction
   ↓
Blur Detection (Low / Medium / High)
   ↓
Medium + High Blur Frames ──► NAFNet Deblurring
Low Blur Frames ───────────► Skip Deblur
   ↓
All Frames ──► Real-ESRGAN Enhancement
   ↓
Frame Reordering
   ↓
Every 5–6 Frames ──► EasyOCR
   ↓
Wagon Number + Confidence
   ↓
React Dashboard


---

📂 Project Structure (ROI Removed)

hack-innovate-2026/
├── backend/
│   ├── app.py                 # Flask API
│   ├── main_pipeline.py       # Core video pipeline
│   ├── blur_detection/        # Laplacian variance logic
│   ├── deblur/                # NAFNet inference
│   ├── enhancement/           # Real-ESRGAN inference
│   ├── ocr/                   # EasyOCR logic
│   ├── utils/                 # Frame handling utilities
│   └── requirements.txt
│
├── railguard-frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md


---

🛠️ Tech Stack

Backend

Python 3.9+

Flask

PyTorch

OpenCV

EasyOCR


Models Used

Blur Detection – Laplacian Variance

Deblurring – NAFNet (Image Restoration)

Enhancement – Real-ESRGAN

OCR – EasyOCR


Frontend

React 18

Modern dashboard UI



---

🧪 Main Processing Pipeline

Video Input
 → Frame Split
 → Blur Detection (Low / Medium / High)
 → Medium + High → NAFNet Deblur
 → Low → Skip Deblur
 → All Frames → Real-ESRGAN Enhance
 → Frame Ordering
 → Every 6th Frame → EasyOCR
 → Output: Text + Confidence


---

🚀 Getting Started

🔧 Prerequisites

Python 3.9+

GPU recommended (CPU supported)



---

1️⃣ Backend Setup

cd backend
pip install -r requirements.txt

📥 Download Model Weights

NAFNet (Deblurring)
Download and place in backend/deblur/:

NAFNet-GoPro-width64.pth

🔗 https://huggingface.co/mikestealth/nafnet-models/blob/main/NAFNet-GoPro-width64.pth


---

Real-ESRGAN (Enhancement)
Download and place in backend/enhancement/:

RealESRGAN_x4plus.pth

🔗 https://huggingface.co/lllyasviel/Annotators/blob/main/RealESRGAN_x4plus.pth


---

▶️ Run Pipeline Manually

python main_pipeline.py --input input_video/test.mp4 --output output.mp4

▶️ Run Flask API

python app.py


---

2️⃣ Frontend Setup

cd railguard-frontend
npm install
npm run dev


---

📊 Optimization Results

Metric	Traditional OCR	RailVision AI

Deblur Invocation	Every frame	Only medium & high blur
OCR Frequency	Every frame	Every 6th frame
Processing Speed	Slow	4–5× faster
OCR Accuracy	Low	High & Stable



---

🔮 Future Roadmap

[ ] Video-aware deblurring (BasicVSR++)

[ ] TensorRT acceleration

[ ] Live RTSP stream support

[ ] Edge deployment (Jetson)



---

<p align="center">
Built with ❤️ for <strong>Hack Innovate 2026</strong><br/>
by <strong>Team Unk0wn C0ders</strong>
</p>
---



Bas bol 🔥
