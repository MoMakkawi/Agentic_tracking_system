import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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
                <Sidebar />
                <div className="main-content">

                    <div className="animate-fade-in">
                        <Routes>
                            <Route path="/" element={<Overview />} />
                            <Route path="/attendance" element={<Attendance />} />
                            <Route path="/alerts" element={<Alerts />} />
                            <Route path="/groups" element={<Groups />} />
                            <Route path="/agent" element={<Agent />} />
                            <Route path="/about" element={<About />} />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </div>
                </div>
            </div>
        </Router>
    );
}

export default App;
