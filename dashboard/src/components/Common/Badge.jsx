import React from 'react';
import './Badge.css';

const Badge = ({ children, type = 'default', style, className = '', ...props }) => {
    return (
        <span className={`badge-comp badge-${type} ${className}`} style={style} {...props}>
            {children}
        </span>
    );
};

export default Badge;
