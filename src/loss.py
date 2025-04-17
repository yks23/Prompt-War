import torch
from transformers import CLIPProcessor, CLIPModel
from scipy.spatial.distance import cosine

# Load pre-trained CLIP model and processor
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

def get_clip_embedding(img):
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    return features.squeeze().numpy()
def get_string_embedding(text):
    inputs = processor(text=text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        features = model.get_text_features(**inputs)
    return features.squeeze().numpy()
def calculate_loss_with_image(img1, img2):
    embedding1 = get_clip_embedding(img1)
    embedding2 = get_clip_embedding(img2)
    loss = 1 - cosine(embedding1, embedding2)
    return loss
def calculate_loss_with_string(text, img):
    embedding1 = get_string_embedding(text)
    embedding2 = get_clip_embedding(img)
    loss = 1 - cosine(embedding1, embedding2)
    return loss

