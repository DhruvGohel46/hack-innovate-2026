<<<<<<< HEAD
# Video Restoration Flask API

Flask backend API for video restoration pipeline that connects with the React frontend.

## Features

1. **Single Frame Processing** (`/api/process/frame`)
   - Upload an image file
   - Returns deblurred and enhanced images
   - Shows side-by-side comparison
   - Provides confidence level from OCR analysis

2. **Video Processing** (`/api/process/video`)
   - Upload a video file
   - Processes all frames
   - Returns 10 sample frames with comparisons
   - Shows confidence levels for each sample frame

## Quick Start (Windows)

### Option 1: Automated Start (Recommended)

Simply run the batch file from the root directory:

```bash
run.bat
```

This will:
- Check for Python and Node.js
- Create virtual environment if needed
- Install backend dependencies if needed
- Install frontend dependencies if needed
- Start both backend and frontend in separate windows

**Quick Start (No Checks):**
```bash
run-simple.bat
```
Faster startup without dependency checks (use if already set up)

**Stop Servers:**
```bash
stop.bat
```

### Option 2: Manual Setup

#### Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Ensure model weights are in place:
   - `backend/deblur/nafnet.pth`
   - `backend/enhancement/RealESRGAN_x2.pth`

3. Run the Flask server:
```bash
cd backend
python app.py
```

The server will run on `http://localhost:5000`

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Update API URL if needed (default is `http://localhost:5000`):
   - Edit `frontend/src/services/api.js`
   - Change `API_BASE_URL` if your Flask server runs on a different port

3. Run the React app:
```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

## API Endpoints

### POST `/api/process/frame`
Process a single image frame.

**Request:**
- Form data with `image` file

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing"
}
```

### POST `/api/process/video`
Process a video file.

**Request:**
- Form data with `video` file

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing"
}
```

### GET `/api/status/<job_id>`
Get processing status for a job.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing" | "completed" | "error",
  ...
}
```

### GET `/api/result/<job_id>`
Get processing results for a completed job.

**Response (for image):**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "blur_detection": {
    "level": "low|medium|high",
    "laplacian_variance": 123.45,
    "edge_density": 0.1234
  },
  "images": {
    "original": "base64...",
    "deblurred": "base64...",
    "enhanced": "base64...",
    "comparison": "base64..."
  },
  "ocr_result": {
    "blur_confidence": 0.85,
    "enhanced_confidence": 0.92,
    "improvement": 0.07
  },
  "confidence_level": 0.92
}
```

**Response (for video):**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "total_frames": 100,
  "processed_frames": 10,
  "sample_frames": [
    {
      "frame_id": "000000",
      "frame_number": 0,
      "blur_level": "medium",
      "images": {
        "before": "base64...",
        "enhanced": "base64...",
        "comparison": "base64..."
      },
      "ocr_result": {
        "blur_confidence": 0.85,
        "enhanced_confidence": 0.92,
        "improvement": 0.07
      },
      "confidence_level": 0.92
    },
    ...
  ]
}
```

## Directory Structure

```
backend/
  ├── app.py                  # Flask application
  ├── test_frame.py          # Single frame processing logic
  ├── main_pipeline.py       # Video processing logic
  ├── uploads/               # Uploaded files (created automatically)
  ├── api_outputs/           # Processing outputs (created automatically)
  ├── static/
  │   └── results/           # Served result images
  └── frames/                # Video frame processing directory (created automatically)
      ├── original/
      ├── blurred/
      ├── deblurred/
      └── enhanced/

frontend/
  ├── src/
  │   ├── App.jsx            # Main React component
  │   ├── App.css            # Styles
  │   └── services/
  │       └── api.js         # API client
  └── public/
```

## Usage

1. Start the Flask backend server
2. Start the React frontend
3. Open `http://localhost:3000` in your browser
4. Upload an image or video file
5. Wait for processing to complete
6. View the results with side-by-side comparisons and confidence levels

## Notes

- Processing happens asynchronously in background threads
- Results are stored temporarily and can be accessed via job_id
- Large videos may take significant time to process
- OCR processing requires EasyOCR (included in requirements.txt)
=======
# RailVision AI - Advanced Wagon Monitoring System

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/backend-Python%203.9+-yellow.svg) ![React](https://img.shields.io/badge/frontend-React%2018-blue.svg) ![Pytorch](https://img.shields.io/badge/AI-Pytorch%20%7C%20OpenCV-orange.svg)

**RailVision AI** is a state-of-the-art automated video restoration and Optical Character Recognition (OCR) pipeline designed for high-speed railway logistics. It specializes in extracting wagon identifiers from noisy, blurry, and low-light footage captured by trackside cameras.

---

## 🎯 Problem Statement
In automated railway logistics, accurately reading wagon numbers is critical. However, trackside cameras often produce degraded footage due to:
*   **Motion Blur**: High-speed trains passing cameras.
*   **Low Light/Noise**: Nighttime operations causing sensor grain.
*   **Vibration**: Unstable camera mounts.

Standard OCR engines fail on such "dirty" signals. **RailVision AI** solves this by reconstructing the signal *before* OCR.

---

## 🚀 Key Features

### 🧠 Intelligent Signal Processing
*   **Static ROI Extraction**: Automatically isolates the text region (processing only **~8%** of the frame), reducing compute load by 92%.
*   **Adaptive Denoising**: Context-aware `Non-Local Means` denoising that adjusts strength based on lighting conditions (Day/Night).
*   **Conditional Deblurring (NAFNet)**: A deep learning based deblurring model that activates only when motion blur is detected.
*   **Super-Resolution (Real-ESRGAN)**: Enhances text resolution for distant or small characters.
*   **Contrast Normalization (CLAHE)**: Locally adaptive histogram equalization to maximize character separability.

### ⚡ Performance Optimized
*   **Throttled Inference**: Heavy AI models run at optimized intervals (e.g., 15 FPS) with result caching, achieving **~4x speedup**.
*   **Latency**: Processed at ~1.2s per frame on CPU (Production ready).

### 🖥️ Modern Dashboard
*   **React-based UI**: sleek, dark-mode interface for video upload and real-time monitoring.
*   **Live Metrics**: Track OCR accuracy, frame processing speed, and wagon counts.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Input[Input Video Stream] --> BlurDetect[Blur Detection & Quality Check]
    
    subgraph "Signal Restoration Engine (Backend)"
        BlurDetect -- "High Blur/Noise" --> ROI[Static ROI Extraction]
        ROI --> Denoise[Adaptive Denoising\n(NLMeans)]
        Denoise --> NAFNet[Deep Deblurring\n(NAFNet - 1 Pass)]
        NAFNet -- "If Resolution Low" --> SR[Super-Resolution\n(Real-ESRGAN)]
        NAFNet -- "If Resolution OK" --> SkipSR[Skip Enhancement]
        SR --> CLAHE[Contrast Normalization]
        SkipSR --> CLAHE
    end
    
    CLAHE --> OCR[OCR Engine\n(Tesseract/PaddleOCR)]
    OCR --> JSON[Wagon ID & Confidence]
    
    subgraph "Visualization (Frontend)"
        JSON --> Dashboard[React Dashboard]
        CLAHE --> VideoOut[Recomposed Video]
        VideoOut --> Dashboard
    end
```

---

## 📂 Project Structure

```text
hack-innovate-2026/
├── backend/                  # Python Restoration Engine
│   ├── blur_detection/       # Laplacian Variance Logic
│   ├── deblur/               # NAFNet Model & Inference
│   ├── enhancement/          # Real-ESRGAN & Fallbacks
│   ├── roi/                  # Static ROI Extraction Module
│   ├── main_pipeline.py      # Core Orchestrator
│   └── requirements.txt      # Python Dependencies
├── railguard-frontend/       # React Dashboard
│   ├── src/                  # Components & UI Logic
│   ├── package.json          # Node Dependencies
│   └── public/               # Static Assets
└── README.md                 # Documentation
```

---

## 🛠️ Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js 16+
*   GPU (Recommended for NAFNet/Real-ESRGAN, but runs on CPU)

### 1. Backend Setup (Restoration Engine)
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the pipeline test
python main_pipeline.py --input input_video/test.mp4 --output output.mp4
```

### 2. Frontend Setup (Dashboard)
```bash
cd railguard-frontend

# Install dependencies
npm install

# Start Development Server
npm run dev
```

---

## 🧪 Optimization Metrics

| Metric | Unoptimized | RailVision Optimized | Improvement |
| :--- | :--- | :--- | :--- |
| **ROI Coverage** | 100% (Full Frame) | **7.91%** | **92% Reduction** |
| **Inference Time** | ~6.0s / frame | **~1.2s / frame** | **5x Faster** |
| **OCR Accuracy** | < 40% (Noisy) | **> 90%** | **Major Boost** |

---

## 🔮 Future Roadmap
- [ ] **Dynamic ROI**: Implement DBNet-lite for periodic ROI re-centering to handle camera vibrations.
- [ ] **Edge Deployment**: Port NAFNet to TensorRT for Jetson Nano deployment.
- [ ] **Live RTSP Support**: Connect directly to IP cameras.

---

<p align="center">
  Built with ❤️ for Hack Innovate 2026 by Team Unk0wn C0ders
</p>
>>>>>>> 9d402c57cfc143ed15f00ccaf4ebbdae0d0983e5
