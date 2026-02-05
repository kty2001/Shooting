import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import SoyanalysisPage from './pages/SoyanalysisPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/soyanalysis" element={<SoyanalysisPage />} />
      </Routes>
    </Layout>
  );
}

export default App; 