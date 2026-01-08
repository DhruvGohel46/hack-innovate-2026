import torch
import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path


class RealESRGANEnhancer:
    """
    Real-ESRGAN enhancement inference module.
    Uses the CORRECT Real-ESRGAN API: RealESRGANer (not RealESRGAN class).
    Weights should be placed at: enhancement/realesr-general-x4v3.pth or RealESRGAN_x4plus.pth
    """
    
    def __init__(self, model_path=None, scale=2, device=None):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scale = scale
        self.upsampler = None
        
        # Auto-detect weights if not provided (try multiple variants)
        if model_path is None:
            # Try different weight file names in order of preference
            weight_paths = [
                ("RealESRGAN_x4plus.pth", 4),  # Primary weight file
                ("RealESRGAN_x2.pth", 2),
                ("RealESRGAN_x2plus.pth", 2),
                ("realesr-general-x4v3.pth", 4),  # Fallback
            ]
            
            for weight_name, weight_scale in weight_paths:
                default_path = Path(__file__).parent / weight_name
                if default_path.exists():
                    model_path = str(default_path)
                    if scale != weight_scale:
                        print(f"[INFO] Found {weight_name}, updating scale to {weight_scale}")
                        scale = weight_scale
                        self.scale = weight_scale
                    print(f"[OK] Auto-detected Real-ESRGAN weights: {model_path} (scale={weight_scale}x)")
                    break
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path, scale)
        else:
            print("[WARNING] Real-ESRGAN weights not found. Using fallback method.")
            print(f"   Expected locations (checked in order):")
            print(f"     - {Path(__file__).parent / 'RealESRGAN_x4plus.pth'} (x4, recommended)")
            print(f"     - {Path(__file__).parent / 'RealESRGAN_x2.pth'} (x2)")
            print(f"     - {Path(__file__).parent / 'RealESRGAN_x2plus.pth'} (x2)")
    
    def load_model(self, model_path, scale=2):
        """Load Real-ESRGAN model using CORRECT API."""
        try:
            # CORRECT IMPORTS (Official Real-ESRGAN way)
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            
            # Use RRDBNet for RealESRGAN_x4plus (standard architecture)
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=scale,
            )
            
            # Create RealESRGANer (CORRECT wrapper)
            self.upsampler = RealESRGANer(
                scale=scale,
                model_path=model_path,
                model=model,
                tile=0,  # 0 = no tiling (faster, more memory)
                tile_pad=10,
                pre_pad=0,
                half=self.device.type != 'cpu',  # Use FP16 on GPU
                device=self.device,
            )
            
            print(f"[OK] Real-ESRGAN loaded correctly: {model_path} (x{scale})")
            print(f"   Device: {self.device}, Architecture: RRDBNet")
            
        except ImportError as e:
            print(f"[ERROR] Real-ESRGAN dependencies not found: {e}")
            print("   Install with: pip install realesrgan basicsr")
            print("   Using simple enhancement fallback.")
            self.upsampler = None
        except Exception as e:
            print(f"[ERROR] Error loading Real-ESRGAN: {e}")
            print("   Using simple enhancement fallback.")
            self.upsampler = None
    
    def enhance_image(self, img):
        """
        Enhance a single image.
        
        Args:
            img: Input image (BGR format, numpy array)
        
        Returns:
            Enhanced image (BGR format, numpy array)
        """
        if self.upsampler is None:
            # Fallback: Simple upscaling and sharpening
            return self._simple_enhance(img)
        
        try:
            # Convert BGR to RGB (RealESRGAN expects RGB)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Enhance using RealESRGANer (CORRECT API)
            output, _ = self.upsampler.enhance(img_rgb, outscale=self.scale)
            
            # Convert RGB back to BGR
            output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
            
            return output_bgr
        except Exception as e:
            print(f"[WARNING] Error in Real-ESRGAN inference: {e}")
            print("   Falling back to simple enhancement method.")
            return self._simple_enhance(img)
    
    def _simple_enhance(self, img):
        """Simple enhancement fallback using interpolation and sharpening."""
        # Upscale using Lanczos interpolation
        h, w = img.shape[:2]
        upscaled = cv2.resize(img, (w * self.scale, h * self.scale), 
                             interpolation=cv2.INTER_LANCZOS4)
        
        # Apply sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(upscaled, -1, kernel)
        
        # Blend original and sharpened
        result = cv2.addWeighted(upscaled, 0.7, sharpened, 0.3, 0)
        
        return result


# Global instance
_enhancer_model = None


def get_enhancer_model(model_path=None, scale=2):
    """Get or create global enhancer model instance."""
    global _enhancer_model
    if _enhancer_model is None:
        _enhancer_model = RealESRGANEnhancer(model_path=model_path, scale=scale)
    return _enhancer_model


def enhance_image(img, model_path=None, scale=2):
    """
    Convenience function to enhance an image.
    
    Args:
        img: Input image (BGR format)
        model_path: Path to Real-ESRGAN weights (optional, auto-detects if None)
        scale: Upscaling factor (default: 2)
    
    Returns:
        Enhanced image
    """
    model = get_enhancer_model(model_path, scale)
    return model.enhance_image(img)
