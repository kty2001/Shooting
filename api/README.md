# API

## 설치 및 실행

### 설치
현재 디렉토리에서 아래 코드 실행
```bash
# 가상 환경 생성
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 실행

```bash
python run.py
```

### 빌드
```bash
python build_exe.py
```

## LLM

### python-dotenv 이용한 환경변수 사용
Azure OpenAI 사용
현재 디렉토리에 ```.env``` 생성

```bash
#.env
AZURE_OPENAI_ENDPOINT=YOUR_API_ENDPOINT
AZURE_OPENAI_API_KEY=YOUR_API_KEY
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini (예시)
```
