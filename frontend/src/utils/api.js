import axios from 'axios';

// const API_URL = process.env.REACT_APP_API_URL || '';
const API_URL = 'http://localhost:8000';

export const processShootingAnalysis = async (file, sigma) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sigma', sigma);

    try {
      const response = await axios.post(`${API_URL}/api/shootinganalysis/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
    });
    console.log('shootinganalysis 응답:', response.data)
    return response.data;
  } catch (error) {
    let message = "두유 분석 중 오류가 발생했습니다.";
    if (error.response?.data?.detail) {
      message = error.response.data.detail;
      
    }
    if (message.includes("조도를 조정하세요")) {
      message = message.replace(
        "조도를 조정하세요",
        "<strong style='color:red'>조도를 조정하세요</strong>"
      );
    }
    throw new Error(message);
  }
}; 
