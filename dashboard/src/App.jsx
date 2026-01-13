import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Layout/Sidebar';

import Overview from './pages/Overview';
import Attendance from './pages/Attendance';
import Alerts from './pages/Alerts';
import Groups from './pages/Groups';
import Agent from './pages/Agent';
import About from './pages/About';

function App() {
    return (
        <Router>
            <div className="app-container">
                <Toaster position="top-right" />
                <Sidebar />
                <div className="main-content">
                    <div className="animate-fade-in main-wrapper">
                        <Routes>
                            <Route path="/" element={<div className="scrollable-content"><Overview /></div>} />
                            <Route path="/attendance" element={<div className="scrollable-content"><Attendance /></div>} />
                            <Route path="/alerts" element={<div className="scrollable-content"><Alerts /></div>} />
                            <Route path="/groups" element={<div className="scrollable-content"><Groups /></div>} />
                            <Route path="/agent" element={<Agent />} />
                            <Route path="/about" element={<div className="scrollable-content"><About /></div>} />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </div>
                </div>
            </div>
        </Router>
    );
}

export default App;
