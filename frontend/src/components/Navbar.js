import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <header className="bg-surface text-textPrimary h-[60px] flex items-center px-lg shadow-md z-10">
      <Link to="/" className="text-2xl font-bold text-primary mr-auto">
        두유 분석 및 예측 시스템
      </Link>
    </header>
  );
};

export default Navbar; 