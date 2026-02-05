import os
import sys
import tempfile
import numpy as np
# import onnxruntime as ort
from PIL import Image
from pathlib import Path
import uuid
import matplotlib.pyplot as plt
from scipy import signal as scipy_signal


# class THzOnnxPredictor:
#     def __init__(
#         self,
#         model_path: str,
#         providers: list[str] = ["CPUExecutionProvider"],
#     ) -> None:
#         self.ort_session = ort.InferenceSession(model_path, providers=providers)

#     def predict(self, input_data):
#         input_name = self.ort_session.get_inputs()[0].name
#         ort_outs = self.ort_session.run(None, {input_name: input_data})[0]
#         return ort_outs


# class ImageProcessor:
#     def __init__(self, model_path: str):
#         self.model = THzOnnxPredictor(model_path)
#         self.colormap_name = "viridis"
        
#     def save_image(self, image_array, filename):
#         # """컬러맵을 적용하여 이미지 저장"""
#         # cm = plt.get_cmap(self.colormap_name)
#         # image_array = cm(image_array)
#         # image_array = (image_array * 255).astype(np.uint8)
        
#         # # RGBA to RGB
#         # if image_array.shape[-1] == 4:
#         #     image_array = image_array[:, :, :3]
            
#         img = Image.fromarray(image_array)
#         img.save(filename)
#         return filename
    
#     def calculate_sharpness(self, image_array):
#         """이미지 선명도 계산"""
#         gy, gx = np.gradient(image_array)
#         g_norm = np.sqrt(gx**2 + gy**2)
#         sharpness = np.round(np.average(g_norm), 2)
#         return float(sharpness)
    
#     def calculate_noise_level(self, image_array):
#         """이미지 노이즈 레벨 계산"""
#         # 간단한 노이즈 레벨 추정 (표준편차 기반)
#         return float(np.std(image_array))


# # 모델 경로 설정 (PyInstaller 패키징 고려)
# def get_model_path(model_name: str) -> str:
#     if getattr(sys, 'frozen', False):
#         # PyInstaller로 패키징된 경우
#         base_dir = Path(sys._MEIPASS)
#         return str(base_dir / "models" / model_name)
#     else:
#         # 일반 실행의 경우
#         base_dir = Path(__file__).parent.parent.parent
#         return str(base_dir / "models" / model_name)


# 파일 저장 경로 생성
def get_save_path(directory: str, extension: str) -> str:
    filename = f"{uuid.uuid4()}.{extension}"
    save_dir = Path(tempfile.gettempdir()) / "shooting_ai_system" / directory
    save_dir.mkdir(parents=True, exist_ok=True)
    return str(save_dir / filename) 