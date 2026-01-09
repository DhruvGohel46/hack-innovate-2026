"""
Flask application for video restoration pipeline.
Provides REST API endpoints for single frame and video processing.
"""

import os
import sys
import json
import base64
import cv2
import numpy as np
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import threading
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test_frame import test_single_frame, create_comparison
from main_pipeline import process_video
from blur_detection.blur_test import blur_level, blur_score

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'api_outputs'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('static/results', exist_ok=True)

# Store processing jobs
processing_jobs = {}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def encode_image_to_base64(image_path):
    """Encode image file to base64 string."""
    if not os.path.exists(image_path):
        return None
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def process_single_frame_helper(input_path, output_dir, job_id):
    """Helper function to process single frame and return results."""
    try:
        # Import OCR functions
        try:
            from ocr.ocr_engine import get_ocr_engine, avg_confidence, filter_main_text
            OCR_AVAILABLE = True
        except ImportError:
            OCR_AVAILABLE = False
        
        # Load image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not load image from {input_path}")
        
        # Get blur detection results
        lap_var, edge_density = blur_score(img)
        level = blur_level(img)
        
        # Save original
        original_path = os.path.join(output_dir, "0_original.png")
        cv2.imwrite(original_path, img)
        
        # Process deblurring
        from deblur.nafnet_infer import deblur_image
        deblurred_img = None
        deblurred_path = None
        
        if level in ["medium", "high"]:
            if level == "medium":
                deblurred_img = deblur_image(img)
            elif level == "high":
                deblurred_img = deblur_image(img)
                deblurred_img = deblur_image(deblurred_img)  # Second pass
            
            deblurred_path = os.path.join(output_dir, "1_deblurred.png")
            cv2.imwrite(deblurred_path, deblurred_img)
        else:
            deblurred_img = img.copy()
            deblurred_path = original_path
        
        # Process enhancement
        from enhancement.realesrgan_infer import enhance_image
        enhanced_img = enhance_image(
            deblurred_img if deblurred_img is not None else img,
            scale=2
        )
        enhanced_path = os.path.join(output_dir, "2_enhanced.png")
        cv2.imwrite(enhanced_path, enhanced_img)
        
        # Create comparison image
        comparison = create_comparison(img, deblurred_img, enhanced_img)
        comparison_path = os.path.join(output_dir, "3_comparison.png")
        cv2.imwrite(comparison_path, comparison)
        
        # OCR comparison
        ocr_result = None
        confidence_level = None
        if OCR_AVAILABLE:
            try:
                ocr_engine = get_ocr_engine(gpu=True)
                blur_ocr = ocr_engine.run_ocr(img)
                enhanced_ocr = ocr_engine.run_ocr(enhanced_img)
                
                blur_avg = avg_confidence(blur_ocr)
                enhanced_avg = avg_confidence(enhanced_ocr)
                
                ocr_result = {
                    "blur_confidence": round(blur_avg, 3),
                    "enhanced_confidence": round(enhanced_avg, 3),
                    "improvement": round(enhanced_avg - blur_avg, 3),
                    "blur_text_count": len(blur_ocr),
                    "enhanced_text_count": len(enhanced_ocr)
                }
                confidence_level = round(enhanced_avg, 3)
            except Exception as e:
                print(f"OCR processing failed: {e}")
                ocr_result = None
        
        # Encode images to base64
        original_b64 = encode_image_to_base64(original_path)
        deblurred_b64 = encode_image_to_base64(deblurred_path) if deblurred_path else original_b64
        enhanced_b64 = encode_image_to_base64(enhanced_path)
        comparison_b64 = encode_image_to_base64(comparison_path)
        
        # Return results
        result = {
            "job_id": job_id,
            "status": "completed",
            "blur_detection": {
                "level": level,
                "laplacian_variance": round(lap_var, 2),
                "edge_density": round(edge_density, 4)
            },
            "images": {
                "original": original_b64,
                "deblurred": deblurred_b64,
                "enhanced": enhanced_b64,
                "comparison": comparison_b64
            },
            "image_paths": {
                "original": f"/static/results/{job_id}/0_original.png",
                "deblurred": f"/static/results/{job_id}/1_deblurred.png",
                "enhanced": f"/static/results/{job_id}/2_enhanced.png",
                "comparison": f"/static/results/{job_id}/3_comparison.png"
            },
            "ocr_result": ocr_result,
            "confidence_level": confidence_level
        }
        
        # Copy files to static directory for serving
        static_dir = os.path.join('static', 'results', job_id)
        os.makedirs(static_dir, exist_ok=True)
        
        import shutil
        shutil.copy(original_path, os.path.join(static_dir, "0_original.png"))
        if deblurred_path and deblurred_path != original_path:
            shutil.copy(deblurred_path, os.path.join(static_dir, "1_deblurred.png"))
        shutil.copy(enhanced_path, os.path.join(static_dir, "2_enhanced.png"))
        shutil.copy(comparison_path, os.path.join(static_dir, "3_comparison.png"))
        
        processing_jobs[job_id] = result
        return result
        
    except Exception as e:
        processing_jobs[job_id] = {
            "job_id": job_id,
            "status": "error",
            "error": str(e)
        }
        raise

def process_video_helper(input_path, output_path, job_id):
    """Helper function to process video and return sample frames."""
    try:
        # Process video (this will save frames to frames/ directory)
        process_video(
            input_path=input_path,
            output_path=output_path,
            enhance_scale=2,
            skip_frames=1,
            process_blurred_only=True
        )
        
        # Get sample frames (10 frames evenly distributed)
        frames_dir = Path("frames")
        original_dir = frames_dir / "original"
        enhanced_dir = frames_dir / "enhanced"
        blurred_dir = frames_dir / "blurred"
        deblurred_dir = frames_dir / "deblurred"
        
        # Get all frame files
        frame_files = sorted([f for f in os.listdir(original_dir) if f.endswith('.png')])
        
        if not frame_files:
            raise ValueError("No frames were processed")
        
        # Select 10 evenly distributed frames
        total_frames = len(frame_files)
        if total_frames > 0:
            step = max(1, total_frames // 10)
            selected_frames = frame_files[::step][:10]
        else:
            selected_frames = []
        
        sample_frames = []
        
        for frame_file in selected_frames:
            frame_id = frame_file.replace('.png', '')
            
            # Load images
            original_path = original_dir / frame_file
            enhanced_path = enhanced_dir / frame_file
            blurred_path = blurred_dir / frame_file if (blurred_dir / frame_file).exists() else None
            deblurred_path = deblurred_dir / frame_file if (deblurred_dir / frame_file).exists() else None
            
            # Use blurred if exists, otherwise original
            blur_img_path = blurred_path if blurred_path else original_path
            before_img = cv2.imread(str(blur_img_path))
            enhanced_img = cv2.imread(str(enhanced_path))
            
            if before_img is None or enhanced_img is None:
                continue
            
            # Create comparison
            comparison = create_comparison(before_img, before_img, enhanced_img)
            
            # Save comparison to static
            static_dir = Path('static') / 'results' / job_id / 'frames'
            static_dir.mkdir(parents=True, exist_ok=True)
            
            comparison_path = static_dir / f"comparison_{frame_id}.png"
            cv2.imwrite(str(comparison_path), comparison)
            
            # Also save individual images
            before_save_path = static_dir / f"{frame_id}_before.png"
            enhanced_save_path = static_dir / f"{frame_id}_enhanced.png"
            cv2.imwrite(str(before_save_path), before_img)
            cv2.imwrite(str(enhanced_save_path), enhanced_img)
            
            # Get blur level
            level = blur_level(before_img)
            
            # OCR result if available
            ocr_result = None
            confidence_level = None
            try:
                from ocr.ocr_engine import get_ocr_engine, avg_confidence
                ocr_engine = get_ocr_engine(gpu=True)
                
                blur_ocr = ocr_engine.run_ocr(before_img)
                enhanced_ocr = ocr_engine.run_ocr(enhanced_img)
                
                blur_avg = avg_confidence(blur_ocr)
                enhanced_avg = avg_confidence(enhanced_ocr)
                
                ocr_result = {
                    "blur_confidence": round(blur_avg, 3),
                    "enhanced_confidence": round(enhanced_avg, 3),
                    "improvement": round(enhanced_avg - blur_avg, 3)
                }
                confidence_level = round(enhanced_avg, 3)
            except Exception as e:
                print(f"OCR processing failed for frame {frame_id}: {e}")
            
            # Encode images
            before_b64 = encode_image_to_base64(str(blur_img_path))
            enhanced_b64 = encode_image_to_base64(str(enhanced_path))
            comparison_b64 = encode_image_to_base64(str(comparison_path))
            
            sample_frames.append({
                "frame_id": frame_id,
                "frame_number": int(frame_id),
                "blur_level": level,
                "images": {
                    "before": before_b64,
                    "enhanced": enhanced_b64,
                    "comparison": comparison_b64
                },
                "image_paths": {
                    "before": f"/static/results/{job_id}/frames/{frame_id}_before.png",
                    "enhanced": f"/static/results/{job_id}/frames/{frame_id}_enhanced.png",
                    "comparison": f"/static/results/{job_id}/frames/comparison_{frame_id}.png"
                },
                "ocr_result": ocr_result,
                "confidence_level": confidence_level
            })
        
        result = {
            "job_id": job_id,
            "status": "completed",
            "total_frames": total_frames,
            "processed_frames": len(selected_frames),
            "sample_frames": sample_frames,
            "output_video": output_path
        }
        
        processing_jobs[job_id] = result
        return result
        
    except Exception as e:
        processing_jobs[job_id] = {
            "job_id": job_id,
            "status": "error",
            "error": str(e)
        }
        raise

@app.route('/')
def index():
    return jsonify({"message": "Video Restoration API", "version": "1.0"})

@app.route('/api/process/frame', methods=['POST'])
def process_frame():
    """Process a single frame image."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({"error": "Invalid file type. Allowed: PNG, JPG, JPEG"}), 400
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    upload_dir = os.path.join(UPLOAD_FOLDER, job_id)
    output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    input_path = os.path.join(upload_dir, filename)
    file.save(input_path)
    
    # Update job status
    processing_jobs[job_id] = {"job_id": job_id, "status": "processing"}
    
    # Process in background thread
    def process():
        try:
            process_single_frame_helper(input_path, output_dir, job_id)
        except Exception as e:
            processing_jobs[job_id] = {
                "job_id": job_id,
                "status": "error",
                "error": str(e)
            }
    
    thread = threading.Thread(target=process)
    thread.start()
    
    # Return immediately with job ID
    return jsonify({
        "job_id": job_id,
        "status": "processing",
        "message": "Frame processing started"
    }), 202

@app.route('/api/process/video', methods=['POST'])
def process_video_endpoint():
    """Process a video file."""
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        return jsonify({"error": "Invalid file type. Allowed: MP4, AVI, MOV, MKV"}), 400
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    upload_dir = os.path.join(UPLOAD_FOLDER, job_id)
    output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    input_path = os.path.join(upload_dir, filename)
    output_path = os.path.join(output_dir, "output.mp4")
    file.save(input_path)
    
    # Update job status
    processing_jobs[job_id] = {"job_id": job_id, "status": "processing"}
    
    # Process in background thread
    def process():
        try:
            process_video_helper(input_path, output_path, job_id)
        except Exception as e:
            processing_jobs[job_id] = {
                "job_id": job_id,
                "status": "error",
                "error": str(e)
            }
    
    thread = threading.Thread(target=process)
    thread.start()
    
    # Return immediately with job ID
    return jsonify({
        "job_id": job_id,
        "status": "processing",
        "message": "Video processing started"
    }), 202

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status for a job."""
    if job_id not in processing_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    result = processing_jobs[job_id]
    return jsonify(result), 200

@app.route('/api/result/<job_id>', methods=['GET'])
def get_result(job_id):
    """Get processing results for a job."""
    if job_id not in processing_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    result = processing_jobs[job_id]
    
    if result.get("status") == "processing":
        return jsonify({
            "job_id": job_id,
            "status": "processing",
            "message": "Processing is still in progress"
        }), 202
    
    return jsonify(result), 200

@app.route('/static/results/<path:filename>')
def serve_result(filename):
    """Serve result images."""
    static_path = Path(__file__).parent / 'static' / 'results'
    # Handle nested paths like job_id/frames/filename.png
    file_path = static_path / filename
    if file_path.exists() and file_path.is_file():
        directory = str(file_path.parent)
        file = file_path.name
        return send_from_directory(directory, file)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
