import React from 'react';

const ResultDisplay = ({ result, metricName }) => {
  if (!result) return null;

  return (
    <div className="flex flex-col gap-lg mt-lg">
      <h2 className="text-textPrimary text-2xl mb-md">처리 결과</h2>
      <div className="flex gap-lg flex-wrap">
        <div className="flex-1 min-w-[300px] bg-surface rounded-md shadow-md overflow-hidden">
          <h3 className="p-md bg-primary text-white m-0">입력 이미지</h3>
          <div className="p-md flex justify-center items-center bg-black min-h-[300px]">
            <img 
              src={result.input_image_url} 
              alt="입력 이미지"
              className="max-w-full max-h-[500px] object-contain"
            />
          </div>
          <div className="p-md">
            <div className="flex justify-between py-sm border-b border-border">
              <span className="text-textSecondary">크기</span>
              <span className="text-textPrimary font-medium">
                {result.input_width} x {result.input_height}
              </span>
            </div>
            <div className="flex justify-between py-sm">
              <span className="text-textSecondary">{metricName}</span>
              <span className="text-textPrimary font-medium">
                {result.input_metric.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        <div className="flex-1 min-w-[300px] bg-surface rounded-md shadow-md overflow-hidden">
          <h3 className="p-md bg-primary text-white m-0">출력 이미지</h3>
          <div className="p-md flex justify-center items-center bg-black min-h-[300px]">
            <img 
              src={result.output_image_url} 
              alt="출력 이미지"
              className="max-w-full max-h-[500px] object-contain"
            />
          </div>
          <div className="p-md">
            <div className="flex justify-between py-sm border-b border-border">
              <span className="text-textSecondary">크기</span>
              <span className="text-textPrimary font-medium">
                {result.output_width} x {result.output_height}
              </span>
            </div>
            <div className="flex justify-between py-sm">
              <span className="text-textSecondary">{metricName}</span>
              <span className="text-textPrimary font-medium">
                {result.output_metric.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-md p-md bg-surface rounded-md text-textSecondary text-sm">
        처리 시간: {result.processing_time.toFixed(2)}초
      </div>
    </div>
  );
};

export default ResultDisplay; 