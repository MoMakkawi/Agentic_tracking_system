import React from 'react';
import './Card.css';

const Card = ({ children, title, subtitle, extra, className = '' }) => {
    return (
        <div className={`card glass ${className}`}>
            {(title || extra) && (
                <div className="card-header">
                    <div className="card-titles">
                        {title && <h3>{title}</h3>}
                        {subtitle && <span className="card-subtitle">{subtitle}</span>}
                    </div>
                    {extra && <div className="card-extra">{extra}</div>}
                </div>
            )}
            <div className="card-body">
                {children}
            </div>
        </div>
    );
};

export default Card;
