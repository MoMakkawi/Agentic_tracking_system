import React from 'react';
import { Search, Bell, User, ChevronDown } from 'lucide-react';
import './Header.css';

const Header = () => {
    return (
        <header className="header animate-fade-in">
            <div className="header-search">
                <Search size={18} className="search-icon" />
                <input type="text" placeholder="Search for data, alerts or students..." />
            </div>

            <div className="header-actions">
                <button className="icon-btn">
                    <Bell size={20} />
                    <span className="badge"></span>
                </button>

                <div className="user-profile">
                    <div className="user-avatar">
                        <User size={18} />
                    </div>
                    <div className="user-info">
                        <span className="user-name">John Doe</span>
                        <span className="user-role">Administrator</span>
                    </div>
                    <ChevronDown size={14} />
                </div>
            </div>
        </header>
    );
};

export default Header;
