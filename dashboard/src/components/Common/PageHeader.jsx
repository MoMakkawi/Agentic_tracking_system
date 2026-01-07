import React from 'react';
import './PageHeader.css';

const PageHeader = ({ title, icon: Icon, description, actions, gradient, iconColor, iconBgColor }) => {
    return (
        <div className="page-header-component">
            <div className="header-left">
                {Icon && (
                    <div
                        className="header-icon-container glass-icon"
                        style={{
                            background: iconBgColor || 'var(--bg-secondary)',
                            color: iconColor || 'var(--accent-primary)',
                            borderColor: iconColor ? `${iconColor}40` : 'var(--border-primary)'
                        }}
                    >
                        <Icon size={40} />
                    </div>
                )}
                <div>
                    <h1 className="header-title" style={gradient ? { background: gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' } : {}}>
                        {title}
                    </h1>
                    {description && (
                        <p className="header-description">
                            {description}
                        </p>
                    )}
                </div>
            </div>
            {actions && (
                <div className="header-actions">
                    {actions}
                </div>
            )}
        </div>
    );
};

export default PageHeader;
