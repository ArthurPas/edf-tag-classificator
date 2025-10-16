
import cv2
from ultralytics import YOLO
import os
import pytesseract
import cv2
import re
model_path = 'tag_cropper/best.pt'
folder_path = 'test_original'
def crop_tag(image_path, model_path, output_dir, file_name):
    model = YOLO(model_path)
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found")
    results = model(image)
    os.makedirs(output_dir, exist_ok=True)
    i=0
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())  # Get coordinates
            padding = 20  # Define padding
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.shape[1], x2 + padding)
            y2 = min(image.shape[0], y2 + padding)
            cropped_image = image[y1:y2, x1:x2]  # Crop the image
            output_path = os.path.join(output_dir, f"{file_name}_{i}")
            cv2.imwrite(f"{output_path}.png", cropped_image) # Save the cropped image
            print(f"Cropped image saved to {output_path}")
            i += 1

def crop_folder(model_path, folder_path, output_dir='output'):
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for img_path in image_files:
        try:
            crop_tag(img_path, model_path, output_dir=output_dir, file_name=os.path.splitext(os.path.basename(img_path))[0])
        except ValueError as e:
            print(e)

def do_ocr(matched_tags, regex_pattern, folder_path):
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for img_path in image_files:
        text = pytesseract.image_to_string(img_path)
        clean_text = re.sub(r'[^a-zA-Z0-9_]', '', text).upper()
        match = re.search(regex_pattern, clean_text)
        if match:
            matched_tags.append((match.group(), img_path))
        else:
            not_matched_tags.append((clean_text, img_path))
def report(matched_tags, not_matched_tags):
    print("Report:")
    total_tags = len(matched_tags) + len(not_matched_tags)
    if total_tags > 0:
        success_rate = (len(matched_tags) / total_tags) * 100
        failure_rate = (len(not_matched_tags) / total_tags) * 100
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Failure Rate: {failure_rate:.2f}%")
    else:
        print("No tags processed.")

    print("\nExamples of Matched Tags:")
    for tag, path in matched_tags[:5]:
        print(f"Tag: {tag}, Image Path: {path}")

    print("\nExamples of Failed Tags:")
    for text, path in not_matched_tags:
        print(f"Extracted Text: {text}, Image Path: {path}")
def enlarge_image(input_path, output_path, scale=2):
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError("Image not found")
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    enlarged_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(output_path, enlarged_image)
    print(f"Enlarged image saved to {output_path}")

def enlarge_folder(input_dir, output_dir, scale=5):
    os.makedirs(output_dir, exist_ok=True)
    image_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for img_path in image_files:
        file_name = os.path.basename(img_path)
        output_path = os.path.join(output_dir, file_name)
        try:
            enlarge_image(img_path, output_path, scale)
        except ValueError as e:
            print(e)

matched_tags = []
not_matched_tags = []
folder_path = 'test_original_cropped/enlarged'
regex_pattern = r"([A-Z0-9]{9})"
# crop_folder(model_path, folder_path, "test_original_cropped")
# enlarge_folder("test_original", "test_original/enlarged")
# do_ocr(matched_tags, regex_pattern, folder_path)
report(matched_tags, not_matched_tags)
# ['0S2POMPIG', '1DVS305LP', '4RPE101VE', '1RPE069SN', '1RRIO71MI', '7RPE105WE', '1RIS029ND', '1RPE100VE', '7RRI023PO', '1RRI021PU', '82TE536WM', '4EVR031VD', '1RRI250VN', '4EVR031KD', '4RRI005WN', '1RIS344VH', '1EVR141YT', '1EVR041RF', '6POOGNGEX', '1EVR234VN', '1RIS672DI', '1DVS305LP', '4EVR031VD', '1EVR041RF', '2UIERISIS', '7RPE105WE', '1KRG102CO', '1EAS073YD', '4EVR031KD', '1EAS073VN', '4RRI001VN', '1RPE091YP', '1EAS073VN', '4RRI001VN']
# Report:
# Success Rate: 20.42%
# Failure Rate: 79.58%

# Examples of Matched Tags:
# Tag: 1SRESERYP, Image Path: output/8059cda3-20251009_100356_0.png.png
# Tag: 1DVS305LP, Image Path: output/e0ee4f56-20251009_102419_2.png.png
# Tag: 549LPPRES, Image Path: output/0b8ec27d-20251009_103115_7.png.png
# Tag: 1RPE069SN, Image Path: output/f00d5ad3-20251009_100259_0.png.png
# Tag: 1RIS029ND, Image Path: output/904ab53d-20251009_100453_0.png.png

# Examples of Failed Tags:
# Extracted Text: , Image Path: output/67ee1bdb-20251009_101252_0.png.png
# Extracted Text: TRIS836yyspSOLEMENT548pI0S2PomPiga, Image Path: output/0b8ec27d-20251009_103115_0.png.png
# Extracted Text: , Image Path: output/a32a3455-20251009_103244_5.png.png
# Extracted Text: , Image Path: output/8ecc60f3-20251009_100349_2.png.png
# Extracted Text: 4RPE101VepotDEvISU_, Image Path: output/1a69b7f6-20251009_100841_1.png.png