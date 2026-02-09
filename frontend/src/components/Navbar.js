import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <header className="bg-black text-white h-[60px] flex items-center px-lg shadow-md z-10">
      <Link to="/" className="text-2xl font-bold text-white mr-auto">
        EDU GUN - 탄착 분석 시스템
      </Link>
      
      <div className="ml-auto flex items-center gap-2">
        <button className="p-2 hover:bg-white/10 rounded-full">
          <img
            src="/account_icon.ico"
            alt="account"
            className="w-7 h-7 rounded-full border border-white"
          />
        </button>

        <button className="p-2 hover:bg-white/10 rounded-md">
          <img src="/menu_icon.ico" alt="menu" className="w-6 h-6" />
        </button>
      </div>
    </header>
  );
};

export default Navbar; 