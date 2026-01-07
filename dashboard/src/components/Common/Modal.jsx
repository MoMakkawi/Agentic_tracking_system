import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import './Modal.css';

const Modal = ({ isOpen, onClose, title, children }) => {
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    console.log('Modal Render Check. isOpen:', isOpen);

    if (!isOpen) return null;

    const modalRoot = document.getElementById('modal-root') || document.body;

    return createPortal(
        <div className={`modal-overlay active animate-fade-in`} onClick={onClose} style={{ zIndex: 10000 }}>
            <div className="modal-content glass shadow-2xl animate-scale-in" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">{title}</h2>
                    <button className="modal-close-btn icon-btn" onClick={onClose}>
                        <X size={24} />
                    </button>
                </div>
                <div className="modal-body">
                    {children}
                </div>
            </div>
        </div>,
        modalRoot
    );
};

export default Modal;
