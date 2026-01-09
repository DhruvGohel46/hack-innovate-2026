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
