import React from 'react';
import { Link } from 'react-router-dom';
import { FaWaveSquare } from 'react-icons/fa';

const HomePage = () => {
  return (
    <div className="p-lg">
      <h1 className="text-textPrimary text-3xl mb-lg">두유 분석 및 예측 시스템</h1>
      <p className="text-textSecondary mb-xl max-w-[800px] leading-relaxed">
        두유 측정기 이미지를 이용한 AI 기반 시스템입니다. 
        두유 이미지 분석, 두유 이미지 처리, 실시간 두유 농도 예측을 제공합니다.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-lg mt-xl">
        <Link 
          to="/shootinganalysis"
          className="bg-surface rounded-md p-lg shadow-md hover:-translate-y-1 hover:shadow-lg transition-all duration-fast flex flex-col items-center text-center"
        >
          <div className="text-5xl text-primary mb-md">
            <FaWaveSquare />
          </div>
          <h3 className="text-textPrimary text-xl mb-md">두유 분석</h3>
          <p className="text-textSecondary text-sm">
            두유의 성분을 분석합니다.
          </p>
        </Link>
      </div>
    </div>
  );
};

export default HomePage; 