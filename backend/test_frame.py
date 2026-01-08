"""
Single frame testing script for video restoration pipeline.
Tests blur detection, deblurring, and enhancement on a single image.
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path
import argparse

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from blur_detection.blur_test import blur_level, blur_score
from deblur.nafnet_infer import deblur_image
from enhancement.realesrgan_infer import enhance_image


def test_single_frame(
    input_path,
    output_dir="output",
    deblur_model_path=None,
    enhance_model_path=None,
    enhance_scale=2,
    show_results=True
):
    """
    Test all models on a single frame.
    
    Auto-detects weights in default locations:
    - deblur/nafnet.pth
    - enhancement/RealESRGAN_x2.pth
    
    Args:
        input_path: Path to input image
        output_dir: Directory to save results
        deblur_model_path: Path to NAFNet weights (optional, auto-detects if None)
        enhance_model_path: Path to Real-ESRGAN weights (optional, auto-detects if None)
        enhance_scale: Upscaling factor for enhancement (default: 2)
        show_results: Display results using cv2.imshow (default: True)
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
    
    # Check if input image exists
    if not os.path.exists(input_path):
        print(f"[ERROR] Input image not found at {input_path}")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load input image
    print(f"📸 Loading image: {input_path}")
    img = cv2.imread(input_path)
    if img is None:
        print(f"[ERROR] Could not load image from {input_path}")
        return
    
    h, w = img.shape[:2]
    print(f"   Image size: {w}x{h}")
    
    # Save original (PNG for lossless quality)
    original_path = os.path.join(output_dir, "0_original.png")
    cv2.imwrite(original_path, img)
    print(f"[OK] Saved original: {original_path}")
    
    # Step 1: Blur Detection
    print("\n🔍 Step 1: Blur Detection")
    lap_var, edge_density = blur_score(img)
    level = blur_level(img)
    print(f"   Laplacian variance: {lap_var:.2f}")
    print(f"   Edge density: {edge_density:.4f}")
    print(f"   Blur level: {level.upper()}")
    
    # Save blur info
    blur_info_path = os.path.join(output_dir, "blur_info.txt")
    with open(blur_info_path, 'w') as f:
        f.write(f"Blur Detection Results\n")
        f.write(f"{'='*40}\n")
        f.write(f"Laplacian variance: {lap_var:.2f}\n")
        f.write(f"Edge density: {edge_density:.4f}\n")
        f.write(f"Blur level: {level.upper()}\n")
    print(f"[OK] Saved blur info: {blur_info_path}")
    
    # Step 2: Deblurring (if needed) - with double-pass for high blur
    deblurred_img = None
    if level in ["medium", "high"]:
        print(f"\n🔧 Step 2: Deblurring (blur level: {level})")
        
        if level == "medium":
            print("   Processing with NAFNet (1 pass)...")
            deblurred_img = deblur_image(img, model_path=deblur_model_path)
        elif level == "high":
            print("   Processing with NAFNet (2 passes for heavy blur)...")
            deblurred_img = deblur_image(img, model_path=deblur_model_path)
            deblurred_img = deblur_image(deblurred_img, model_path=deblur_model_path)  # Second pass
        
        deblurred_path = os.path.join(output_dir, "1_deblurred.png")
        cv2.imwrite(deblurred_path, deblurred_img)
        print(f"[OK] Saved deblurred: {deblurred_path}")
        
        # Compare blur scores
        lap_var_deblur, edge_density_deblur = blur_score(deblurred_img)
        level_deblur = blur_level(deblurred_img)
        print(f"   After deblur - Laplacian: {lap_var_deblur:.2f}, Edge: {edge_density_deblur:.4f}, Level: {level_deblur.upper()}")
    else:
        print(f"\n⏭️  Step 2: Skipping deblur (blur level: {level} - no deblur needed)")
        deblurred_img = img.copy()
    
    # Step 3: Enhancement
    print(f"\n✨ Step 3: Enhancement (scale: {enhance_scale}x)")
    print("   Processing with Real-ESRGAN...")
    enhanced_img = enhance_image(
        deblurred_img if deblurred_img is not None else img,
        model_path=enhance_model_path,
        scale=enhance_scale
    )
    enhanced_path = os.path.join(output_dir, "2_enhanced.png")
    cv2.imwrite(enhanced_path, enhanced_img)
    print(f"[OK] Saved enhanced: {enhanced_path}")
    
    eh, ew = enhanced_img.shape[:2]
    print(f"   Enhanced size: {ew}x{eh}")
    
    # Create comparison image
    print(f"\n📊 Creating comparison image...")
    comparison = create_comparison(img, deblurred_img if deblurred_img is not None else img, enhanced_img)
    comparison_path = os.path.join(output_dir, "3_comparison.png")
    cv2.imwrite(comparison_path, comparison)
    print(f"[OK] Saved comparison: {comparison_path}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"[OK] Testing complete!")
    print(f"   Input: {input_path}")
    print(f"   Output directory: {output_dir}")
    print(f"   Blur level: {level.upper()}")
    print(f"   Deblurred: {'Yes' if level in ['medium', 'high'] else 'No (not needed)'}")
    print(f"   Enhanced: Yes ({enhance_scale}x)")
    print(f"{'='*50}\n")
    
    # Display results if requested
    if show_results:
        print("Press any key to close windows...")
        cv2.imshow("Original", resize_for_display(img))
        if deblurred_img is not None and not np.array_equal(deblurred_img, img):
            cv2.imshow("Deblurred", resize_for_display(deblurred_img))
        cv2.imshow("Enhanced", resize_for_display(enhanced_img))
        cv2.imshow("Comparison", resize_for_display(comparison))
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def create_comparison(original, deblurred, enhanced):
    """
    Create a side-by-side comparison image.
    
    Args:
        original: Original image
        deblurred: Deblurred image
        enhanced: Enhanced image
    
    Returns:
        Comparison image
    """
    # Resize all images to same height for comparison
    target_h = max(original.shape[0], deblurred.shape[0], enhanced.shape[0])
    
    # Resize images maintaining aspect ratio
    def resize_to_height(img, height):
        h, w = img.shape[:2]
        scale = height / h
        new_w = int(w * scale)
        return cv2.resize(img, (new_w, height))
    
    orig_resized = resize_to_height(original, target_h)
    deblur_resized = resize_to_height(deblurred, target_h)
    enh_resized = resize_to_height(enhanced, target_h)
    
    # Add labels
    def add_label(img, text):
        labeled = img.copy()
        cv2.putText(labeled, text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return labeled
    
    orig_labeled = add_label(orig_resized, "Original")
    deblur_labeled = add_label(deblur_resized, "Deblurred")
    enh_labeled = add_label(enh_resized, f"Enhanced ({enhanced.shape[1]}x{enhanced.shape[0]})")
    
    # Concatenate horizontally
    comparison = np.hstack([orig_labeled, deblur_labeled, enh_labeled])
    
    return comparison


def resize_for_display(img, max_size=800):
    """
    Resize image for display while maintaining aspect ratio.
    
    Args:
        img: Input image
        max_size: Maximum width or height
    
    Returns:
        Resized image
    """
    h, w = img.shape[:2]
    if max(h, w) <= max_size:
        return img
    
    if h > w:
        scale = max_size / h
    else:
        scale = max_size / w
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test video restoration on a single frame")
    parser.add_argument("--input", "-i", default="input/test_frame.jpg",
                       help="Input image path (default: input/test_frame.jpg)")
    parser.add_argument("--output", "-o", default="output",
                       help="Output directory (default: output)")
    parser.add_argument("--deblur-model", "-d", default=None,
                       help="Path to NAFNet weights (optional)")
    parser.add_argument("--enhance-model", "-e", default=None,
                       help="Path to Real-ESRGAN weights (optional)")
    parser.add_argument("--scale", "-s", type=int, default=2,
                       help="Enhancement upscale factor (default: 2)")
    parser.add_argument("--no-show", action="store_true",
                       help="Don't display results with cv2.imshow")
    
    args = parser.parse_args()
    
    test_single_frame(
        input_path=args.input,
        output_dir=args.output,
        deblur_model_path=args.deblur_model,
        enhance_model_path=args.enhance_model,
        enhance_scale=args.scale,
        show_results=not args.no_show
    )

