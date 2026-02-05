import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ShootingAnalysisPage from './pages/ShootingAnalysisPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/shootinganalysis" element={<ShootingAnalysisPage />} />
      </Routes>
    </Layout>
  );
}

export default App; 