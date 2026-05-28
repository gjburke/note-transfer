from transformers import TrOCRProcessor, VisionEncoderDecoderModel, GenerationConfig
from peft import PeftModel
import cv2
import torch
from anytree import Node, PreOrderIter
from PIL import Image
import difflib
import numpy as np

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_text_recognition(base_model_name, lora_path):
    processor = TrOCRProcessor.from_pretrained(base_model_name)
    model = VisionEncoderDecoderModel.from_pretrained(base_model_name)

    # model = PeftModel.from_pretrained(base_model, lora_path)
    # model = model.merge_and_unload()

    model.generation_config = GenerationConfig(
        max_new_tokens=64,
        num_beams=2,                 
        length_penalty=1.2,
        repetition_penalty=1.2,
        no_repeat_ngram_size=3,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        decoder_start_token_id=processor.tokenizer.cls_token_id # Explicitly guide the decoder's first step
    )

    model.to(DEVICE)
    model.eval()

    return model, processor

def is_text(node):
    return node.cls_id == 3

# Preprocessing

def find_best_single_cut(vertical_projection, start_x, end_x, sigma_factor=0.7):
    """
    Scans a localized window frame and uses a Standard Deviation baseline
    to dynamically isolate the true structural valleys of the text layout.
    """
    start_x, end_x = max(0, start_x), min(len(vertical_projection), end_x)
    if start_x >= end_x:
        return start_x, True

    slice_zone = vertical_projection[start_x:end_x]
    
    # Statistical Distribution Profiling
    local_mean = np.mean(slice_zone)
    local_std = np.std(slice_zone)
    local_threshold = local_mean - (sigma_factor * local_std)
    
    # Map slice arrays to binary space (1 for true space, 0 for ink zones)
    is_space = (slice_zone <= local_threshold).astype(np.int8)
    
    # Run-length boundary parsing
    bounded = np.concatenate(([0], is_space, [0]))
    changes = np.diff(bounded)
    starts = np.where(changes == 1)[0] + start_x
    ends = np.where(changes == -1)[0] + start_x

    if len(starts) == 0:
        return int(start_x + np.argmin(slice_zone)), True

    widths = ends - starts
    
    # Filter out micro-tears under 5px (protects loose loops like 'y')
    valid_mask = widths >= 5 
    
    if not np.any(valid_mask):
        return int(start_x + np.argmin(slice_zone)), True
        
    v_starts = starts[valid_mask]
    v_ends = ends[valid_mask]
    v_widths = widths[valid_mask]
    
    # Calculate geometric centers and center-proximity metrics
    v_centers = (v_starts + v_ends) / 2.0
    ideal_center = (start_x + end_x) / 2.0
    v_distances = np.abs(v_centers - ideal_center)
    
    # Structured context tie-breaker: maximize width first, minimize center distance second
    best_idx = sorted(
        range(len(v_starts)), 
        key=lambda idx: (-v_widths[idx], v_distances[idx])
    )[0]
    
    return int(v_centers[best_idx]), False


def balance_and_plan_cuts(image, target_ratio=12, margin=0.25):
    """
    SYSTEM REBOOT: Scales purely by Target Aspect Ratio (Width / Height).
    Determines the number of chunks needed so that each resulting sub-slice 
    closely matches the requested aspect ratio format.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    vertical_projection = np.sum(thresh, axis=0)
    
    img_height, img_width = gray.shape
    
    # Calculate current raw aspect ratio
    current_ratio = img_width / img_height
    
    # Dynamically determine chunk count based on the aspect ratio threshold
    num_chunks = int(np.ceil(current_ratio / target_ratio))
    
    if num_chunks <= 1:
        return [0, img_width]
        
    ideal_step = img_width / num_chunks
    cut_points = [0]
    dynamic_margin = int(ideal_step * margin)

    for i in range(1, num_chunks):
        ideal_x = int(i * ideal_step)
        
        computed_cut, is_blocked = find_best_single_cut(
            vertical_projection, 
            ideal_x - dynamic_margin, 
            ideal_x + dynamic_margin, 
            sigma_factor=0.7
        )
        
        cut_x = ideal_x if is_blocked else computed_cut
        cut_points.append(cut_x)
        
    cut_points.append(img_width)
    return sorted(list(set(cut_points)))


def extract_chunks_from_plan(image, cut_points):
    """ Slices an image matrix horizontally based on verified coordinate plans. """
    return [image[:, cut_points[i]:cut_points[i+1]] for i in range(len(cut_points) - 1)]

# Inference

def merge_text_chunks(text_chunks):
    """
    Takes a list of text strings extracted from sequential image chunks 
    and merges them seamlessly by deduplicating overlapping words at the seams.
    """
    if not text_chunks:
        return ""
        
    # Start with the text from the absolute first chunk
    combined_text = text_chunks[0].strip()
    
    for next_chunk in text_chunks[1:]:
        next_chunk = next_chunk.strip()
        if not next_chunk:
            continue
            
        words_combined = combined_text.split()
        words_next = next_chunk.split()
        
        # Find the longest matching sequence of words between the end of 
        # our accumulated text and the start of the incoming chunk
        matcher = difflib.SequenceMatcher(None, words_combined, words_next)
        match = matcher.find_longest_match(0, len(words_combined), 0, len(words_next))
        
        # Verify that the match happens at the boundary junction
        # (The match must end at the last word of combined_text OR start at the first word of words_next)
        if match.size > 0 and (match.a + match.size == len(words_combined) or match.b == 0):
            # Slice and merge at the overlapping juncture
            merged_words = words_combined[:match.a] + words_next[match.b:]
            combined_text = " ".join(merged_words)
        else:
            # Fallback if no clean linguistic overlap is detected
            combined_text += " " + next_chunk

    return combined_text

def get_text_prediction(image, model, processor):
    pil_image = Image.fromarray(image).convert("RGB")

    inputs = processor(images=pil_image, return_tensors="pt")
    pixel_values = inputs.pixel_values.to(DEVICE)

    with torch.no_grad():
        generated_ids = model.generate(pixel_values)

    pred_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return pred_text.strip()

def get_line_prediction(line, model, processor):
    cut_points = balance_and_plan_cuts(line)
    line_chunks = extract_chunks_from_plan(line, cut_points)

    text_chunks = [
        get_text_prediction(chunk, model, processor)
        for chunk in line_chunks
    ]

    output_text = merge_text_chunks(text_chunks)
    return output_text

def detect_text(root, model, processor):
    print("Detecting text")
    for node in PreOrderIter(root):
        if is_text(node):
            print(".", end='', flush=True)
            cv2_img = node.img
            text = get_line_prediction(cv2_img, model, processor)
            node.text = text