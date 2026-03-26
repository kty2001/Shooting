import axios from 'axios';

// const API_URL = process.env.REACT_APP_API_URL || '';
const API_URL = 'http://localhost:8000';

export const getUsers = async () => {
  try {
    const response = await axios.get(
      `${API_URL}/api/shootinganalysis/users`
    );
    return response.data;
  } catch (error) {
    let message = "유저 목록을 불러오는 중 오류가 발생했습니다.";
    if (error.response?.data?.detail) {
      message = error.response.data.detail;
    }
    throw new Error(message);
  }
};

export const getShootingSessions = async (userId = null) => {
  try {
    const response = await axios.get(
      `${API_URL}/api/shootinganalysis/sessions`,
      { params: userId ? { user_id: userId } : {} }
    );

    // response.data === string[]
    return response.data;

  } catch (error) {
    let message = "세션 목록을 불러오는 중 오류가 발생했습니다.";

    if (error.response?.data?.detail) {
      message = error.response.data.detail;
    }

    throw new Error(message);
  }
};

export const processShootingAnalysis = async (gameId) => {
  try {
    const response = await axios.get(
      `${API_URL}/api/shootinganalysis/process`,
      {
        params: {
          game_id: gameId,
        },
      }
    );

    return response.data;

  } catch (error) {
    let message = "탄착 분석 중 오류가 발생했습니다.";

    if (error.response?.data?.detail) {
      message = error.response.data.detail;
    }

    throw new Error(message);
  }
};