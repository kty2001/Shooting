import React, { useState } from 'react';
import FileDropzone from '../components/FileDropzone';
import AnalysisResultDisplay from '../components/AnalysisResultDisplay';
import { processSoyanalysis } from '../utils/api';
import TakePicture from '../components/TakePicture';

const SoyanalysisPage = () => {
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
      const response = await processSoyanalysis(file, sigma);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-lg">

      <div className="flex gap-lg flex-wrap">
        <div className="flex-[1] min-w-[300px]">
          <div className="flex border-b border-border mt-md">
            <button
              className={`flex-1 px-4 py-2 text-lg ${
                activeTab === "camera"
                  ? "bg-primary text-white font-semibold"
                  : "text-textSecondary hover:bg-muted"
              }`}
              onClick={() => setActiveTab("camera")}
            >
              카메라 촬영
            </button>
            <button
              className={`flex-1 px-4 py-2 text-lg ${
                activeTab === "file"
                  ? "bg-primary text-white font-semibold"
                  : "text-textSecondary hover:bg-muted"
              }`}
              onClick={() => setActiveTab("file")}
            >
              파일 업로드
            </button>
          </div>

          <div className="p-md">
            {activeTab === "camera" && <TakePicture onCapture={handleCapture} />}
            {activeTab === "file" && (
              <div className="min-h-[400px] flex items-center justify-center">
                <FileDropzone
                  onFileDrop={handleFileDrop}
                  acceptedFileTypes={{ "image/*": [".png", ".jpg", ".jpeg", ".bmp"] }}
                  fileTypeDescription="PNG, JPG, BMP 파일만 허용됩니다."
                />
              </div>
            )}
          </div>
          
          <div className="mb-xs flex justify-center mt-sm">
            <input
              type="number"
              step="any"
              value={sigma}
              onChange={(e) => setSigma(e.target.value)}
              className="bg-surface border border-border text-textPrimary rounded-md px-2 py-1
              appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [&-moz-appearance:textfield]"
              placeholder="Sigma Value"
            />
          </div>
        </div>
        

        <div className="flex-[3] min-w-[300px]">
          {result && <AnalysisResultDisplay result={result} metricName="선명도" onCapture={handleCapture}/>}
        </div>
      </div>

      {error && (
        <div
          className="p-md bg-error/20 border-l-4 border-error text-textPrimary mb-lg rounded-sm"
          dangerouslySetInnerHTML={{ __html: error }}
        />
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center p-xl bg-surface rounded-md shadow-md mt-lg">
          <p className="text-textPrimary mt-md">두유 이미지 분석 중...</p>
        </div>
      )}

      {/* <div className="my-md" />
      <FileDropzone
        onFileDrop={handleFileDrop}
        acceptedFileTypes={{ 'image/*': ['.png', '.jpg', '.jpeg', '.bmp'] }}
        fileTypeDescription="PNG, JPG, BMP 파일만 허용됩니다."
      /> */}
    </div>
  );
};

export default SoyanalysisPage;