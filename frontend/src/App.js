import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainPage from './MainPage';
import SharedPromptPage from './SharedPromptPage';
import GalleryPage from './GalleryPage'; // Import GalleryPage
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainPage />} />
      <Route path="/prompt/:promptId" element={<SharedPromptPage />} />
      <Route path="/gallery" element={<GalleryPage />} /> {/* Add Gallery Route */}
    </Routes>
  );
}

export default App;
