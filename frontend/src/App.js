import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainPage from './MainPage';
import SharedPromptPage from './SharedPromptPage';
import GalleryPage from './GalleryPage';
import SettingsPage from './SettingsPage';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainPage />} />
      <Route path="/prompt/:promptId" element={<SharedPromptPage />} />
      <Route path="/gallery" element={<GalleryPage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  );
}

export default App;