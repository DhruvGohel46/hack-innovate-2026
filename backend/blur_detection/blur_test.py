import cv2
import numpy as np


def blur_score(image):
    """
    Calculate blur score using Laplacian variance and edge density.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        tuple: (laplacian_variance, edge_density)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Laplacian variance
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Edge density
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.sum(edges > 0) / edges.size

    return lap_var, edge_density


def blur_level(image):
    """
    Determine blur level: low, medium, or high.
    
    Args:
        image: Input image (BGR format)
    
    Returns:
        str: 'low', 'medium', or 'high'
    """
    lap, edge = blur_score(image)

    # Tighter thresholds - only real blur gets deblurred
    if lap > 1080:
        return "low"
    elif lap > 40:
        return "medium"
    else:
        return "high"
    
