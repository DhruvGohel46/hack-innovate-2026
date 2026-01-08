import cv2
import os
import sys
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from blur_detection.blur_test import blur_level
from deblur.nafnet_infer import deblur_image
from enhancement.realesrgan_infer import enhance_image


def process_video(
    input_path="input_video/input.mp4",
    output_path="output_video/final.mp4",
    deblur_model_path=None,
    enhance_model_path=None,
    enhance_scale=2,
    skip_frames=1,
    process_blurred_only=True
):
    """
    Main video restoration pipeline.
    
    Auto-detects weights in default locations:
    - deblur/nafnet.pth
    - enhancement/RealESRGAN_x2.pth
    
    Args:
        input_path: Path to input video
        output_path: Path to output video
        deblur_model_path: Path to NAFNet weights (optional, auto-detects if None)
        enhance_model_path: Path to Real-ESRGAN weights (optional, auto-detects if None)
        enhance_scale: Upscaling factor for enhancement (default: 2)
        skip_frames: Process every Nth frame (default: 1 = all frames)
        process_blurred_only: Only deblur frames with medium/high blur (default: True)
    """
    
    # Auto-detect weights if not provided
    if deblur_model_path is None:
        default_deblur = Path(__file__).parent / "deblur" / "nafnet.pth"
        if default_deblur.exists():
            deblur_model_path = str(default_deblur)
            print(f"[OK] Auto-detected NAFNet weights: {deblur_model_path}")
    
    if enhance_model_path is None:
        default_enhance = Path(__file__).parent / "enhancement" / "RealESRGAN_x2.pth"
        if default_enhance.exists():
            enhance_model_path = str(default_enhance)
            print(f"[OK] Auto-detected Real-ESRGAN weights: {enhance_model_path}")
    
    # Check if input video exists
    if not os.path.exists(input_path):
        print(f"Error: Input video not found at {input_path}")
        return
    
    # Create output directories
    os.makedirs("frames/original", exist_ok=True)
    os.makedirs("frames/blurred", exist_ok=True)
    os.makedirs("frames/deblurred", exist_ok=True)
    os.makedirs("frames/enhanced", exist_ok=True)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video info: {width}x{height} @ {fps} FPS, {total_frames} frames")
    
    # Calculate output dimensions (after enhancement upscaling)
    out_width = width * enhance_scale
    out_height = height * enhance_scale
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (out_width, out_height))
    
    if not out.isOpened():
        print(f"Error: Could not create output video {output_path}")
        cap.release()
        return
    
    frame_id = 0
    processed_count = 0
    deblurred_count = 0
    
    print("\nProcessing video frames...")
    
    # Process frames
    with tqdm(total=total_frames, desc="Processing") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames if needed
            if frame_id % skip_frames != 0:
                frame_id += 1
                pbar.update(1)
                continue
            
            # Save original frame (PNG for lossless quality)
            cv2.imwrite(f"frames/original/{frame_id:06d}.png", frame)
            
            # Detect blur level
            level = blur_level(frame)
            
            # Deblur if needed (with double-pass for high blur)
            if level in ["medium", "high"]:
                if process_blurred_only or not process_blurred_only:
                    cv2.imwrite(f"frames/blurred/{frame_id:06d}.png", frame)
                    
                    # Single pass for medium blur
                    if level == "medium":
                        frame = deblur_image(frame, model_path=deblur_model_path)
                        print(f"Frame {frame_id}: blur={level} → deblur (1 pass) + enhance")
                    # Double pass for high blur (stronger deblurring)
                    elif level == "high":
                        frame = deblur_image(frame, model_path=deblur_model_path)
                        frame = deblur_image(frame, model_path=deblur_model_path)  # Second pass
                        print(f"Frame {frame_id}: blur={level} → deblur (2 passes) + enhance")
                    
                    cv2.imwrite(f"frames/deblurred/{frame_id:06d}.png", frame)
                    deblurred_count += 1
            else:
                print(f"Frame {frame_id}: blur={level} → enhance only (no deblur needed)")
            
            # Enhance frame (always happens after deblur if needed)
            frame = enhance_image(frame, model_path=enhance_model_path, scale=enhance_scale)
            cv2.imwrite(f"frames/enhanced/{frame_id:06d}.png", frame)
            
            # Write to output video
            out.write(frame)
            
            processed_count += 1
            frame_id += 1
            pbar.update(1)
    
    # Release resources
    cap.release()
    out.release()
    
    print(f"\n[OK] Processing complete!")
    print(f"   Processed: {processed_count} frames")
    print(f"   Deblurred: {deblurred_count} frames")
    print(f"   Output: {output_path}")
    print(f"   Output size: {out_width}x{out_height}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Restoration Pipeline")
    parser.add_argument("--input", "-i", default="input_video/input.mp4",
                       help="Input video path")
    parser.add_argument("--output", "-o", default="output_video/final.mp4",
                       help="Output video path")
    parser.add_argument("--deblur-model", "-d", default=None,
                       help="Path to NAFNet weights")
    parser.add_argument("--enhance-model", "-e", default=None,
                       help="Path to Real-ESRGAN weights")
    parser.add_argument("--scale", "-s", type=int, default=2,
                       help="Enhancement upscale factor (default: 2)")
    parser.add_argument("--skip", type=int, default=1,
                       help="Process every Nth frame (default: 1)")
    parser.add_argument("--all-frames", action="store_true",
                       help="Deblur all frames, not just blurred ones")
    
    args = parser.parse_args()
    
    process_video(
        input_path=args.input,
        output_path=args.output,
        deblur_model_path=args.deblur_model,
        enhance_model_path=args.enhance_model,
        enhance_scale=args.scale,
        skip_frames=args.skip,
        process_blurred_only=not args.all_frames
    )
