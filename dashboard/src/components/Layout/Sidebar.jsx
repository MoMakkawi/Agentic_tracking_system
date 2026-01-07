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
            <div className="sidebar-logo">
                <div className="logo-icon">ATS</div>
                <span className="logo-text">Agentic Tracking</span>
            </div>

            <nav className="sidebar-nav">
                {menuItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        style={{ '--item-color': item.color }}
                    >
                        {item.icon}
                        <span>{item.name}</span>
                    </NavLink>
                ))}
            </nav>


        </aside>
    );
};

export default Sidebar;
