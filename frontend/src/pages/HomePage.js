import React from 'react';
import { Link } from 'react-router-dom';
import { FaBullseye } from 'react-icons/fa';
import { FaWaveSquare } from 'react-icons/fa';

const HomePage = () => {
  return (
    <div className="p-lg">
      <h1 className="text-textPrimary text-3xl font-bold mb-sm">AI 탄착 분석 시스템</h1>
      <p className="text-textSecondary mb-xl max-w-[800px] leading-relaxed">
        탄착 데이터를 이용한 AI 기반 사격 코칭 시스템입니다.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-lg mt-xl">
        <Link
          to="/shootinganalysis"
          className="bg-surface border border-border rounded-lg p-lg shadow-md hover:-translate-y-1 hover:shadow-blue hover:border-primary-500 transition-all duration-fast flex flex-col items-center text-center group"
        >
          <div className="text-5xl text-primary-400 mb-md group-hover:text-primary-500 transition-colors duration-fast">
            <FaBullseye />
          </div>
          <h3 className="text-textPrimary text-xl font-semibold mb-sm">탄착 분석</h3>
          <p className="text-textSecondary text-sm">
            탄착군 패턴을 분석하고 오류를 진단합니다.
          </p>
        </Link>

        <Link
          to="/seriesanalysis"
          className="bg-surface border border-border rounded-lg p-lg shadow-md hover:-translate-y-1 hover:shadow-blue hover:border-primary-500 transition-all duration-fast flex flex-col items-center text-center group"
        >
          <div className="text-5xl text-primary-400 mb-md group-hover:text-primary-500 transition-colors duration-fast">
            <FaWaveSquare />
          </div>
          <h3 className="text-textPrimary text-xl font-semibold mb-sm">추이 분석</h3>
          <p className="text-textSecondary text-sm">
            세션별 결과 추이를 분석합니다.
          </p>
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
