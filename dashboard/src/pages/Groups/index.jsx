import React, { useState, useEffect, useMemo } from 'react';
import { groupService, attendanceService } from '../../services/api';
import Card from '../../components/Common/Card';
import PageHeader from '../../components/Common/PageHeader';
import Modal from '../../components/Common/Modal';
import {
    Users,
    User,
    ArrowRight,
    Layers,
    Search,
    ChevronLeft,
    ChevronRight,
    PieChart as PieIcon,
    TrendingUp,
    Shield,
    Calendar,
    Filter,
    AlertTriangle
} from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    Cell,
    LineChart,
    Line,
    AreaChart,
    Area,
    Legend
} from 'recharts';
import './Groups.css';

const GroupCard = ({ group, onClick }) => {
    return (
        <div className="group-card-premium animate-fade-in" onClick={() => onClick(group)}>
            <div className="card-header">
                <div className="group-info-main">
                    <span className="group-tag">Analytics Active</span>
                    <h3 className="group-name-text">{group.name}</h3>
                </div>
                <div className="group-icon-box">
                    <Layers size={20} />
                </div>
            </div>

            <div className="card-visual-stats">
                <div className="stat-mini-item">
                    <span className="stat-mini-label">Total Members</span>
                    <span className="stat-mini-value">{group.members.length}</span>
                </div>
                <div className="stat-mini-item" style={{ textAlign: 'right' }}>
                    <span className="stat-mini-label">Avg. Presence</span>
                    <span className="stat-mini-value" style={{ color: 'var(--page-accent)' }}>{group.avgAttendance || 0}%</span>
                </div>
            </div>

            <div className="attendance-sparkline" style={{ height: '40px', margin: '0.5rem 0' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={group.attendanceTrend}>
                        <Line
                            type="monotone"
                            dataKey="presence"
                            stroke="var(--page-accent)"
                            strokeWidth={2}
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="avatar-group-preview">
                {group.members.slice(0, 4).map((m, idx) => (
                    <div key={idx} title={m} className="preview-avatar">
                        <User size={12} />
                    </div>
                ))}
                {group.members.length > 4 && (
                    <div className="preview-avatar more-count">
                        +{group.members.length - 4}
                    </div>
                )}
            </div>

            <div className="card-action-bar">
                <div className="cohesion-indicator">
                    <Shield size={14} color="var(--page-accent)" />
                    <span>Dynamic Cluster</span>
                </div>
                <div className="detail-link-arrow">
                    <ArrowRight size={18} />
                </div>
            </div>
        </div>
    );
};

const Groups = () => {
    const [groups, setGroups] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [showModal, setShowModal] = useState(false);

    // Pagination state
    const [page, setPage] = useState(1);
    const [pageSize] = useState(6); // 6 per page for grid
    const [totalPages, setTotalPages] = useState(0);

    // Date Filtering state (consistent with Overview)
    const [dateRange, setDateRange] = useState(() => {
        const now = new Date();
        const fromDate = new Date();
        fromDate.setDate(now.getDate() - 6);

        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };

        return {
            from: formatDate(fromDate),
            to: formatDate(now)
        };
    });
    const [inputDateRange, setInputDateRange] = useState(dateRange);
    const [validationError, setValidationError] = useState('');

    useEffect(() => {
        fetchGroups();
    }, [dateRange]); // Refetch when date filter committed

    const handleInputChange = (field, value) => {
        const nextRange = { ...inputDateRange, [field]: value };
        setInputDateRange(nextRange);
        validateDates(nextRange.from, nextRange.to);
    };

    const validateDates = (from, to) => {
        if (!from || !to) {
            setValidationError('Both dates are required');
            return false;
        }

        const fromDate = new Date(from);
        const toDate = new Date(to);
        const now = new Date();
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(now.getFullYear() - 1);

        if (fromDate > toDate) {
            setValidationError('From date cannot be after To date');
            return false;
        }

        if (fromDate < oneYearAgo) {
            setValidationError('Cannot query data older than 1 year');
            return false;
        }

        setValidationError('');
        return true;
    };

    const handleFilterClick = () => {
        if (validateDates(inputDateRange.from, inputDateRange.to)) {
            setDateRange(inputDateRange);
            setPage(1);
        }
    };

    const fetchGroups = async () => {
        setLoading(true);
        try {
            const [groupsRes, sessionsRes] = await Promise.all([
                groupService.getGroups(),
                attendanceService.filterSessions({
                    received_at_from: dateRange.from,
                    received_at_to: dateRange.to,
                    page_size: 1000
                })
            ]);
            setGroups(groupsRes.data.items || []);
            setSessions(sessionsRes.data.items || []);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    // Correlation Logic: Attendance analytics for groups
    const groupAnalytics = useMemo(() => {
        if (!groups.length || !sessions.length) return [];

        return groups.map(group => {
            const memberSet = new Set(group.members);

            // Calculate presence per session
            const sessionPresence = sessions.map(session => {
                const presentMembers = session.logs ?
                    session.logs.filter(log => memberSet.has(log.uid)).length : 0;

                return {
                    date: session.logs_date,
                    sessionId: session.session_id,
                    presence: group.members?.length > 0 ? (presentMembers / group.members.length) * 100 : 0
                };
            }).sort((a, b) => new Date(a.date) - new Date(b.date));

            const avgAttendance = sessionPresence.reduce((acc, s) => acc + s.presence, 0) / sessionPresence.length;

            return {
                ...group,
                avgAttendance: Math.round(avgAttendance),
                attendanceTrend: sessionPresence.slice(-10) // Last 10 sessions
            };
        });
    }, [groups, sessions]);

    const activeAnalytics = useMemo(() => {
        return groupAnalytics
            .sort((a, b) => b.avgAttendance - a.avgAttendance)
            .slice(0, 5)
            .map(g => ({
                name: g.name,
                presence: g.avgAttendance
            }));
    }, [groupAnalytics]);

    const multiTrendData = useMemo(() => {
        if (!sessions.length || !groups.length) return [];

        // Derive total unassigned pool from all available session logs
        const allGroupMembers = new Set(groups.flatMap(g => g.members || []));
        const allParticipantUids = new Set();
        sessions.forEach(s => {
            if (s.logs) s.logs.forEach(l => allParticipantUids.add(l.uid));
        });
        const unassignedPool = [...allParticipantUids].filter(uid => !allGroupMembers.has(uid));
        const unassignedPoolSize = unassignedPool.length;

        const dates = [...new Set(sessions.map(s => s.logs_date))].sort();
        return dates.map(date => {
            const daySessions = sessions.filter(s => s.logs_date === date);
            const row = { date };

            groups.forEach(group => {
                const memberSet = new Set(group.members);
                let presentCount = 0;

                daySessions.forEach(s => {
                    if (s.logs) {
                        const presentOnDay = new Set(s.logs.filter(l => memberSet.has(l.uid)).map(l => l.uid));
                        presentCount += presentOnDay.size;
                    }
                });

                const memberCount = group.members?.length || 1;
                const avgPresence = (presentCount / (memberCount * (daySessions.length || 1))) * 100;
                row[group.name] = Math.round(avgPresence);
            });

            // Calculate for Unassigned
            let unassignedPresentCount = 0;
            daySessions.forEach(s => {
                if (s.logs) {
                    const unassignedOnDay = new Set(s.logs.filter(l => !allGroupMembers.has(l.uid)).map(l => l.uid));
                    unassignedPresentCount += unassignedOnDay.size;
                }
            });
            row['Unassigned Users'] = unassignedPoolSize > 0 ? Math.round((unassignedPresentCount / (unassignedPoolSize * (daySessions.length || 1))) * 100) : 0;

            return row;
        });
    }, [groups, sessions]);

    const groupColors = useMemo(() => {
        const colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#f97316'];
        const map = {
            'Unassigned Users': '#ef4444' // Red for unassigned
        };
        groups.forEach((g, i) => {
            map[g.name] = colors[i % colors.length];
        });
        return map;
    }, [groups]);

    const showYear = useMemo(() => {
        if (!sessions.length) return false;
        const years = new Set(sessions.map(s => {
            const dateStr = s.received_at || s.logs_date;
            return dateStr ? dateStr.split('-')[0] : null;
        }).filter(Boolean));
        return years.size > 1;
    }, [sessions]);

    const formatDate = (dateStr) => {
        if (!dateStr || typeof dateStr !== 'string') return dateStr;
        const parts = dateStr.split('-');
        if (parts.length !== 3) return dateStr;
        const [year, month, day] = parts;
        return showYear ? `${month}/${day}/${year}` : `${month}/${day}`;
    };

    // Filter Logic
    const filteredGroups = useMemo(() => {
        return groupAnalytics.filter(group => {
            const searchLower = searchTerm.toLowerCase();
            const matchesName = group.name.toLowerCase().includes(searchLower);
            const matchesMember = group.members.some(member => member.toLowerCase().includes(searchLower));
            return matchesName || matchesMember;
        });
    }, [groupAnalytics, searchTerm]);

    const distributionData = useMemo(() => {
        return activeAnalytics.map((item, idx) => ({
            ...item,
            color: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'][idx % 5]
        }));
    }, [activeAnalytics]);
    useEffect(() => {
        setTotalPages(Math.ceil(filteredGroups.length / pageSize));
        if (page > Math.ceil(filteredGroups.length / pageSize) && page > 1) {
            setPage(1);
        }
    }, [filteredGroups, pageSize, page]);

    const paginatedGroups = filteredGroups.slice(
        (page - 1) * pageSize,
        page * pageSize
    );

    const handleViewComposition = (group) => {
        setSelectedGroup(group);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setSelectedGroup(null);
    };

    return (
        <div className="groups-page animate-fade-in">
            <PageHeader
                title="Student Intelligence"
                icon={Users}
                description="Advanced clustering analysis for behavioral pattern identification."
                gradient="linear-gradient(to right, #10b981, #059669)"
                iconColor="#10b981"
                iconBgColor="rgba(16, 185, 129, 0.1)"
                actions={
                    <div className="search-container">
                        <Search style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} size={20} />
                        <input
                            type="text"
                            placeholder="Search by group or member UID..."
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value);
                                setPage(1);
                            }}
                            className="search-input"
                        />
                    </div>
                }
            />

            <div className="groups-analytics animate-staggered">
                <Card
                    title="Group Attendance History (%)"
                    subtitle="Comparative presence trends for all identified clusters"
                    className="full-width"
                    extra={
                        <div className="date-range-picker">
                            {validationError && (
                                <div className="date-error-message">
                                    <AlertTriangle size={12} /> {validationError}
                                </div>
                            )}
                            <div className="date-inputs-row">
                                <div className="premium-date-input">
                                    <Calendar size={14} className="input-icon" />
                                    <div className="input-content">
                                        <span className="input-label">From</span>
                                        <input
                                            type="date"
                                            className={`date-input ${validationError ? 'error' : ''}`}
                                            value={inputDateRange.from}
                                            onChange={(e) => handleInputChange('from', e.target.value)}
                                        />
                                    </div>
                                </div>
                                <div className="premium-date-input">
                                    <Calendar size={14} className="input-icon" />
                                    <div className="input-content">
                                        <span className="input-label">To</span>
                                        <input
                                            type="date"
                                            className={`date-input ${validationError ? 'error' : ''}`}
                                            value={inputDateRange.to}
                                            onChange={(e) => handleInputChange('to', e.target.value)}
                                        />
                                    </div>
                                </div>
                                <button
                                    className="filter-btn-premium"
                                    onClick={handleFilterClick}
                                    disabled={!!validationError}
                                >
                                    <Filter size={14} />
                                    <span>Apply Filter</span>
                                </button>
                            </div>
                        </div>
                    }
                >
                    <div className="chart-wrapper" style={{ height: '350px', marginTop: '1rem' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                                data={multiTrendData}
                                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                                <XAxis
                                    dataKey="date"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                                    tickFormatter={formatDate}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                                    domain={[0, 100]}
                                />
                                <RechartsTooltip
                                    labelFormatter={formatDate}
                                    contentStyle={{
                                        backgroundColor: 'rgba(22, 27, 34, 0.95)',
                                        border: '1px solid var(--border-primary)',
                                        borderRadius: '12px',
                                        padding: '12px'
                                    }}
                                    itemStyle={{ padding: '2px 0' }}
                                />
                                <Legend
                                    verticalAlign="bottom"
                                    height={36}
                                    content={(props) => {
                                        const { payload } = props;
                                        return (
                                            <div className="chart-legend" style={{ borderTop: 'none', marginTop: '1rem' }}>
                                                {payload.map((entry, index) => (
                                                    <div key={`item-${index}`} className="legend-item">
                                                        <span className="legend-dot" style={{ background: entry.color }}></span>
                                                        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{entry.value}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        );
                                    }}
                                />
                                {groups.map((group) => (
                                    <Line
                                        key={group.name}
                                        type="monotone"
                                        dataKey={group.name}
                                        stroke={groupColors[group.name]}
                                        strokeWidth={4}
                                        dot={{ r: 4, fill: groupColors[group.name], strokeWidth: 0 }}
                                        activeDot={{ r: 6, strokeWidth: 0 }}
                                    />
                                ))}
                                <Line
                                    type="monotone"
                                    dataKey="Unassigned Users"
                                    name="Unassigned"
                                    stroke={groupColors['Unassigned Users']}
                                    strokeWidth={3}
                                    strokeDasharray="5 5"
                                    dot={{ r: 4, fill: groupColors['Unassigned Users'], strokeWidth: 0 }}
                                    activeDot={{ r: 6, strokeWidth: 0 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>

            {loading ? (
                <div className="loading-state" style={{ padding: '8rem', textAlign: 'center' }}>
                    <div className="spinner"></div>
                    <p style={{ marginTop: '1.5rem', color: 'var(--text-muted)', fontSize: '1.1rem' }}>Processing neural clusters...</p>
                </div>
            ) : (
                <>
                    <div className="groups-grid">
                        {paginatedGroups.map((group) => (
                            <GroupCard
                                key={group.name}
                                group={group}
                                onClick={handleViewComposition}
                            />
                        ))}
                    </div>

                    {filteredGroups.length === 0 && (
                        <div className="no-results">
                            <div className="icon-wrapper" style={{ width: '80px', height: '80px', borderRadius: '24px', background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
                                <Search size={40} color="var(--text-muted)" />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', color: 'var(--text-primary)' }}>No results found</h3>
                            <p style={{ color: 'var(--text-muted)' }}>We couldn't find any groups matching "{searchTerm}"</p>
                            <button
                                className="filter-btn"
                                style={{ marginTop: '1.5rem', padding: '0.75rem 2.5rem' }}
                                onClick={() => setSearchTerm('')}
                            >
                                Reset Filters
                            </button>
                        </div>
                    )}

                    <div className="pagination">
                        <button
                            disabled={page === 1}
                            onClick={() => setPage(p => p - 1)}
                            className="icon-btn"
                        >
                            <ChevronLeft size={24} />
                        </button>
                        <div className="page-indicator" style={{ fontSize: '1.1rem' }}>
                            <span style={{ fontWeight: 800, color: 'var(--text-primary)' }}>{page}</span>
                            <span style={{ margin: '0 0.5rem', color: 'var(--text-muted)' }}>/</span>
                            <span style={{ color: 'var(--text-muted)' }}>{totalPages || 1}</span>
                        </div>
                        <button
                            disabled={page === totalPages || totalPages === 0}
                            onClick={() => setPage(p => p + 1)}
                            className="icon-btn"
                        >
                            <ChevronRight size={24} />
                        </button>
                    </div>
                </>
            )}

            <Modal
                isOpen={showModal}
                onClose={closeModal}
                title={selectedGroup ? `Cluster Detail: ${selectedGroup.name}` : 'Group Details'}
            >
                {selectedGroup && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div className="section-title" style={{ margin: 0 }}>
                                <h3>Member Roster ({selectedGroup.members.length})</h3>
                                <div className="line"></div>
                            </div>
                            <div className="group-tag">Highly Stable</div>
                        </div>

                        <div className="members-grid" style={{ maxHeight: '450px', overflowY: 'auto', paddingRight: '0.75rem' }}>
                            {selectedGroup.members.map((member) => (
                                <div key={member} className="member-card">
                                    <div className="member-avatar-placeholder">
                                        <User size={20} />
                                    </div>
                                    <div className="member-details">
                                        <span className="uid">{member}</span>
                                        <span className="member-rank">Identity Verified</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default Groups;
