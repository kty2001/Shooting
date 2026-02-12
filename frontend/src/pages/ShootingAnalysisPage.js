import React, { useEffect, useState } from 'react';
import { getShootingSessions, getShootingAnalysisResult } from '../utils/api';
import FileDropzone from '../components/FileDropzone';
import AnalysisResultDisplay from '../components/AnalysisResultDisplay';
import { processShootingAnalysis } from '../utils/api';
import TakePicture from '../components/TakePicture';

const ShootingAnalysisPage = () => {
  const [sessionList, setSessionList] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sigma, setSigma] = useState(24);

  useEffect(() => {
    setLoading(true);

    getShootingSessions()
      .then(data => {
        setSessionList(data);
        if (data.length > 0) {
          setSelectedSession(data[0]);
        }
        console.log("len sessions:", data.length)
        console.log("sessions[0]:", data[0])
      })
      .catch(err => {
        setError(err.message)
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedSession) return;

    setLoading(true);
    setResult(null);

    processShootingAnalysis(selectedSession)
      .then(data => {
        setResult(data)
        console.log("analysis result:", data);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));

  }, [selectedSession]);

  if (error) {
    return <div className="text-center text-red-500">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6 font-sans">
      <div className="p-8">
        <div className="flex items-center gap-4 mb-20">
          <h2 className="text-2xl font-bold text-black">세션 선택</h2>
          <select
            className="border-2 border-black rounded-lg px-4 py-2 text-lg"
            value={selectedSession ?? ""}
            onChange={(e) => setSelectedSession(e.target.value)}
          >
            {sessionList.map((id) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
        </div>

        {loading && (
          <div className="text-center">분석 결과 불러오는 중...</div>
        )}
        {error && (
          <div className="text-center text-red-500">{error}</div>
        )}
        {!loading && !error && !result && (
          <div className="text-center">결과를 선택하세요</div>
        )}

        {result && (
          <>
            {/* 메인 분석 영역 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
              
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
                        boxShadow: `0 0 4px ${shot.color}`,
                        zIndex: 10,
                      }}
                    />
                  ))}

                  {/* COI 표시 (X 마커) */}
                  {result && (
                    <div
                      className="absolute text-red-500 font-bold text-xl select-none"
                      style={{
                        left: `${result.coi[0] * 256}px`,
                        top: `${result.coi[1] * 256}px`,
                        transform: "translate(-50%, -50%)",
                        zIndex: 20,
                      }}
                    >
                      ✕
                    </div>
                  )}
                </div>

                {/* Result Box */}
                <div className="relative border-2 border-black rounded-2xl p-6 w-full pt-14">
                  {result && (
                    <>
                      <h3 className="text-2xl font-bold text-black absolute top-3 left-5">
                        Result Box
                      </h3>
                      <div className="flex flex-col justify-center items-center text-center h-full">
                        <p>
                          COI: ({result.coi[0].toFixed(2)}, {result.coi[1].toFixed(2)}) /
                          TTF: {result.ttf.toFixed(2)}
                        </p>
                        <p>
                          MR: {result.mean_radius.toFixed(3)} /
                          STD: ({result.std[0].toFixed(3)}, {result.std[1].toFixed(3)})
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* 오른쪽 영역: 분석 및 피드백 */}
              <div className="flex flex-col gap-6 h-full">
                <div className="border-2 border-black rounded-2xl p-6 flex-1">
                  {/* Error Analysis Box */}
                  {result && (
                    <>
                      <h3 className="text-2xl font-bold mb-3 text-black">
                        Error Analysis Box
                      </h3>
                      <p className="text-gray-700 leading-relaxed">
                        주요 오류는{" "}
                        <span className="font-bold">
                          {result.major_error[0].major_error_name}
                        </span>
                        입니다.
                        (신뢰도: {(result.major_error[0].confidence * 100).toFixed(0)}%)<br />
                        {result.analysis_text}
                      </p>
                    </>
                  )}
                </div>

                {/* Feedback Box */}
                <div className="border-2 border-black rounded-2xl p-6 flex-1">
                  {result && (
                    <>
                      <h3 className="text-2xl font-bold mb-3 text-black">
                        Feedback Box
                      </h3>
                      <p className="text-gray-700 leading-relaxed">
                        {/* 추천 드릴:{" "}
                        <span className="font-bold"> */}
                          {result.recommend_text}
                        {/* </span> */}
                      </p>
                    </>
                  )}
                </div>
              </div>

            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ShootingAnalysisPage;