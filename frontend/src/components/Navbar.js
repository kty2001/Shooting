import React from 'react';
import { Link } from 'react-router-dom';
import { VscAccount } from "react-icons/vsc";
import { CiMenuBurger } from "react-icons/ci";

const Navbar = () => {
  return (
    <header className="bg-background h-[60px] flex items-center px-lg shadow-md z-10 border-b border-border">
      <Link to="/" className="text-2xl font-bold text-white mr-auto tracking-tight">
        <span className="text-primary-400">PRAX</span>AI
      </Link>

      <div className="ml-auto flex items-center gap-2">
        <button className="p-2 hover:bg-surface rounded-full transition-colors duration-fast text-textSecondary hover:text-textPrimary">
          <VscAccount className="w-7 h-7" />
        </button>

        <button className="p-2 hover:bg-surface rounded-md transition-colors duration-fast text-textSecondary hover:text-textPrimary">
          <CiMenuBurger className="w-7 h-7" />
        </button>
      </div>
    </header>
  );
};

export default Navbar;
