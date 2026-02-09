import React, { useEffect, useState } from 'react';
import FileDropzone from '../components/FileDropzone';
import AnalysisResultDisplay from '../components/AnalysisResultDisplay';
import { processShootingAnalysis } from '../utils/api';
import TakePicture from '../components/TakePicture';

const ShootingAnalysisPage = () => {
  const [activeTab, setActiveTab] = useState("camera");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sigma, setSigma] = useState(24);

  useEffect(() => {
    fetch("http://localhost:4000/api/analysis")
      .then(res => res.json())
      .then(data => {
        console.log(data);
        setResult(data)
      })
      .catch(err => console.error(err));
  }, []);

  // const handleCapture = (imageDataUrl) => {
  //   console.log('Captured image data URL:', imageDataUrl.slice(0,50));
  //   fetch(imageDataUrl)
  //     .then(res => res.blob())
  //     .then(blob => {
  //       const file = new File([blob], "captured_image.png", { type: "image/png" });
  //       handleFileDrop(file);
  //     });
  // };

  // const handleFileDrop = async (file) => {
  //   setLoading(true);
  //   setError(null);
  //   setResult(null);

  //   try {
  //     const response = await processShootingAnalysis(file, sigma);
  //     setResult(response);
  //   } catch (err) {
  //     setError(err.message);
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  if (loading) {
    return <div className="text-center">분석 결과 불러오는 중...</div>;
  }

  if (!result) {
    return <div className="text-center text-red-500">데이터 없음</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6 font-sans">

      <div className="p-8">
        <h2 className="text-3xl font-bold mb-8 text-black">세션 분석</h2>

        {/* 메인 분석 영역 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 itmes-stretch">
          
          {/* 왼쪽 영역: 타겟 및 결과 수치 */}
          <div className="flex flex-col items-center">
            {/* 타겟 시각화 (AnalysisResultDisplay 내부에서 처리되거나 여기서 대체) */}
            <div className="relative w-64 h-64 border-2 border-black rounded-full flex items-center justify-center mb-6">
              <div className="w-48 h-48 border border-black rounded-full flex items-center justify-center">
                <div className="w-32 h-32 border border-black rounded-full flex items-center justify-center">
                  <div className="w-16 h-16 bg-black rounded-full"></div>
                </div>
              </div>
              {/* 예시 탄착군 (데이터가 있을 때 매핑) */}
              {result && result.shooting_result.map((shot) => (
                <div
                  key={shot.nth}
                  className="absolute w-2 h-2 rounded-full"
                  style={{
                    left: `${shot.pointX * 256}px`,
                    top: `${shot.pointY * 256}px`,
                    backgroundColor: shot.color,
                    transform: "translate(-50%, -50%)",
                    boxShadow: `0 0 6px ${shot.color}`
                  }}
                />
              ))}
            </div>

            {/* Result Box */}
            {result && (
              <>
                <p>
                  COI: ({result.coi[0].toFixed(2)}, {result.coi[1].toFixed(2)}) /
                  TTF: {result.ttf.toFixed(2)}
                </p>
                <p>
                  MR: {result.mean_radius.toFixed(3)} /
                  STD: ({result.std[0].toFixed(3)}, {result.std[1].toFixed(3)})
                </p>
              </>
            )}
          </div>

          {/* 오른쪽 영역: 분석 및 피드백 */}
          <div className="flex flex-col gap-6 h-full">
            <div className="border-2 border-black rounded-2xl p-6 flex-1">
              {/* Error Analysis Box */}
              {result && (
                <p className="text-gray-700 leading-relaxed">
                  주요 오류는{" "}
                  <span className="font-bold">
                    {result.major_error[0].error}
                  </span>
                  입니다.<br />
                  신뢰도: {(result.major_error[0].confidence * 100).toFixed(0)}%
                </p>
              )}
            </div>

            {/* Feedback Box */}
            <div className="border-2 border-black rounded-2xl p-6 flex-1">
              {result && (
                <p className="text-gray-700 leading-relaxed">
                  추천 드릴:{" "}
                  <span className="font-bold">
                    {result.recommended_drill}
                  </span>
                  <br />
                  그립 안정성과 손바닥 압력 분산을 중심으로 훈련하세요.
                </p>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ShootingAnalysisPage;