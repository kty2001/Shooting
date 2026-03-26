import React from 'react';
import { NavLink } from 'react-router-dom';
import { FaImage, FaBullseye, FaWaveSquare } from 'react-icons/fa';

const Sidebar = () => {
  return (
    <nav className="w-[220px] bg-background border-r border-border p-md flex flex-col gap-xs">
      <p className="text-textMuted text-xs uppercase tracking-widest mb-sm pl-sm">메인 메뉴</p>
      <NavLink
        to="/"
        end
        className={({ isActive }) => `
          flex items-center gap-md px-sm py-[10px] rounded-md text-sm font-medium
          transition-colors duration-fast
          ${isActive
            ? 'bg-primary-600 text-white shadow-blue'
            : 'text-textSecondary hover:bg-surface hover:text-textPrimary'}
        `}
      >
        <FaImage className="text-base shrink-0" />
        홈
      </NavLink>

      <p className="text-textMuted text-xs uppercase tracking-widest mb-sm pl-sm mt-md">분석 메뉴</p>
      <NavLink
        to="/shootinganalysis"
        className={({ isActive }) => `
          flex items-center gap-md px-sm py-[10px] rounded-md text-sm font-medium
          transition-colors duration-fast
          ${isActive
            ? 'bg-primary-600 text-white shadow-blue'
            : 'text-textSecondary hover:bg-surface hover:text-textPrimary'}
        `}
      >
        <FaBullseye className="text-base shrink-0" />
        탄착 분석
      </NavLink>

      <NavLink
        to="/seriesanalysis"
        className={({ isActive }) => `
          flex items-center gap-md px-sm py-[10px] rounded-md text-sm font-medium
          transition-colors duration-fast
          ${isActive
            ? 'bg-primary-600 text-white shadow-blue'
            : 'text-textSecondary hover:bg-surface hover:text-textPrimary'}
        `}
      >
        <FaWaveSquare className="text-base shrink-0" />
        추이 분석
      </NavLink>
    </nav>
  );
};

export default Sidebar;
