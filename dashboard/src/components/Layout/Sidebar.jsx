import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    CalendarCheck,
    AlertTriangle,
    Users,
    Bot,
    BarChart3,
    Info,
    Activity
} from 'lucide-react';
const logo = '/logo.png';
import './Sidebar.css';

const Sidebar = () => {
    const menuItems = [
        { name: 'Overview', icon: <Activity size={20} />, path: '/', color: '#8b5cf6' },
        { name: 'Attendance', icon: <CalendarCheck size={20} />, path: '/attendance', color: '#6366f1' },
        { name: 'Alerts', icon: <AlertTriangle size={20} />, path: '/alerts', color: '#f59e0b' },
        { name: 'Groups', icon: <Users size={20} />, path: '/groups', color: '#10b981' },
        { name: 'Agent', icon: <Bot size={20} />, path: '/agent', color: '#a78bfa' },
        { name: 'About', icon: <Info size={20} />, path: '/about', color: '#22d3ee' },
    ];

    return (
        <aside className="sidebar glass">
            <NavLink to="/" className="sidebar-logo-link">
                <div className="sidebar-logo">
                    <img src={logo} alt="ATS Logo" className="logo-image" />
                    <div className="logo-text-container">
                        <h1 className="logo-primary">ATS</h1>
                        <p className="logo-subtitle">Agentic Tracking System</p>
                    </div>
                </div>
            </NavLink>

            <nav className="sidebar-nav">
                {/* Monitored Section */}
                <div className="nav-section">
                    <NavLink
                        to="/"
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        style={{ '--item-color': '#8b5cf6' }}
                    >
                        <Activity size={20} />
                        <span>Overview</span>
                    </NavLink>
                    <NavLink
                        to="/groups"
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        style={{ '--item-color': '#10b981' }}
                    >
                        <Users size={20} />
                        <span>Groups</span>
                    </NavLink>
                </div>

                <div className="nav-divider"></div>

                {/* Data Section */}
                <div className="nav-section">
                    <NavLink
                        to="/attendance"
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        style={{ '--item-color': '#6366f1' }}
                    >
                        <CalendarCheck size={20} />
                        <span>Attendance</span>
                    </NavLink>
                    <NavLink
                        to="/alerts"
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        style={{ '--item-color': '#f59e0b' }}
                    >
                        <AlertTriangle size={20} />
                        <span>Alerts</span>
                    </NavLink>
                </div>

                <div className="nav-divider"></div>

                {/* AI Agent Section */}
                <div className="nav-section">
                    <NavLink
                        to="/agent"
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        style={{ '--item-color': '#a78bfa' }}
                    >
                        <Bot size={20} />
                        <span>Agent</span>
                    </NavLink>
                </div>

                <div className="nav-divider"></div>



                {/* Meta Section */}
                <div className="nav-section">
                    <NavLink
                        to="/about"
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        style={{ '--item-color': '#22d3ee' }}
                    >
                        <Info size={20} />
                        <span>About</span>
                    </NavLink>
                </div>
            </nav>

        </aside>
    );
};

export default Sidebar;
