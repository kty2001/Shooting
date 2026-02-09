import React from 'react';
import { NavLink } from 'react-router-dom';
import { FaImage, FaBullseye, FaWaveSquare } from 'react-icons/fa';

const Sidebar = () => {
  return (
    <nav className="w-[240px] bg-surface p-md shadow-md">
      <h3 className="text-textSecondary text-sm mb-md pl-sm">메인 메뉴</h3>
      <NavLink 
        to="/" 
        end
        className={({ isActive }) => `
          flex items-center p-md rounded-md mb-sm text-textPrimary
          transition-colors duration-fast hover:bg-white/5
          ${isActive ? 'bg-primary text-white' : ''}
        `}
      >
        <FaImage className="mr-md text-lg" />
        홈
      </NavLink>

      <h3 className="text-textSecondary text-sm mb-md pl-sm">분석 메뉴</h3>
      <NavLink 
        to="/shootinganalysis"
        className={({ isActive }) => `
          flex items-center p-md rounded-md mb-sm text-textPrimary
          transition-colors duration-fast hover:bg-white/5
          ${isActive ? 'bg-primary text-white' : ''}
        `}
      >
        <FaBullseye className="mr-md text-lg" />
        탄착 분석
      </NavLink>

      <NavLink 
        to="/seriesanalysis"
        className={({ isActive }) => `
          flex items-center p-md rounded-md mb-sm text-textPrimary
          transition-colors duration-fast hover:bg-white/5
          ${isActive ? 'bg-primary text-white' : ''}
        `}
      >
        <FaWaveSquare className="mr-md text-lg" />
        추이 분석
      </NavLink>
    </nav>
  );
};

export default Sidebar; 