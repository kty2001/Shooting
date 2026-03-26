import pickle
from pathlib import Path

import pandas as pd
import numpy as np
import sklearn
import sklearn.multioutput
import sklearn.ensemble
from fastapi import HTTPException

from app.models.schemas import MajorError

class ShootingInference:
    def __init__(self, model_path: str, feature_path: str):
        """
        모델과 피처 리스트를 로드합니다.
        """
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(feature_path, 'rb') as f:
                self.feature_cols = pickle.load(f)
            
            # 모델 학습 시 사용된 라벨 순서 (통합 버전)
            self.label_cols = [
                'label_jerking', 'label_heeling', 'label_thumbing_too_much_finger', 
                'label_too_little_finger', 'label_lobstering'
            ]
            
            # 사용자에게 보여줄 한글 매핑 테이블
            self.label_map = {
                'label_jerking': '급격한 방아쇠 당김(Jerking)',
                'label_heeling': '손바닥 밀어올림(Heeling)',
                'label_thumbing_too_much_finger': '엄지 압력/방아쇠 손가락 불량',
                'label_too_little_finger': '검지 끝 사용 불량',
                'label_lobstering': '그립 과도 압력(Lobstering)'
            }
            print(f"모델 로드 완료: {model_path}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"모델 오류 발생: {str(e)}")

    def predict(self, shooting_result, coi):
        """
        입력된 10발 데이터를 바탕으로 오류 확률과 상위 1개 오류를 반환합니다.
        """
        # 1. 모델 입력 규격(Wide Format)으로 데이터 재구성
        input_data = {}
        
        # 10발 데이터 매핑
        for i, shot in enumerate(shooting_result):
            n = i + 1
            input_data[f'point_x_{n}'] = shot.pointX
            input_data[f'point_y_{n}'] = shot.pointY

        # 통계 지표 매핑
        input_data['coi_x'] = coi[0]
        input_data['coi_y'] = coi[1]

        # 2. DataFrame 생성 및 학습 시 피처 순서와 동일하게 정렬
        X_input = pd.DataFrame([input_data])
        X_input = X_input[self.feature_cols] # 매우 중요: 컬럼 순서 강제 일치
        
        # 3. 확률 예측 (predict_proba)
        # MultiOutputClassifier는 리스트 안에 라벨별로 [정상확률, 오류확률] 배열을 반환함
        y_proba = self.model.predict_proba(X_input)
        
        error_probabilities = {}
        major_errors = []
        
        for i, label in enumerate(self.label_cols):
            confidence = float(y_proba[i][0][1])
            kor_name = self.label_map.get(label, label)
            
            error_probabilities[kor_name] = round(confidence, 4)
            
            major_errors.append(
                MajorError(
                major_error_name=kor_name,
                confidence=confidence,
            ))
            
        major_errors = [
            e for e in major_errors
            if e.confidence >= 0.7
        ]

        major_errors = sorted(
            major_errors,
            key=lambda x: x.confidence,
            reverse=True,
        )

        top_errors = major_errors[:1]

        return error_probabilities, top_errors