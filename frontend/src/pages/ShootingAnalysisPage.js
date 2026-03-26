import React, { useEffect, useState } from 'react';
import { getUsers, getShootingSessions, getShootingAnalysisResult } from '../utils/api';
import FileDropzone from '../components/FileDropzone';
import AnalysisResultDisplay from '../components/AnalysisResultDisplay';
import { processShootingAnalysis } from '../utils/api';
import TakePicture from '../components/TakePicture';

const ShootingAnalysisPage = () => {
  const [userList, setUserList] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [sessionList, setSessionList] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 최초 로드: 유저 목록
  useEffect(() => {
    setLoading(true);
    getUsers()
      .then(data => {
        setUserList(data);
        if (data.length > 0) setSelectedUser(data[0]);
      })
      .catch(err => {
        setError(err.message);
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, []);

  // 유저 선택 시: 해당 유저의 세션 목록 로드
  useEffect(() => {
    if (!selectedUser) return;

    setSessionList([]);
    setSelectedSession(null);
    setResult(null);
    setLoading(true);

    getShootingSessions(selectedUser)
      .then(data => {
        setSessionList(data);
        if (data.length > 0) setSelectedSession(data[0]);
        console.log(`sessions for ${selectedUser}:`, data.length);
      })
      .catch(err => {
        setError(err.message);
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, [selectedUser]);

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
    return <div className="text-center text-error p-lg">{error}</div>;
  }

  return (
    <div className="min-h-screen p-lg font-sans">
      <div className="p-md">
        {/* 선택 영역 */}
        <div className="flex items-center gap-md mb-xl flex-wrap">
          <label className="text-textSecondary text-sm font-medium">유저</label>
          <select
            className="bg-surface border border-border rounded-md px-md py-sm text-textPrimary text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            value={selectedUser ?? ""}
            onChange={(e) => setSelectedUser(e.target.value)}
          >
            {userList.map((id) => (
              <option key={id} value={id} className="bg-surface">{id}</option>
            ))}
          </select>

          <label className="text-textSecondary text-sm font-medium ml-md">세션</label>
          <select
            className="bg-surface border border-border rounded-md px-md py-sm text-textPrimary text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 disabled:opacity-40 disabled:cursor-not-allowed"
            value={selectedSession ?? ""}
            onChange={(e) => setSelectedSession(e.target.value)}
            disabled={sessionList.length === 0}
          >
            {sessionList.length === 0 && (
              <option value="" className="bg-surface">세션 없음</option>
            )}
            {sessionList.map((id) => (
              <option key={id} value={id} className="bg-surface">{id}</option>
            ))}
          </select>
        </div>

        {loading && (
          <div className="text-center text-textMuted py-xl">분석 결과 불러오는 중...</div>
        )}
        {!loading && !error && !result && (
          <div className="text-center text-textMuted py-xl">결과를 선택하세요</div>
        )}

        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg items-stretch">

            {/* 왼쪽 영역: 타겟 및 결과 수치 */}
            <div className="flex flex-col items-center gap-lg">
              {/* 타겟 시각화 */}
              <div className="relative w-80 h-80 border border-border rounded-full flex items-center justify-center">
                <div className="w-64 h-64 border border-border rounded-full flex items-center justify-center">
                  <div className="w-48 h-48 border border-border rounded-full flex items-center justify-center">
                    <div className="w-32 h-32 border border-border rounded-full flex items-center justify-center">
                      <div className="w-16 h-16 bg-surface-300 rounded-full"></div>
                    </div>
                  </div>
                </div>

                {/* 탄착군 */}
                {result.shooting_result && result.shooting_result.map((shot) => (
                  <div
                    key={shot.nth}
                    className="absolute flex items-center justify-center w-4 h-4 rounded-full"
                    style={{
                      left: `${shot.pointX * 320}px`,
                      top: `${shot.pointY * 320}px`,
                      backgroundColor: shot.color,
                      border: "1px solid rgba(255, 255, 255, 0.5)",
                      transform: "translate(-50%, -50%)",
                      boxShadow: `0 0 6px ${shot.color}`,
                      zIndex: shot.nth,
                    }}
                  >
                    <span style={{ fontSize: '9px', fontWeight: 'bold', color: '#fff', lineHeight: 1, textShadow: '0 0 2px rgba(0,0,0,0.8)' }}>
                      {shot.nth}
                    </span>
                  </div>
                ))}

                {/* COI 마커 */}
                {result.shooting_result && (
                  <div
                    className="absolute text-error font-bold text-xl select-none"
                    style={{
                      left: `${result.coi[0] * 320}px`,
                      top: `${result.coi[1] * 320}px`,
                      transform: "translate(-50%, -50%)",
                      zIndex: 20,
                    }}
                  >
                    ✕
                  </div>
                )}

                {/* 임계값 영역 */}
                {result.coi && result.threshold && (
                  <div
                    className="absolute rounded-full border border-dashed border-error pointer-events-none opacity-60"
                    style={{
                      width: `${result.threshold * 2 * 320}px`,
                      height: `${result.threshold * 2 * 320}px`,
                      left: `${result.coi[0] * 320}px`,
                      top: `${result.coi[1] * 320}px`,
                      transform: "translate(-50%, -50%)",
                      zIndex: 15,
                    }}
                  />
                )}
              </div>

              {/* Result Box */}
              <div className="bg-surface border border-border rounded-lg p-lg w-full">
                <div className="flex items-center justify-between mb-md">
                  <h3 className="text-textPrimary text-lg font-semibold">Result</h3>
                  <span className="text-xs font-semibold px-sm py-xs rounded-md bg-primary-700 text-primary-100 tracking-wide">
                    {result.skill_level}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-sm">
                  {[
                    { label: "COI X", value: result.coi[0].toFixed(3) },
                    { label: "COI Y", value: result.coi[1].toFixed(3) },
                    { label: "Mean Radius", value: result.mean_radius.toFixed(3) },
                    { label: "STD X", value: result.std[0].toFixed(3) },
                    { label: "STD Y", value: result.std[1].toFixed(3) },
                    { label: "Shots", value: result.shooting_result?.length ?? "-" },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-background-200 rounded-md p-sm text-center">
                      <p className="text-textMuted text-xs mb-xs">{label}</p>
                      <p className="text-primary-400 font-mono font-semibold text-sm">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 오른쪽 영역: 분석 및 피드백 */}
            <div className="flex flex-col gap-lg h-full">
              {/* Error Analysis Box */}
              <div className="bg-surface border border-border rounded-lg p-lg flex-1">
                <h3 className="text-textPrimary text-lg font-semibold mb-md">Error Analysis Box</h3>
                {result.shooting_result && result.shooting_result.length === 10 ? (
                  <div className="text-textSecondary leading-relaxed flex flex-col gap-xs">
                    {result.major_error && result.major_error.length > 0 ? (
                      result.major_error.map((err, idx) => (
                        <p key={idx}>
                          <span className="text-primary-400 font-bold">[{err.major_error_name}]</span>{" "}
                          <span className="text-textPrimary">{(err.confidence * 100).toFixed(0)}%</span>
                        </p>
                      ))
                    ) : (
                      <p className="text-textMuted">감지된 오류가 없습니다.</p>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-textMuted text-sm">
                    세션 분석에는 10발 사격 결과가 필요합니다.
                  </div>
                )}
              </div>

              {/* Feedback Box */}
              <div className="bg-surface border border-border rounded-lg p-lg flex-1">
                <h3 className="text-textPrimary text-lg font-semibold mb-md">Feedback Box</h3>
                {result.shooting_result && result.shooting_result.length === 10 ? (
                  <div className="text-textSecondary text-sm leading-relaxed flex flex-col gap-sm">
                    {result.analysis_text && result.analysis_text.split('\n').map((line, idx) => {
                      const match = line.match(/^(\[.+?\])\s*(.*)/);
                      return match ? (
                        <p key={idx}>
                          <span className="text-primary-400 font-bold">{match[1]}</span>{" "}
                          {match[2]}
                        </p>
                      ) : (
                        <p key={idx}>{line}</p>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-textMuted text-sm">
                    세션 분석에는 10발 사격 결과가 필요합니다.
                  </div>
                )}
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};

export default ShootingAnalysisPage;
