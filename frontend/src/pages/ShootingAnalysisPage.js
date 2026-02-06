import React, { useState } from 'react';
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

  const handleCapture = (imageDataUrl) => {
    console.log('Captured image data URL:', imageDataUrl.slice(0,50));
    fetch(imageDataUrl)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], "captured_image.png", { type: "image/png" });
        handleFileDrop(file);
      });
  };

  const handleFileDrop = async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await processShootingAnalysis(file, sigma);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // return (
  //   <div className="p-lg">

  //     <div className="flex gap-lg flex-wrap">
  //       <div className="flex-[1] min-w-[300px]">
  //         <div className="flex border-b border-border mt-md">
  //           <button
  //             className={`flex-1 px-4 py-2 text-lg ${
  //               activeTab === "camera"
  //                 ? "bg-primary text-white font-semibold"
  //                 : "text-textSecondary hover:bg-muted"
  //             }`}
  //             onClick={() => setActiveTab("camera")}
  //           >
  //             카메라 촬영
  //           </button>
  //           <button
  //             className={`flex-1 px-4 py-2 text-lg ${
  //               activeTab === "file"
  //                 ? "bg-primary text-white font-semibold"
  //                 : "text-textSecondary hover:bg-muted"
  //             }`}
  //             onClick={() => setActiveTab("file")}
  //           >
  //             파일 업로드
  //           </button>
  //         </div>

  //         <div className="p-md">
  //           {activeTab === "camera" && <TakePicture onCapture={handleCapture} />}
  //           {activeTab === "file" && (
  //             <div className="min-h-[400px] flex items-center justify-center">
  //               <FileDropzone
  //                 onFileDrop={handleFileDrop}
  //                 acceptedFileTypes={{ "image/*": [".png", ".jpg", ".jpeg", ".bmp"] }}
  //                 fileTypeDescription="PNG, JPG, BMP 파일만 허용됩니다."
  //               />
  //             </div>
  //           )}
  //         </div>
          
  //         <div className="mb-xs flex justify-center mt-sm">
  //           <input
  //             type="number"
  //             step="any"
  //             value={sigma}
  //             onChange={(e) => setSigma(e.target.value)}
  //             className="bg-surface border border-border text-textPrimary rounded-md px-2 py-1
  //             appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [&-moz-appearance:textfield]"
  //             placeholder="Sigma Value"
  //           />
  //         </div>
  //       </div>
        

  //       <div className="flex-[3] min-w-[300px]">
  //         {result && <AnalysisResultDisplay result={result} metricName="선명도" onCapture={handleCapture}/>}
  //       </div>
  //     </div>

  //     {error && (
  //       <div
  //         className="p-md bg-error/20 border-l-4 border-error text-textPrimary mb-lg rounded-sm"
  //         dangerouslySetInnerHTML={{ __html: error }}
  //       />
  //     )}

  //     {loading && (
  //       <div className="flex flex-col items-center justify-center p-xl bg-surface rounded-md shadow-md mt-lg">
  //         <p className="text-textPrimary mt-md">두유 이미지 분석 중...</p>
  //       </div>
  //     )}

  //     {/* <div className="my-md" />
  //     <FileDropzone
  //       onFileDrop={handleFileDrop}
  //       acceptedFileTypes={{ 'image/*': ['.png', '.jpg', '.jpeg', '.bmp'] }}
  //       fileTypeDescription="PNG, JPG, BMP 파일만 허용됩니다."
  //     /> */}
  //   </div>
  // );
  return (
    <div className="min-h-screen bg-gray-100 p-6 font-sans">
      {/* 상단 헤더 영역 */}
      <div className="max-w-6xl mx-auto bg-white rounded-3xl shadow-xl overflow-hidden border-2 border-black">
        <div className="bg-black text-white p-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="font-black text-2xl italic">EDU GUN</span>
            <div className="w-6 h-6 border-2 border-red-500 rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            </div>
          </div>
          <div className="flex gap-4 items-center">
            <div className="w-8 h-8 rounded-full border border-white flex items-center justify-center">👤</div>
            <div className="space-y-1">
              <div className="w-6 h-0.5 bg-white"></div>
              <div className="w-6 h-0.5 bg-white"></div>
              <div className="w-6 h-0.5 bg-white"></div>
            </div>
          </div>
        </div>

        <div className="p-8">
          <h2 className="text-3xl font-bold mb-8 text-black">세션 분석</h2>

          {/* 메인 분석 영역 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
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
                {result && <div className="absolute top-10 right-16 w-2 h-2 bg-red-500 rounded-full shadow-[0_0_5px_red]"></div>}
              </div>

              {/* Result Box */}
              <div className="w-full max-w-sm border-2 border-black rounded-xl p-4 text-center">
                <h3 className="text-xl font-bold mb-2">Result Box</h3>
                <div className="text-sm font-mono space-y-1">
                  <p>COI: (0.57, 0.48) / TTF: 6.34</p>
                  <p>MR: 0.03 / STD: (0.02, 0.15)</p>
                </div>
              </div>
            </div>

            {/* 오른쪽 영역: 분석 및 피드백 */}
            <div className="flex flex-col gap-6">
              {/* Error Analysis Box */}
              <div className="border-2 border-black rounded-2xl p-6 min-h-[150px]">
                <h3 className="text-xl font-bold mb-3">Error Analysis Box</h3>
                <p className="text-gray-700 leading-relaxed">
                  탄착군이 1시 방향에 모이며 상하로 흩어집니다.<br/>
                  <span className="font-bold">'힐링'</span>으로 인해 발생한 결과일 수 있습니다.
                </p>
              </div>

              {/* Feedback Box */}
              <div className="border-2 border-black rounded-2xl p-6 min-h-[150px]">
                <h3 className="text-xl font-bold mb-3">Feedback Box</h3>
                <p className="text-gray-700 leading-relaxed">
                  <span className="font-bold">'힐링'</span>은 손바닥 뒤꿈치를 밀어 그립이 위로 올라가는 것입니다. 
                  그립 압력 및 고정에 신경 써야 합니다.
                </p>
              </div>
            </div>
          </div>

          {/* 입력/업로드 섹션 (하단 배치) */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="flex justify-center gap-4 mb-6">
              <button 
                onClick={() => setActiveTab("camera")}
                className={`px-6 py-2 rounded-full font-bold transition ${activeTab === "camera" ? 'bg-black text-white' : 'bg-gray-200 text-gray-600'}`}
              >카메라 촬영</button>
              <button 
                onClick={() => setActiveTab("file")}
                className={`px-6 py-2 rounded-full font-bold transition ${activeTab === "file" ? 'bg-black text-white' : 'bg-gray-200 text-gray-600'}`}
              >파일 업로드</button>
            </div>

            <div className="max-w-md mx-auto">
              {activeTab === "camera" ? (
                <TakePicture onCapture={handleCapture} />
              ) : (
                <FileDropzone onFileDrop={handleFileDrop} />
              )}
              
              <div className="mt-4 flex items-center justify-center gap-2">
                <span className="text-sm font-bold text-gray-500">Sigma:</span>
                <input
                  type="number"
                  value={sigma}
                  onChange={(e) => setSigma(e.target.value)}
                  className="w-20 border-b-2 border-black text-center focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 로딩 및 에러 메시지 */}
      {loading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl text-center">
            <div className="animate-spin w-8 h-8 border-4 border-black border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="font-bold">데이터 분석 중...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShootingAnalysisPage;