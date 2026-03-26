import React from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-background-100">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-lg overflow-y-auto">
          {children}
        </main>

      </div>
    </div>
  );
};

export default Layout;
