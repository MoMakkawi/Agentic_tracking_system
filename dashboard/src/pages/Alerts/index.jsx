import React, { useState, useEffect } from 'react';
import { alertService, attendanceService } from '../../services/api';
import Card from '../../components/Common/Card';
import Table from '../../components/Common/Table';
import Badge from '../../components/Common/Badge';
import Modal from '../../components/Common/Modal';
import {
    AlertTriangle, ShieldCheck, User, Clock, Smartphone, Search,
    ChevronLeft, ChevronRight, Calendar, Hash, Users, AlertCircle,
    CheckCircle2, Shield, Info, Bookmark
} from 'lucide-react';
import './Alerts.css';

const Alerts = () => {
    const [activeTab, setActiveTab] = useState('device');
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [pageSize] = useState(10);
    const [total, setTotal] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [sortConfig, setSortConfig] = useState({ key: 'id', direction: 'desc' });
    const [searchTerm, setSearchTerm] = useState('');

    // Modal state
    const [selectedSession, setSelectedSession] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalLoading, setModalLoading] = useState(false);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            fetchAlerts();
        }, 300);
        return () => clearTimeout(timeoutId);
    }, [activeTab, page, sortConfig, searchTerm]);

    const fetchAlerts = async () => {
        setLoading(true);
        try {
            let response;
            const params = {
                page,
                page_size: pageSize,
                order_by: sortConfig.key,
                order_direction: sortConfig.direction
            };

            if (searchTerm) {
                params.search = searchTerm;
            }

            if (activeTab === 'device') {
                response = await alertService.getDeviceAlerts(params);
            } else if (activeTab === 'identity') {
                response = await alertService.getIdentityAlerts(params);
            } else {
                response = await alertService.getTimestampAlerts(params);
            }

            setAlerts(response.data.items);
            setTotal(response.data.total);
            setTotalPages(response.data.total_pages);
        } catch (error) {
            console.error(`Error fetching ${activeTab} alerts:`, error);
        } finally {
            setLoading(false);
        }
    };

    const handleSort = (key) => {
        let direction = 'desc';
        if (sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc';
        }
        setSortConfig({ key, direction });
        setPage(1);
    };

    const handleRowClick = async (alert) => {
        if (!alert.session_id) return;

        setModalLoading(true);
        setIsModalOpen(true);
        setSelectedSession(null);

        try {
            const response = await attendanceService.filterSessions({
                session_id: alert.session_id,
                page: 1,
                page_size: 1
            });

            if (response.data.items && response.data.items.length > 0) {
                setSelectedSession(response.data.items[0]);
            }
        } catch (error) {
            console.error('Error fetching session details:', error);
        } finally {
            setModalLoading(false);
        }
    };

    const getColumns = () => {
        const common = [
            {
                title: 'Reasons',
                key: 'reasons',
                sortable: false,
                render: (reasons) => (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {Array.isArray(reasons) ? reasons.map((reason, idx) => (
                            <Badge key={idx} type="warning" style={{ fontSize: '0.75rem' }}>{reason}</Badge>
                        )) : <Badge type="warning">{reasons}</Badge>}
                    </div>
                )
            },
        ];

        if (activeTab === 'device') {
            return [
                { title: 'ID', key: 'id', render: (val) => <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>#{val}</span> },
                { title: 'Session', key: 'session_id', render: (val) => <Badge type="info">ID: {val}</Badge> },
                { title: 'Device Fingerprint', key: 'device_id', render: (val) => <code className="glass-code">{val}</code> },
                ...common
            ];
        } else if (activeTab === 'identity') {
            return [
                { title: 'ID', key: 'id', render: (val) => <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>#{val}</span> },
                { title: 'Identity UID', key: 'uid', render: (val) => <span style={{ fontWeight: '600' }}>{val}</span> },
                {
                    title: 'Anomaly Sessions',
                    key: 'anomaly_sessions',
                    sortable: false,
                    render: (sessions) => (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                            {sessions?.map((sid) => (
                                <Badge
                                    key={sid}
                                    type="danger"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleRowClick({ session_id: sid });
                                    }}
                                    style={{ cursor: 'pointer', fontSize: '0.75rem' }}
                                >
                                    ID: {sid}
                                </Badge>
                            ))}
                        </div>
                    )
                },
                { title: 'Device', key: 'device_id', render: (val) => <code className="glass-code">{val}</code> },
                { title: 'Anomaly Cycles', key: 'repeated_anomaly_count', render: (val) => <Badge type="danger">{val}</Badge> },
                ...common
            ];
        } else {
            return [
                { title: 'ID', key: 'id', render: (val) => <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>#{val}</span> },
                { title: 'Session', key: 'session_id', render: (val) => <Badge type="info">ID: {val}</Badge> },
                { title: 'Identity UID', key: 'uid', render: (val) => <span style={{ fontWeight: '600' }}>{val}</span> },
                {
                    title: 'Temporal Record', key: 'timestamp', render: (val) => (
                        <div className="timestamp-cell" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '2px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-primary)', fontWeight: '600', fontSize: '0.9rem' }}>
                                <Calendar size={12} color="var(--accent-warning)" />
                                {new Date(val).toLocaleDateString('fr-FR', {
                                    year: 'numeric',
                                    month: '2-digit',
                                    day: '2-digit'
                                })}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                <Clock size={12} />
                                {new Date(val).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                        </div>
                    )
                },
                { title: 'Device', key: 'device_id', render: (val) => <code className="glass-code">{val}</code> },
                ...common
            ];
        }
    };

    return (
        <div className="alerts-page animate-fade-in">
            <div className="page-header" style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                        <div className="header-icon-container">
                            <AlertTriangle size={32} color="var(--accent-warning)" />
                        </div>
                        <h1 style={{ fontSize: '2.5rem', margin: 0, background: 'linear-gradient(to right, var(--text-primary), var(--accent-warning))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                            Alerts
                        </h1>
                    </div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginLeft: '3.5rem' }}>
                        Automated anomaly detection and multi-factor tracking alerts.
                    </p>
                </div>

                <div className="search-container" style={{ position: 'relative' }}>
                    <Search style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} size={20} />
                    <input
                        type="text"
                        placeholder="Search alerts..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setPage(1);
                        }}
                        style={{
                            padding: '1rem 1rem 1rem 3.5rem',
                            borderRadius: '16px',
                            border: '1px solid var(--border-primary)',
                            background: 'var(--bg-secondary)',
                            color: 'var(--text-primary)',
                            width: '350px',
                            transition: 'all 0.3s ease',
                            outline: 'none',
                            fontSize: '1rem'
                        }}
                        className="search-input"
                    />
                </div>
            </div>

            <div className="alerts-tabs glass">
                <button
                    className={`tab-item ${activeTab === 'device' ? 'active' : ''}`}
                    onClick={() => {
                        setActiveTab('device');
                        setPage(1);
                        setSortConfig({ key: 'id', direction: 'desc' });
                        setSearchTerm('');
                    }}
                >
                    <Smartphone size={18} />
                    Device Alerts
                </button>
                <button
                    className={`tab-item ${activeTab === 'identity' ? 'active' : ''}`}
                    onClick={() => {
                        setActiveTab('identity');
                        setPage(1);
                        setSortConfig({ key: 'id', direction: 'desc' });
                        setSearchTerm('');
                    }}
                >
                    <User size={18} />
                    Identity Mismatch
                </button>
                <button
                    className={`tab-item ${activeTab === 'timestamp' ? 'active' : ''}`}
                    onClick={() => {
                        setActiveTab('timestamp');
                        setPage(1);
                        setSortConfig({ key: 'timestamp', direction: 'desc' });
                        setSearchTerm('');
                    }}
                >
                    <Clock size={18} />
                    Timestamp Alerts
                </button>
            </div>

            <Card
                className="alerts-card glass overflow-hidden"
                style={{ padding: '0' }}
                title={`${activeTab.charAt(0).toUpperCase() + activeTab.slice(1).replace('-', ' ')} Anomalies`}
                subtitle={`Total ${total} security incidents identified`}
                extra={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-success)', fontSize: '0.9rem', fontWeight: '600' }}>
                        <ShieldCheck size={18} />
                        System Active
                    </div>
                }
            >
                <Table
                    columns={getColumns()}
                    data={alerts}
                    loading={loading}
                    onSort={handleSort}
                    sortConfig={sortConfig}
                    onRowClick={activeTab !== 'identity' ? handleRowClick : null}
                />

                <div className="pagination" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1.5rem', padding: '1.5rem 0', borderTop: '1px solid var(--border-primary)' }}>
                    <button
                        disabled={page === 1}
                        onClick={() => setPage(p => p - 1)}
                        className={`icon-btn hover-lift ${page === 1 ? 'disabled' : ''}`}
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <div className="page-indicator">
                        Page <span className="current-page">{page}</span> of <span className="total-pages">{totalPages}</span>
                    </div>
                    <button
                        disabled={page === totalPages}
                        onClick={() => setPage(p => p + 1)}
                        className={`icon-btn hover-lift ${page === totalPages ? 'disabled' : ''}`}
                    >
                        <ChevronRight size={20} />
                    </button>
                </div>
            </Card>

            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={`Linked Session Insight #${selectedSession?.session_id || ''}`}
            >
                {modalLoading ? (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        Retrieving session intelligence...
                    </div>
                ) : selectedSession ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                            <div className="detail-item glass" style={{ padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-primary)' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>Context</label>
                                <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{selectedSession.session_context || 'General Session'}</div>
                            </div>
                            <div className="detail-item glass" style={{ padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-primary)' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>Recorded At</label>
                                <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{new Date(selectedSession.received_at).toLocaleString()}</div>
                            </div>
                        </div>

                        {selectedSession.matched_sessions && selectedSession.matched_sessions.length > 0 && (
                            <section>
                                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                                    <Bookmark size={18} color="var(--accent-primary)" />
                                    Matched Calendar Sessions ({selectedSession.matched_sessions.length})
                                </h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    {selectedSession.matched_sessions.map((ms, idx) => (
                                        <div key={idx} className="glass" style={{
                                            padding: '1.25rem',
                                            borderRadius: '16px',
                                            border: '1px solid var(--border-primary)',
                                            background: 'rgba(var(--accent-primary-rgb), 0.03)',
                                            transition: 'transform 0.2s ease'
                                        }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                                <div style={{ fontWeight: '700', fontSize: '1.05rem', color: 'var(--text-primary)', lineHeight: '1.4' }}>
                                                    {ms.summary}
                                                </div>
                                                <Badge type="info" style={{ whiteSpace: 'nowrap' }}>ID: {ms.id}</Badge>
                                            </div>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                    <Clock size={14} color="var(--accent-primary)" />
                                                    <span style={{ fontWeight: '500' }}>Start:</span>
                                                    <span>{new Date(ms.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                                </div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                    <Clock size={14} color="var(--accent-primary)" />
                                                    <span style={{ fontWeight: '500' }}>End:</span>
                                                    <span>{new Date(ms.end).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        {selectedSession.alerts && selectedSession.alerts.length > 0 && (
                            <section>
                                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', color: 'var(--accent-warning)', fontWeight: '700' }}>
                                    <Shield size={18} />
                                    Security Anomalies ({selectedSession.alerts.length})
                                </h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    {selectedSession.alerts.map((alert, idx) => (
                                        <div key={idx} className="glass" style={{
                                            padding: '1.25rem',
                                            borderRadius: '16px',
                                            border: '1px solid rgba(var(--accent-warning-rgb), 0.2)',
                                            background: 'rgba(var(--accent-warning-rgb), 0.02)',
                                            position: 'relative',
                                            overflow: 'hidden'
                                        }}>
                                            <div style={{
                                                position: 'absolute',
                                                top: 0,
                                                left: 0,
                                                width: '4px',
                                                height: '100%',
                                                background: 'var(--accent-warning)'
                                            }}></div>

                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                                <div>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                                                        <Badge type="warning" style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                                            {alert.type} Anomaly
                                                        </Badge>
                                                        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>ID: {alert.id}</span>
                                                    </div>
                                                    <div style={{ fontWeight: '700', fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                                                        {alert.type === 'Device' && `Device: ${alert.device_id}`}
                                                        {alert.type === 'Identity' && `User: ${alert.uid}`}
                                                        {alert.type === 'Timestamp' && `User: ${alert.uid}`}
                                                    </div>
                                                </div>
                                                {alert.timestamp && (
                                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'right' }}>
                                                        {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                    </div>
                                                )}
                                            </div>

                                            {alert.reasons && alert.reasons.length > 0 && (
                                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                                                    {alert.reasons.map((reason, ridx) => (
                                                        <div key={ridx} style={{
                                                            padding: '0.35rem 0.75rem',
                                                            borderRadius: '8px',
                                                            background: 'rgba(var(--accent-warning-rgb), 0.1)',
                                                            color: 'var(--accent-warning)',
                                                            fontSize: '0.85rem',
                                                            fontWeight: '600',
                                                            border: '1px solid rgba(var(--accent-warning-rgb), 0.1)'
                                                        }}>
                                                            {reason}
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        <section>
                            <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                                <Users size={18} color="var(--accent-primary)" />
                                Attendance Records ({selectedSession.unique_count || 0})
                            </h4>
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
                                gap: '0.75rem',
                                background: 'rgba(0,0,0,0.1)',
                                padding: '1.25rem',
                                borderRadius: '16px',
                                border: '1px solid var(--border-primary)',
                                maxHeight: '320px',
                                overflowY: 'auto'
                            }}>
                                {selectedSession.logs && selectedSession.logs.map((log, idx) => (
                                    <div key={idx} style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        gap: '0.25rem',
                                        padding: '0.6rem 0.8rem',
                                        background: 'var(--bg-secondary)',
                                        borderRadius: '10px',
                                        fontSize: '0.85rem',
                                        border: '1px solid var(--border-primary)',
                                        color: 'var(--text-primary)',
                                        transition: 'transform 0.2s ease'
                                    }} className="hover-lift">
                                        <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{log.uid}</span>
                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.35rem',
                                            color: 'var(--text-secondary)'
                                        }}>
                                            <Clock size={12} color="var(--accent-primary)" />
                                            <span>{log.ts.slice(0, 5)}</span>
                                        </div>
                                    </div>
                                ))}
                                {(!selectedSession.logs || selectedSession.logs.length === 0) && (
                                    <div style={{ gridColumn: '1/-1', textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                                        No student identifiers found for this session.
                                    </div>
                                )}
                            </div>
                        </section>
                    </div>
                ) : (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-danger)' }}>
                        Failed to load session intelligence.
                    </div>
                )}
            </Modal>
        </div>
    );
};


export default Alerts;
