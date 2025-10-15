from ultralytics import YOLO

DATA_CONFIG_PATH = './conf.yaml'
model = YOLO('yolov8n.pt') 

results = model.train(
    data=DATA_CONFIG_PATH,
    epochs=50,
    imgsz=640,
    batch=8,
    device='cuda',
    save=True,
    degrees=2.0,
    translate=0.05,
    scale=0.05,
    shear=1.0,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    fliplr=0.0,
    flipud=0.0,
    mosaic=1.0,
    mixup=0.1
)

print("[INFO] Entraînement terminé.")