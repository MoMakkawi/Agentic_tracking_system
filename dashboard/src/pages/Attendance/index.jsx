import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { attendanceService, groupService } from '../../services/api';
import Card from '../../components/Common/Card';
import Table from '../../components/Common/Table';
import Badge from '../../components/Common/Badge';
import Modal from '../../components/Common/Modal';
import './Attendance.css';
import {
    Calendar, Users, Hash, Clock, Filter,
    ChevronLeft, ChevronRight, AlertCircle,
    CheckCircle2, AlertTriangle, Shield,
    User, Info, Bookmark, TrendingUp, ArrowRight, Layers, Sparkles, ShieldCheck
} from 'lucide-react';

const Attendance = () => {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [pageSize] = useState(10);
    const [total, setTotal] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [sortConfig, setSortConfig] = useState({ key: 'received_at', direction: 'desc' });
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedSession, setSelectedSession] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [activeFilter, setActiveFilter] = useState('all'); // 'all', 'alerts'
    const [stats, setStats] = useState({ total: 0, with_alerts: 0 });
    const [groupsCount, setGroupsCount] = useState(0);

    useEffect(() => {
        fetchStats();
    }, []);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            fetchSessions();
        }, 300);
        return () => clearTimeout(timeoutId);
    }, [page, sortConfig, searchTerm, activeFilter]);

    const fetchStats = async () => {
        try {
            const [statsRes, groupsRes] = await Promise.all([
                attendanceService.getStats(),
                groupService.getGroups({ page_size: 1 })
            ]);
            setStats(statsRes.data);
            setGroupsCount(groupsRes.data.total);
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
        }
    };

    const fetchSessions = async () => {
        setLoading(true);
        try {
            const params = {
                page,
                page_size: pageSize,
                order_by: sortConfig.key,
                order_direction: sortConfig.direction,
            };

            if (searchTerm) {
                params.search = searchTerm;
            }

            if (activeFilter === 'alerts') {
                params.has_alerts = true;
            }

            const response = await attendanceService.filterSessions(params);
            setSessions(response.data.items);
            setTotal(response.data.total);
            setTotalPages(response.data.total_pages);
        } catch (error) {
            console.error('Error fetching sessions:', error);
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

    const handleRowClick = (session) => {
        setSelectedSession(session);
        setIsModalOpen(true);
    };

    const toggleFilter = (filter) => {
        if (activeFilter === filter) {
            setActiveFilter('all');
        } else {
            setActiveFilter(filter);
        }
        setPage(1);
    };

    const columns = [
        {
            title: 'Session ID',
            key: 'session_id',
            render: (val) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Hash size={14} color="var(--accent-primary)" />
                    <Badge type="info" style={{ fontWeight: '700' }}>{val}</Badge>
                </div>
            )
        },
        {
            title: 'Context',
            key: 'session_context',
            render: (val) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', maxWidth: '200px' }}>
                    <Info size={14} color='var(--text-secondary)' style={{ flexShrink: 0 }} />
                    <span className="truncate" title={val} style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                        {val || 'Unknown'}
                    </span>
                </div>
            )
        },
        {
            title: 'Date',
            key: 'received_at',
            render: (val) => {
                if (!val) return '-';
                const date = new Date(val);

                return (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: '600' }}>
                            <Calendar size={13} color="var(--accent-primary)" />
                            {date.toLocaleDateString('fr-FR', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit'
                            })}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            <Clock size={12} color="var(--accent-primary)" />
                            {date.toLocaleTimeString('fr-FR', {
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: false
                            })}
                        </div>
                    </div>
                );
            }
        },
        {
            title: 'Attendance',
            key: 'unique_count',
            render: (val) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Users size={14} color={val > 50 ? 'var(--accent-success)' : 'var(--text-secondary)'} />
                    {val}
                </div>
            )
        },
        {
            title: 'Alerts',
            key: 'alert_count',
            render: (val) => (
                <div
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                        color: val > 50 ? 'var(--accent-warning)' : 'var(--accent-success)',
                        fontSize: '0.85rem',
                    }}
                >
                    {val > 0 ? (
                        <>
                            <AlertCircle size={14} color="var(--accent-warning)" />
                            <span>{val}</span>
                        </>
                    ) : (
                        <>
                            <CheckCircle2 size={14} color="var(--accent-success)" />
                            <span>Secure</span>
                        </>
                    )}
                </div>
            )
        }
    ];

    return (
        <div className="attendance-page animate-fade-in">
            <div className="page-header" style={{ marginBottom: '3rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem', background: 'linear-gradient(to right, var(--text-primary), var(--accent-primary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontWeight: '800' }}>
                        Attendance Insights
                    </h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>
                        Monitor session participation and system health anomalies.
                    </p>
                </div>

                <div className="search-container" style={{ position: 'relative' }}>
                    <Filter style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} size={20} />
                    <input
                        type="text"
                        placeholder="Search sessions..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
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

            <div className="attendance-content-header" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button
                            className={`filter-tab ${activeFilter === 'all' ? 'active' : ''}`}
                            onClick={() => setActiveFilter('all')}
                        >
                            All Sessions
                        </button>
                        <button
                            className={`filter-tab ${activeFilter === 'alerts' ? 'active' : ''}`}
                            onClick={() => toggleFilter('alerts')}
                        >
                            <AlertCircle size={14} /> Critical Only
                        </button>
                    </div>
                </div>
            </div>

            <Card
                className="glass overflow-hidden"
                style={{ padding: '0', border: '1px solid var(--border-primary)' }}
                title="Attendance Sessions"
                subtitle={`Total ${total} records found`}
                extra={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-success)', fontSize: '0.9rem', fontWeight: '600' }}>
                        <ShieldCheck size={18} />
                        Live Monitoring
                    </div>
                }
            >
                <Table
                    columns={columns}
                    data={sessions}
                    loading={loading}
                    onSort={handleSort}
                    sortConfig={sortConfig}
                    onRowClick={handleRowClick}
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
                title={`Session Details #${selectedSession?.session_id}`}
            >
                {selectedSession && (
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

                                            {alert.type === 'Identity' && alert.repeated_anomaly_count > 0 && (
                                                <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                    <AlertTriangle size={14} />
                                                    <span>Repeated anomalies: <strong>{alert.repeated_anomaly_count}</strong> times</span>
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
                                Attendance Records ({selectedSession.unique_count})
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
                )}
            </Modal>
        </div>
    );
};


export default Attendance;
