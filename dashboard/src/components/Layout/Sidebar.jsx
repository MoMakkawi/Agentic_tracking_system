import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    CalendarCheck,
    AlertTriangle,
    Users,
    Bot,
    BarChart3
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
    const menuItems = [
        { name: 'Overview', icon: <LayoutDashboard size={20} />, path: '/' },
        { name: 'Attendance', icon: <CalendarCheck size={20} />, path: '/attendance' },
        { name: 'Alerts', icon: <AlertTriangle size={20} />, path: '/alerts' },
        { name: 'Groups', icon: <Users size={20} />, path: '/groups' },
        { name: 'Agent', icon: <Bot size={20} />, path: '/agent' },
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
