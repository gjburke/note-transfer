from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from peft import PeftModel
import cv2
import torch
from anytree import Node, PreOrderIter
from PIL import Image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_text_recognition(base_model_name, lora_path):
    processor = TrOCRProcessor.from_pretrained(base_model_name)
    base_model = VisionEncoderDecoderModel.from_pretrained(base_model_name)

    model = PeftModel.from_pretrained(base_model, lora_path)
    model = model.merge_and_unload()

    model.to(DEVICE)
    model.eval()

    return model, processor

def is_text(node):
    return node.cls_id == 3

def get_text_prediction(image, model, processor):
    pil_image = Image.fromarray(image).convert("RGB")

    inputs = processor(images=pil_image, return_tensors="pt")
    pixel_values = inputs.pixel_values.to(DEVICE)

    with torch.no_grad():
        generated_ids = model.generate(
            pixel_values,
            max_length=64,
            num_beams=1,
            #repetition_penality=1.2,
            #no_repeat_ngram_size=3,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id
        )

    pred_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return pred_text.strip()

def detect_text(root, model, processor):
    print("Detecting text")
    for node in PreOrderIter(root):
        if is_text(node):
            print(".", end='', flush=True)
            cv2_img = node.img
            text = get_text_prediction(cv2_img, model, processor)
            node.text = text