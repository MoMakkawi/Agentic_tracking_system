import React from 'react';
import './Badge.css';

const Badge = ({ children, type = 'default', style, ...props }) => {
    return (
        <span className={`badge-comp badge-${type}`} style={style} {...props}>
            {children}
        </span>
    );
};

export default Badge;
