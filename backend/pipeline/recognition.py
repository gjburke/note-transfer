from transformers import pipeline
import cv2
from anytree import Node, PreOrderIter
from PIL import Image

def load_text_model():
    return pipeline("image-to-text", model="microsoft/trocr-base-handwritten")

def is_text(node):
    return node.cls_id == 3

def get_text_prediction(image, model):
    results = model(image)
    result = results[0]
    text = result["generated_text"]
    return text.strip()

def detect_text(root, model):
    print("Detecting text")
    for node in PreOrderIter(root):
        if is_text(node):
            print(".", end='', flush=True)
            cv2_img = node.img
            pil_img = Image.fromarray(cv2_img) 
            text = get_text_prediction(pil_img, model)
            node.text = text