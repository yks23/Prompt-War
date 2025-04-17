from PIL import Image
import numpy as np
from scipy.spatial.distance import cosine
from skimage.metrics import structural_similarity as ssim
from skimage.feature import hog
from skimage import color
import cv2
import hashlib
import io

class ImageSimilarity:
    """
    A collection of functions for measuring similarity between images.
    Each function returns a float value where lower values indicate greater similarity.
    """
    
    @staticmethod
    def resize_images(img1, img2, size=(224, 224)):
        """Resize both images to the same dimensions for comparison"""
        return img1.resize(size), img2.resize(size)
    
    @staticmethod
    def to_array(img):
        """Convert PIL Image to numpy array"""
        return np.array(img)
    
    @staticmethod
    def pixel_color_loss(img1, img2):
        """
        Calculate absolute color difference between pixels (RGB channels)
        Similar to the original function but normalized to return values between 0-1
        """
        # Resize to same dimensions
        img1, img2 = ImageSimilarity.resize_images(img1, img2)
        
        # Convert to arrays
        arr1 = ImageSimilarity.to_array(img1)
        arr2 = ImageSimilarity.to_array(img2)
        
        # Calculate mean absolute difference across all pixels and channels
        diff = np.mean(np.abs(arr1.astype(float) - arr2.astype(float)))
        
        # Normalize by maximum possible difference (255*3 for RGB)
        return diff / (255 * 3)
    
    @staticmethod
    def structural_similarity(img1, img2):
        """
        Compute the structural similarity index between two images
        Returns a value between 0-1 where 0 means identical images
        """
        # Resize to same dimensions
        img1, img2 = ImageSimilarity.resize_images(img1, img2)
        
        # Convert to grayscale
        gray1 = color.rgb2gray(ImageSimilarity.to_array(img1))
        gray2 = color.rgb2gray(ImageSimilarity.to_array(img2))
        
        # Calculate SSIM
        similarity = ssim(gray1, gray2, data_range=1.0)
        
        # Convert to distance (0 = identical, 1 = completely different)
        return 1.0 - similarity
    
    @staticmethod
    def histogram_comparison(img1, img2, method=cv2.HISTCMP_BHATTACHARYYA):
        """
        Compare color histograms of two images
        Returns a value normalized between 0-1 where lower values indicate similar distributions
        """
        # Resize to same dimensions
        img1, img2 = ImageSimilarity.resize_images(img1, img2)
        
        # Convert PIL to OpenCV format
        cv_img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        cv_img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
        
        # Convert to HSV which is better for color perception
        hsv_img1 = cv2.cvtColor(cv_img1, cv2.COLOR_BGR2HSV)
        hsv_img2 = cv2.cvtColor(cv_img2, cv2.COLOR_BGR2HSV)
        
        # Calculate histograms
        hist1 = cv2.calcHist([hsv_img1], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
        hist2 = cv2.calcHist([hsv_img2], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
        
        # Normalize histograms
        cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
        
        # Compare histograms
        score = cv2.compareHist(hist1, hist2, method)
        
        return score
    
    @staticmethod
    def edge_difference(img1, img2):
        """
        Compare edge features between images
        Returns a value between 0-1 where lower values indicate similar edge structures
        """
        # Resize to same dimensions
        img1, img2 = ImageSimilarity.resize_images(img1, img2)
        
        # Convert PIL to OpenCV format
        cv_img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        cv_img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(cv_img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cv_img2, cv2.COLOR_BGR2GRAY)
        
        # Detect edges using Canny
        edges1 = cv2.Canny(gray1, 100, 200)
        edges2 = cv2.Canny(gray2, 100, 200)
        
        # Calculate the absolute difference between edge maps
        diff = np.mean(np.abs(edges1.astype(float) - edges2.astype(float)))
        
        # Normalize by maximum possible difference (255)
        return diff / 255.0
    
    @staticmethod
    def feature_vector_similarity(img1, img2):
        """
        Compare images using HOG feature vectors
        Returns a value between 0-1 where lower values indicate similar feature structures
        """
        # Resize to same dimensions
        img1, img2 = ImageSimilarity.resize_images(img1, img2, size=(128, 128))
        
        # Convert to grayscale
        gray1 = color.rgb2gray(ImageSimilarity.to_array(img1))
        gray2 = color.rgb2gray(ImageSimilarity.to_array(img2))
        
        # Calculate HOG features
        fd1, _ = hog(gray1, orientations=8, pixels_per_cell=(16, 16),
                   cells_per_block=(1, 1), visualize=True, channel_axis=None)
        fd2, _ = hog(gray2, orientations=8, pixels_per_cell=(16, 16),
                   cells_per_block=(1, 1), visualize=True, channel_axis=None)
        
        # Calculate cosine distance (0 = same direction, 1 = opposite directions)
        distance = cosine(fd1, fd2)
        
        # Normalize to make sure we get a value between 0-1
        return min(1.0, max(0.0, distance))
    
    @staticmethod
    def combined_similarity(img1, img2, weights=None):
        """
        Calculate a weighted combination of different similarity metrics
        Returns a value between 0-1 where lower values indicate greater similarity
        
        Parameters:
        - img1, img2: PIL Image objects
        - weights: Dictionary of weights for each metric (defaults provided if None)
        """
        if weights is None:
            weights = {
                'pixel': 0.15,
                'structural': 0.30,
                'histogram': 0.25,
                'edge': 0.15,
                'feature': 0.15
            }
        
        # Make a copy of the images to avoid modifying originals
        img1_copy = img1.copy()
        img2_copy = img2.copy()
        
        # Calculate individual metrics
        metrics = {
            'pixel': ImageSimilarity.pixel_color_loss(img1_copy, img2_copy),
            'structural': ImageSimilarity.structural_similarity(img1_copy, img2_copy),
            'histogram': ImageSimilarity.histogram_comparison(img1_copy, img2_copy),
            'edge': ImageSimilarity.edge_difference(img1_copy, img2_copy),
            'feature': ImageSimilarity.feature_vector_similarity(img1_copy, img2_copy)
        }
        
        # Calculate weighted average
        total_weight = sum(weights.values())
        weighted_score = sum(metrics[k] * weights[k] for k in weights) / total_weight
        
        return weighted_score, metrics

    @staticmethod
    def get_detailed_similarity(img1, img2):
        """
        Get a detailed breakdown of similarity metrics with explanations
        Returns overall score and dictionary of component scores
        """
        overall, components = ImageSimilarity.combined_similarity(img1, img2)
        
        return {
            'overall_similarity': 1.0 - overall,  # Convert to similarity (1 = identical)
            'overall_loss': overall,
            'components': {
                'pixel_color': {
                    'score': 1.0 - components['pixel'],
                    'description': 'Pixel-by-pixel RGB color similarity'
                },
                'structural': {
                    'score': 1.0 - components['structural'],
                    'description': 'Structural pattern similarity (texture, lighting, structures)'
                },
                'color_distribution': {
                    'score': 1.0 - components['histogram'],
                    'description': 'Overall color palette and distribution similarity'
                },
                'edge_features': {
                    'score': 1.0 - components['edge'],
                    'description': 'Similarity of edges and contours'
                },
                'visual_features': {
                    'score': 1.0 - components['feature'],
                    'description': 'Similarity of detected visual features and patterns'
                }
            }
        }


def get_loss(img1, img2, metric="combined"):
    """
    Calculate the similarity loss between two images using the specified metric.
    
    Parameters:
    - img1, img2: PIL Image objects
    - metric: String indicating which metric to use:
        "pixel" - Basic pixel color difference (original method)
        "structural" - Structural similarity index
        "histogram" - Color histogram comparison
        "edge" - Edge feature difference
        "feature" - HOG feature vector similarity
        "combined" - Weighted combination of all metrics (default)
    
    Returns:
    - Float value between 0-1 where lower values indicate greater similarity
    """
    img1 = img1.convert("RGB")
    img2 = img2.convert("RGB")
    
    if metric == "pixel":
        return ImageSimilarity.pixel_color_loss(img1, img2)
    elif metric == "structural":
        return ImageSimilarity.structural_similarity(img1, img2)
    elif metric == "histogram":
        return ImageSimilarity.histogram_comparison(img1, img2)
    elif metric == "edge":
        return ImageSimilarity.edge_difference(img1, img2)
    elif metric == "feature":
        return ImageSimilarity.feature_vector_similarity(img1, img2)
    elif metric == "combined":
        result, _ = ImageSimilarity.combined_similarity(img1, img2)
        return result
    else:
        raise ValueError(f"Unknown metric: {metric}")


def get_detailed_comparison(img1, img2):
    """
    Get a detailed analysis of image similarity with component breakdowns.
    Returns a dictionary with overall and component scores.
    """
    img1 = img1.convert("RGB")
    img2 = img2.convert("RGB")
    return ImageSimilarity.get_detailed_similarity(img1, img2)


# Example usage
if __name__ == "__main__":
    try:
        # Load two images
        img1 = Image.open("black.png")
        img2 = Image.open("image.png")
        
        # Get basic loss
        loss = get_loss(img1, img2)
        print(f"Combined Similarity Loss: {loss:.4f}")
        
        # Get detailed comparison
        details = get_detailed_comparison(img1, img2)
        print(f"Overall Similarity: {details['overall_similarity']:.2%}")
        
        print("\nComponent Breakdown:")
        for name, info in details['components'].items():
            print(f"- {name}: {info['score']:.2%} ({info['description']})")
    except FileNotFoundError:
        print("Please update the image file paths in the example code")
    except Exception as e:
        print(f"Error: {str(e)}")