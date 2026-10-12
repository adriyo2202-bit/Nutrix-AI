from ultralytics import YOLO

print("Downloading YOLOv8n...")
model = YOLO('yolov8n.pt')

print("Exporting to CoreML (INT8) for Apple Silicon...")
model.export(format='coreml', int8=True, nms=True)

print("Export complete!")
