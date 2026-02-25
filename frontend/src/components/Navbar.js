import React from 'react';
import { Link } from 'react-router-dom';
import { VscAccount } from "react-icons/vsc";
import { CiMenuBurger } from "react-icons/ci";

const Navbar = () => {
  return (
    <header className="bg-black text-white h-[60px] flex items-center px-lg shadow-md z-10">
      <Link to="/" className="text-2xl font-bold text-white mr-auto">
        EDU GUN - 탄착 분석 시스템
      </Link>
      
      <div className="ml-auto flex items-center gap-2">
        <button className="p-2 hover:bg-white/10 rounded-full">
          <VscAccount className="w-7 h-7" />
        </button>

        <button className="p-2 hover:bg-white/10 rounded-md">
          <CiMenuBurger className="w-7 h-7" />
        </button>
      </div>
    </header>
  );
};

export default Navbar; 