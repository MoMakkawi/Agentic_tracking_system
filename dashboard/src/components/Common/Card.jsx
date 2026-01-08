import React from 'react';
import './Card.css';

const Card = ({ children, title, subtitle, extra, className = '', theme = '', style = {} }) => {
    return (
        <div className={`card glass ${theme ? `theme-${theme}` : ''} ${className}`} style={style}>
            {(title || extra) && (
                <div className="card-header">
                    <div className="card-titles">
                        {title && <h3>{title}</h3>}
                        {subtitle && <span className="card-subtitle">{subtitle}</span>}
                    </div>
                    {extra && <div className="card-extra">{extra}</div>}
                </div>
            )}
            <div className="card-body" style={style.padding === '0' || style.padding === 0 ? { padding: 0 } : {}}>
                {children}
            </div>
        </div>
    );
};

export default Card;
