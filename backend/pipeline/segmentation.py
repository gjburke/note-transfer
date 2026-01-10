from ultralytics import YOLO
from ultralytics.utils.ops import xyxy2xywh, xywh2xyxy
import cv2
import numpy as np
from anytree import Node

def load_seg_model(path):
    return YOLO(path)

# Takes xywhr and standardizes it to -pi/4, pi/4 (instead of 0, pi/2)
def normalize_xywhr(xywhr):
    x_center, y_center, width, height, theta = xywhr.tolist()
    if theta > (1/4)*np.pi or theta < (-1/4)*np.pi:
        temp = width
        width = height
        height = temp
        theta -= np.sign(theta)*(np.pi/2)

    return np.array([x_center, y_center, width, height, theta])

# Takes image and crop vars, returns cropped image
def crop_from_obb(image, xywhr):
    xywhr = normalize_xywhr(xywhr)
    x_center, y_center, width, height, theta = xywhr.tolist()

    # Transformation for rotation, rotate image
    rotation_matrix = cv2.getRotationMatrix2D((x_center, y_center), np.degrees(theta), 1.0)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))

    # Crop the rotated image
    x_corner, y_corner = int(x_center - width/2), int(y_center - height/2)
    cropped_image = rotated_image[y_corner:y_corner+int(height), x_corner:x_corner+int(width)]

    return cropped_image

# Takes image and normal bounding box (no rotation) bounds (top left, bottom right points)
# Returns the cropped image
def crop_from_bb(image, xyxy):
    x1, y1, x2, y2 = xyxy.tolist()
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    return image[y1:y2+1, x1:x2+1]

def normalize_box(xywhr):
    x, y, w, h, r = xywhr
    if r > np.pi/4:
        w, h = h, w
        r -= np.pi/2
    return x, y, w, h, r

def xywhr2corner(xywhr):
    x, y, w, h, r = xywhr[0], xywhr[1], xywhr[2], xywhr[3], xywhr[4]

    x = x - 0.5*w*np.cos(r) + 0.5*h*np.sin(r)
    y = y - 0.5*w*np.sin(r) - 0.5*h*np.cos(r)

    return x, y

def get_page_segmentations(image, section_model, line_model):
    segmentations = []
    sid = 0

    section_result = section_model.predict(image, iou=0.5, agnostic_nms=True)
    if section_result is None or len(section_result) == 0:
        print("No result!")
    section_result = section_result[0]
    if section_result.obb is None:
        print("No OBB!")

    for class_id, xywhr in sorted(list(zip(section_result.obb.cls, section_result.obb.xywhr)), key=lambda res: res[1][1]): # Iterate by descending height
        # First step is the section
        cropped_image = crop_from_obb(image, xywhr)

        if cropped_image.shape[0] == 0 or cropped_image.shape[1] == 0:
            print(f"Incompatible crop: {cropped_image.shape}")
            continue

        sec_class_name = section_result.names[int(class_id)]
        xywhr = normalize_box(xywhr.cpu().tolist())
        x, y = xywhr2corner(xywhr)
        sec_node = Node(
            sec_class_name,
            id=sid,
            is_section=True,
            cls_id=int(class_id.cpu()),
            x=x,
            y=y,
            x_c=xywhr[0],
            y_c=xywhr[1],
            w=xywhr[2],
            h=xywhr[3],
            r=xywhr[4]
        )
        segmentations.append(sec_node)
        sid += 1

        # Then segment by line after each section
        line_result = line_model.predict(cropped_image, iou=0.4, agnostic_nms=True)

        if line_result is None or len(line_result) == 0:
            print("No line result!")
        line_result = line_result[0]
        if line_result.boxes is None:
            print("No boxes!")

        for class_id, xyxy in sorted(list(zip(line_result.boxes.cls, line_result.boxes.xyxy)), key=lambda x: x[1][1]): # Sorted by height
            cropped_line = crop_from_bb(cropped_image, xyxy)
            if cropped_line.shape[0] == 0 or cropped_line.shape[1] == 0:
                print(f"Incompatible crop: {cropped_line.shape}")
                continue
            
            line_class_name = line_result.names[int(class_id)]
            xywhr = xyxy2xywh(xyxy).cpu().tolist()
            xywhr.append(0)
            xywhr = normalize_box(xywhr)
            x, y = xywhr2corner(xywhr)
            line_node = Node(
                line_class_name,
                id=sid,
                is_section=False,
                cls_id=int(class_id.cpu()),
                img=cropped_line,
                x=x,
                y=y,
                x_c=xywhr[0],
                y_c=xywhr[1],
                w=xywhr[2],
                h=xywhr[3],
                r=xywhr[3]
            )
            segmentations.append(line_node)
            sid += 1

    return segmentations 