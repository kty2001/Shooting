import React, { useState } from 'react';

const AnalysisResultDisplay = ({ result, metricName }) => {
  const [values, setValues] = useState(["", "", "", "", ""]);
  
  if (!result) return null;

  const handleInputChange = (index, newValue) => {
    const newValues = [...values];
    newValues[index] = newValue;
    setValues(newValues);
  };

  const generateFilename = (base) => {
    const cleaned = values.map(v => v === "" ? "0" : parseFloat(v).toFixed(1));
    return `${base}${result.predict_value}_${cleaned.join("_")}.png`;
  };

  const generateFolderName = () => {
    const now = new Date();
    const pad = (num) => num.toString().padStart(2, "0");
    const year = now.getFullYear().toString().slice(-2);
    const month = pad(now.getMonth() + 1);
    const day = pad(now.getDate());
    const hours = pad(now.getHours());
    const minutes = pad(now.getMinutes());
    const seconds = pad(now.getSeconds());

    return `${year}${month}${day}_${hours}${minutes}${seconds}`;
  };

  const downloadImage = async (url, filename) => {
    const response = await fetch(url, { mode: "cors" });
    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);
  };

  return (
    <div className="flex flex-col gap-lg mt-lg">
      <h2 className="text-textPrimary text-2xl mb-sm pb-1 border-b border-border"><strong>처리 결과</strong></h2>
      <div className="flex gap-lg flex-wrap">

        <div className="flex-[1] min-w-[300px] bg-surface rounded-md shadow-md overflow-hidden">
          <h3 className="p-md bg-primary text-white m-0">입력 이미지</h3>
          <div className="p-md flex justify-center items-center bg-gray-300 min-h-[300px]">
            <img 
              src={result.input_image_url} 
              alt="입력 이미지"
              className="max-w-full h-[500px] object-contain"
            />
          </div>
          <div className="p-md">
            <div className="flex justify-between py-sm text-2xl">
              <span className="text-textSecondary">크기</span>
              <span className="text-textPrimary font-medium ">
                {result.input_height} x {result.input_width}
              </span>
            </div>
          </div>
        </div>

        <div className="flex-[1] min-w-[300px] bg-surface rounded-md shadow-md overflow-hidden">
          <h3 className="p-md bg-primary text-white m-0">크롭 이미지</h3>
          <div className="p-md flex justify-center items-center bg-gray-300 min-h-[300px]">
            <img 
              src={result.cropped_image_url} 
              alt="크롭 이미지"
              className="max-w-full max-h-[500px] object-contain"
            />
          </div>
          <div className="p-md">
            <div className="flex justify-between items-end px-6 py-sm mt-8">
              <span className="text-textSecondary text-4xl">농도</span>
              <span className="text-red-600 font-bold text-8xl">
                {result.predict_value}
              </span>
            </div>

            <div className="flex gap-md mt-20 mb-4">
              {/* 이미지 분석 버튼 */}
              <button
                onClick={() => window.dispatchEvent(new Event("trigger-camera-capture"))}
                className="flex-1 px-4 py-4 bg-red-600 text-white text-2xl font-bold rounded-md shadow hover:bg-primary-dark transition duration-200"
              >
                측정
              </button>

              {/* 이미지 저장 버튼 */}
              <button
                onClick={() => {
                  const folderName = generateFolderName();
                  downloadImage(result.input_image_url, `${folderName}/${generateFilename("input")}`);
                  downloadImage(result.cropped_image_url, `${folderName}/${generateFilename("cropped")}`);
                  downloadImage(result.output_image_url, `${folderName}/${generateFilename("analysis")}`);
                }}
                className="flex-1 px-4 py-2 bg-green-600 text-white text-2xl font-bold rounded-md shadow hover:bg-secondary-dark transition duration-200"
              >
                저장
              </button>
            </div>
          </div>
        </div>

        <div className="flex-[1] min-w-[300px] bg-surface rounded-md shadow-md overflow-hidden">
          <h3 className="p-md bg-primary text-white m-0">분석 이미지</h3>
          <div className="p-md flex justify-center items-center bg-gray-300 min-h-[300px]">
            <img 
              src={result.output_image_url} 
              alt="분석 이미지"
              className="max-w-full max-h-[500px] object-contain"
            />
          </div>
          <div className="p-md text-2xl">
            <div className="flex justify-between py-sm border-b border-border">
              <span className="text-textSecondary">Min Index</span>
              <span className="text-textPrimary font-medium">
                {result.min_index}
              </span>
            </div>
            <div className="flex justify-between py-sm border-b border-border">
              <span className="text-textSecondary">Width</span>
              <span className="text-textPrimary font-medium">
                {result.width}
              </span>
            </div>
            <div className="flex justify-between py-sm">
              <span className="text-textSecondary">Predict Value</span>
              <span className="text-textPrimary font-medium">
                {result.predict_value}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 실수 입력란 */}
      <div className="grid grid-cols-5 gap-md mb-xs">
        {values.map((val, idx) => (
          <input
            key={idx}
            type="number"
            step="any"
            className="bg-surface border border-border text-textPrimary rounded-md px-2 py-1
            appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [&-moz-appearance:textfield]"
            placeholder={`측정값 ${idx + 1}`}
            value={val}
            onChange={(e) => handleInputChange(idx, e.target.value)}
          />
        ))}
      </div>

      {/* 저장 버튼 (하나만) */}
      <div className="flex justify-center">
        <button
          onClick={() => {
            const folderName = generateFolderName();
            downloadImage(result.input_image_url, `${folderName}/${generateFilename("input")}`);
            downloadImage(result.cropped_image_url, `${folderName}/${generateFilename("cropped")}`);
            downloadImage(result.output_image_url, `${folderName}/${generateFilename("analysis")}`);
          }}
          className="inline-block mt-md px-6 py-2 bg-primary text-white font-semibold rounded-md shadow hover:bg-primary-dark transition duration-200 min-w-[300px] text-center"
        >
          이미지 저장
        </button>
      </div>
    </div>
  );
};

export default AnalysisResultDisplay; 