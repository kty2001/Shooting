import os
import time
import math

import io
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d
from fastapi import Request, APIRouter, UploadFile, File, HTTPException, Form

from app.models.schemas import AnalysisResponse, ErrorResponse
from app.utils.model_utils import get_save_path

router = APIRouter()

def rotate_image(gray_image):
    th1, th2 = 150, 180
    hough_th, hough_min, hough_max = 120, 300, 30

    blurred = cv2.GaussianBlur(gray_image, (5, 5), 1.5)
    edges = cv2.Canny(blurred, th1, th2, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/360, threshold=hough_th, minLineLength=hough_min, maxLineGap=hough_max)

    angles = []
    average_angle = 0
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            angle_rad = math.atan2((y2 - y1), (x2 - x1))
            angle_deg = math.degrees(angle_rad)
            angles.append(angle_deg)
            print(f"Line: ({x1}, {y1}) to ({x2}, {y2}), Angle: {angle_deg:.2f} degrees")
            
        if angles:
            average_angle = np.mean(angles)
            print(f"Average angle: {average_angle:.2f} degrees")
    else:
        print("No lines detected")

    (h, w) = gray_image.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, average_angle, 1.0)
    rotated_img = cv2.warpAffine(gray_image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    
    return average_angle, rotated_img

def fixed_edges_line(img):
    results = {'top': 431, 'bottom': 916, 'left': 400, 'right': 1382}

    cropped_image = img[results['top']:results['bottom'], results['left']:results['right']]
    print(results)
    return results, cropped_image

def find_edges_line(img, hor_threshold, ver_threshold):
    h, w = img.shape
    center_y, center_x = h // 2, w // 2
    results = {}

    # 상단에서 아래
    for y in range(int(center_y*1.5)):
        if np.sum(img[y, :]) > hor_threshold:
            results['top'] = y
            break
    else: results['top'] = 0

    # 하단에서 위
    for y in range(h - 1, int(center_y*0.5), -1):
        if np.sum(img[y, :]) > hor_threshold:
            results['bottom'] = y
            break
    else: results['bottom'] = h - 1

    # 왼쪽에서 오른쪽
    for x in range(int(center_x*1.5)):
        if np.sum(img[:, x]) > ver_threshold:
            results['left'] = x
            break
    else: results['left'] = 0

    # 오른쪽에서 왼쪽
    for x in range(w - 1, int(center_x*0.5), -1):
        if np.sum(img[:, x]) > ver_threshold:
            results['right'] = x
            break
    else: results['right'] = w - 1

    cropped_image = img[results['top']:results['bottom'], results['left']:results['right']]
    print(results)
    return results, cropped_image

def find_edges_max(img, pixel_threshold, hor_threshold, ver_threshold):
    h, w = img.shape
    center_y, center_x = h // 2, w // 2
    results = {}

    # 상단에서 아래
    for y in range(int(center_y*1.5)):
        if np.sum(img[y, :]) > hor_threshold:
            results['top'] = y
            break
    else: results['top'] = 0

    # 하단에서 위
    for y in range(h - 1, int(center_y*0.5), -1):
        if np.sum(img[y, :]) > hor_threshold:
            results['bottom'] = y
            break
    else: results['bottom'] = h - 1

    # 왼쪽에서 오른쪽
    for x in range(int(center_x*1.5)):
        if np.max(img[:, x]) > pixel_threshold and np.sum(img[:, x]) > ver_threshold:
            results['left'] = x
            break
    else: results['left'] = 0

    # 오른쪽에서 왼쪽
    for x in range(w - 1, int(center_x*0.5), -1):
        if np.max(img[:, x]) > pixel_threshold and np.sum(img[:, x]) > ver_threshold:
            results['right'] = x
            break
    else: results['right'] = w - 1

    cropped_image = img[results['top']:results['bottom'], results['left']:results['right']]
    print(results)
    return results, cropped_image

def crop_zero2fifth(image):
    rota_blur = cv2.GaussianBlur(image, (5, 5), 1.5)
    h, w = rota_blur.shape 
    print("left_crop_image shape:", rota_blur.shape)
    
    # cv2.line(left_crop_image, (0, int(h*0.32)), (w, int(h*0.32)), (255, 0, 0), 2)
    # cv2.imshow("Cropped Image", left_crop_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    pixel_data = rota_blur[int(h*0.32), :].astype(np.int16)
    pixel_deriv = np.diff(pixel_data, n=1)
    std_threshold = np.std(pixel_deriv) * 2

    marks = []
    idx = 0
    search_radius = 10

    while idx < len(pixel_deriv):
        if abs(pixel_deriv[idx]) > std_threshold:
            start = max(0, idx - search_radius)
            end = min(len(pixel_data), idx + search_radius)

            local_min_idx = np.argmin(pixel_data[start:end]) + start
            marks.append(local_min_idx)
            idx += 100
        else:
            idx += 1

    print("marks:", marks)
    
    # for j in marks:
    #     cv2.line(left_crop_image, (j, 0), (j, left_crop_image.shape[0]), (0, 0, 0), 2)
    # cv2.imshow("left cropped Image", left_crop_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return marks, (pixel_data, pixel_deriv, std_threshold)

def analyze_analyze(image, sigma=24):
    
    y_raw = image[image.shape[0] // 2, :]
    x = np.arange(len(y_raw))

    # best_sigma, scores, sigmas = select_optimal_sigma(y_raw)
    y_smooth = gaussian_filter1d(y_raw.astype(float), sigma=sigma)
    y_deriv = np.gradient(y_smooth)

    # blur_best_sigma, sigma_per_x, blur_sigmas = select_sigma_snr(y_raw)
    # print(" blur_best_sigma:", blur_best_sigma)
    gua_smooth = gaussian_filter1d(y_raw.astype(float), sigma=24)
    gua_deriv = np.gradient(gua_smooth)

    # ---------------------------------

    min_index = np.argmin(y_deriv)
    min_value = y_deriv[min_index]
    min_value2 = min_value / 2
    min_value2_index = min_index
    while min_value2_index > 0:
        if y_deriv[min_value2_index] >= min_value2:
            break
        min_value2_index -= 1
    width = min_index - min_value2_index
    print("min_index:", min_index, "/ min_value:", min_value)
    print("min_value2_index:", min_value2_index, "/ min_value2:", min_value2)
    print("width:", width)

    fig, axs = plt.subplots(2, 1, figsize=(8, 12))

    region = y_deriv[min_value2_index:min_index+width]
    peaks, _ = find_peaks(-region, prominence=abs(min_value)*0.2)
    print("peaks:", peaks)

    if len(peaks) > 1:
        raise HTTPException(status_code=400, detail="더블 딥(double dip) 현상 감지됨 - 측정 불가")

    # axs[0].plot(x, y_smooth, color='red', label='Raw', linewidth=2)
    # # axs[0].plot(x, blur_smooth, color='cyan', label='Raw', linewidth=2)
    # axs[0].axvline(x=min_index, color='green', linestyle='--', label='Threshold Line')
    # axs[0].axvline(x=min_value2_index, color='blue', linestyle='--', label='Boundary Line')
    # axs[0].axvline(x=min_index+width, color='blue', linestyle='--')
    # axs[0].legend()
    # axs[0].grid(True)
    # axs[0].set_xlim(0, image.shape[1])

    axs[0].plot(x, y_smooth, color='red', label='Pixel Smooth', linewidth=2)
    axs[0].axvline(x=min_index, color='green', linestyle='--', label='Threshold Line')
    axs[0].axvline(x=min_value2_index, color='blue', linestyle='--', label='Boundary Line')
    axs[0].axvline(x=min_index+width, color='blue', linestyle='--')
    axs[0].legend()
    axs[0].grid(True)
    axs[0].set_xlim(0, image.shape[1])

    axs[1].plot(x, y_deriv, color='red', label=f'1st Deriv Smooth {sigma}', linewidth=2)
    axs[1].axvline(x=min_index, color='green', linestyle='--', label='Threshold Line')
    axs[1].axvline(x=min_value2_index, color='blue', linestyle='--', label='Boundary Line')
    axs[1].axvline(x=min_index+width, color='blue', linestyle='--')
    axs[1].legend()
    axs[1].grid(True)
    axs[1].set_xlim(0, image.shape[1])

    # axs[2].plot(x, gua_deriv, color='red', label='1st Deriv Smooth', linewidth=2)
    # axs[2].axvline(x=min_index, color='green', linestyle='--', label='Threshold Line')
    # axs[2].axvline(x=min_value2_index, color='blue', linestyle='--', label='Boundary Line')
    # axs[2].axvline(x=min_index+width, color='blue', linestyle='--')
    # axs[2].legend()
    # axs[2].grid(True)
    # axs[2].set_xlim(0, image.shape[1])

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_pil = Image.open(buf).convert("RGB")
    img_np = np.array(img_pil)

    plt.close(fig)

    return img_np, width, min_index

def calibrate_marks(sorted_marks):
    values = np.array([v for v, _ in sorted_marks], dtype=np.float32)
    positions = np.array([p for _, p in sorted_marks], dtype=np.float32)
    # 1차 다항식 (직선 회귀)
    a, b = np.polyfit(positions, values, 1)
    return a, b

def get_interpolator(sorted_marks):
    if not sorted_marks:
        raise ValueError("sorted_marks is empty")
    
    values = [v for v, _ in sorted_marks]
    positions = [p for _, p in sorted_marks]

    if len(sorted_marks) < 2:
        raise ValueError("Not enough marks for interpolation")
    elif len(sorted_marks) == 2:
        kind = "linear"
    elif len(sorted_marks) == 3:
        kind = "quadratic"
    else:
        kind = "cubic"
    f = interp1d(positions, values, kind="linear", fill_value="extrapolate")
    return f

def get_prediction(marks, min_index):
    try:
        mark_dict = {}
        for mark in marks:
            if min_index - 20 <= mark <= min_index + 20:
                continue
            if 40 < mark < 70 and 0 not in mark_dict:
                mark_dict[0] = mark
            elif 140 < mark < 170 and 5 not in mark_dict:
                mark_dict[5] = mark
            elif 250 < mark < 280 and 10 not in mark_dict:
                mark_dict[10] = mark
            elif 370 < mark < 400 and 15 not in mark_dict:
                mark_dict[15] = mark

        sorted_marks = sorted(mark_dict.items(), key=lambda x: x[1])
        print("sorted_marks:", sorted_marks)

        f = get_interpolator(sorted_marks)
        prediction = round(float(f(min_index)), 1)
        return prediction, sorted_marks
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{len(sorted_marks)}개 눈금 감지 - 조도를 조정하세요")

def get_fixed_prediction(marks, min_index, img_w):
    try:
        sorted_marks = [
            [0, int(img_w*0.116)],
            [5, int(img_w*0.339)],
            [10, int(img_w*0.572)],
            [15, int(img_w*0.826)]
        ]

        f = get_interpolator(sorted_marks)
        prediction = round(float(f(min_index)), 1)
        return prediction, sorted_marks
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{len(sorted_marks)}개 눈금 감지 - 조도를 조정하세요")


@router.post("/process", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}})
async def process_image(request: Request, file: UploadFile = File(...), sigma: float = Form(24)):
    """
    이미지 처리 API (딥러닝 모델 제거, OpenCV 기반 처리)
    
    - **file**: 처리할 이미지 파일 (PNG, JPG, BMP 등)
    
    반환값:
    - 처리된 이미지 정보 및 URL
    """
    
    try:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            raise HTTPException(status_code=400, detail="지원되지 않는 파일 형식입니다. PNG, JPG, JPEG, BMP 파일만 허용됩니다.")
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        input_w, input_h = image.size
        if input_w < input_h:
            image = image.transpose(Image.ROTATE_270)
            input_w, input_h = image.size
        print("image size: ", image.size)

        input_filename = get_save_path("uploads", "jpg")
        image.save(input_filename)

        # rotated_input_pil = image.rotate(90, expand=True)
        # rotated_input_filename = get_save_path("uploads", "jpg")
        # rotated_input_pil.save(rotated_input_filename)

        img_array = np.fromfile(input_filename, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        img = cv2.resize(img.copy(), (1920, 1080))
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # average_angle, rotated_img = rotate_image(gray_image)
        # line_results, line_cropped_image = fixed_edges_line(gray_image)
        # line_results, line_cropped_image = find_edges_line(gray_image, 24000, 16000)
        line_results, line_cropped_image = find_edges_max(gray_image, 80, 24000, 8000)
        print("line cropped image shape:", line_cropped_image.shape)
        
        cropped_image = img[line_results['top']-20:line_results['bottom']+20, line_results['left']:line_results['right']]
        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        input_w, input_h = cropped_image.shape[1], cropped_image.shape[0]
        cropped_input_pil = Image.fromarray(cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE))
        cropped_input_filename = get_save_path("uploads", "jpg")
        cropped_input_pil.save(cropped_input_filename)

        left_crop_ratio = 0.24
        right_crop_ratio = 0.72
        analysis_image = line_cropped_image[:, int(line_cropped_image.shape[1]*left_crop_ratio):int(line_cropped_image.shape[1]*right_crop_ratio)]
        print("mark cropped image shape:", analysis_image.shape)

        # analysis_graph, width, min_index = analyze_image(analysis_image)
        analysis_graph, width, min_index = analyze_analyze(analysis_image, sigma)
        marks, pixel_values = crop_zero2fifth(analysis_image)
        # predict_value, sorted_marks = get_prediction(marks, min_index)
        predict_value, sorted_marks = get_fixed_prediction(marks, min_index, analysis_image.shape[1])
        analysis_image_color = cv2.cvtColor(analysis_image, cv2.COLOR_GRAY2BGR)
        cv2.line(analysis_image_color, (min_index, 0), (min_index, analysis_image_color.shape[0]), (0, 0, 255), 2)
        cv2.rectangle(
            analysis_image_color,
            (min_index-30, 2),
            (min_index+30, analysis_image_color.shape[0]-2),
            (255, 0, 0),
            3
        )
        print("predict_value:", predict_value)

        # for m in sorted_marks:
        #     cv2.line(analysis_image_color, (m[1], 0), (m[1], analysis_image_color.shape[0]), (0, 0, 0), 2)

        cropped_pil = Image.fromarray(cv2.rotate(analysis_image_color, cv2.ROTATE_90_COUNTERCLOCKWISE))
        output_pil = Image.fromarray(analysis_graph)
        
        cropped_filename = get_save_path("results", "jpg")
        cropped_pil.save(cropped_filename)
        output_filename = get_save_path("results", "jpg")
        output_pil.save(output_filename)

        # 절대 URL 생성
        base_url = str(request.base_url).rstrip("/")
        input_url = f"{base_url}/uploads/{os.path.basename(cropped_input_filename)}"
        cropped_output_url = f"{base_url}/results/{os.path.basename(cropped_filename)}"
        output_url = f"{base_url}/results/{os.path.basename(output_filename)}"

        return AnalysisResponse(
            input_width=input_w,
            input_height=input_h,
            output_width=cropped_pil.size[0],
            output_height=cropped_pil.size[1],
            input_metric=1,
            output_metric=1,
            average_angle=0,
            min_index=min_index,
            width=width,
            marks=marks,
            sorted_marks=sorted_marks,
            predict_value=predict_value,
            input_image_url=input_url,
            cropped_image_url=cropped_output_url,
            output_image_url=output_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"이미지 처리 중 오류가 발생했습니다: {str(e)}")