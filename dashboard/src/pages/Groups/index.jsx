import React, { useState, useEffect, useMemo } from 'react';
import { groupService, attendanceService, analyticsService } from '../../services/api';
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
    Calendar,
    Filter,
    AlertTriangle
} from 'lucide-react';
import {
    AreaChart,
    Area,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    Legend
} from 'recharts';
import './Groups.css';

const GroupCard = ({ group, onClick }) => (
    <div className="group-card-premium animate-fade-in" onClick={() => onClick(group)}>
        <div className="card-header">
            <div className="group-info-main">
                <span className="group-tag">Analytics Active</span>
                <h3 className="group-name-text">{group.name}</h3>
            </div>
            <div className="group-icon-box"><Layers size={20} /></div>
        </div>

        <div className="card-visual-stats">
            <div className="stat-mini-item">
                <span className="stat-mini-label">Total Members</span>
                <span className="stat-mini-value">{group.members.length}</span>
            </div>
            <div className="stat-mini-item" style={{ textAlign: 'right' }}>
                <span className="stat-mini-label">Avg. Presence</span>
                <span className="stat-mini-value" style={{ color: 'var(--page-accent)' }}>
                    {group.avgAttendance || 0}%
                </span>
            </div>
        </div>

        <div className="attendance-sparkline" style={{ height: '40px', margin: '0.5rem 0' }}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={group.attendanceTrend}>
                    <defs>
                        <linearGradient id={`spark-grad-${group.name.replace(/\s+/g, '-')}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--page-accent)" stopOpacity={0.2} />
                            <stop offset="95%" stopColor="var(--page-accent)" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <Area
                        type="monotone"
                        dataKey="presence"
                        stroke="var(--page-accent)"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill={`url(#spark-grad-${group.name.replace(/\s+/g, '-')})`}
                        dot={false}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>

        <div className="avatar-group-preview">
            {group.members.slice(0, 4).map((m, idx) => (
                <div key={idx} title={m} className="preview-avatar">
                    <User size={12} />
                </div>
            ))}
            {group.members.length > 4 && (
                <div className="preview-avatar more-count">+{group.members.length - 4}</div>
            )}
        </div>

        <div className="card-action-bar">
            <div className="cohesion-indicator">
                <ArrowRight size={14} color="var(--page-accent)" />
                <span>Dynamic Cluster</span>
            </div>
        </div>
    </div>
);

const Groups = () => {
    const [groups, setGroups] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [page, setPage] = useState(1);
    const [pageSize] = useState(6);
    const [totalPages, setTotalPages] = useState(0);

    const [multiTrendData, setMultiTrendData] = useState([]);
    const [groupColors, setGroupColors] = useState({});

    const [dateRange, setDateRange] = useState(() => {
        const now = new Date();
        const from = new Date();
        from.setMonth(now.getMonth() - 1);
        const formatDate = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
        return { from: formatDate(from), to: formatDate(now) };
    });
    const [inputDateRange, setInputDateRange] = useState(dateRange);
    const [validationError, setValidationError] = useState('');

    // ===== Fetch Data =====
    useEffect(() => { fetchGroups(); }, [dateRange]);

    const fetchGroups = async () => {
        setLoading(true);
        try {
            const res = await analyticsService.getGroupAnalytics({
                received_at_from: dateRange.from,
                received_at_to: dateRange.to
            });
            const { groups: enrichedGroups, multiTrendData: trend, groupColors: colors } = res.data;
            setGroups(enrichedGroups || []);
            setMultiTrendData(trend || []);
            setGroupColors(colors || {});
        } catch (error) {
            console.error(error);
        } finally { setLoading(false); }
    };

    // ===== Date Validation =====
    const validateDates = (from, to) => {
        if (!from || !to) { setValidationError('Both dates are required'); return false; }
        const f = new Date(from), t = new Date(to);
        if (f > t) { setValidationError('From date cannot be after To date'); return false; }
        const oneYearAgo = new Date(); oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        if (f < oneYearAgo) { setValidationError('Cannot query older than 1 year'); return false; }
        setValidationError(''); return true;
    };

    const handleInputChange = (field, value) => {
        setInputDateRange(prev => ({ ...prev, [field]: value }));
        validateDates(field === 'from' ? value : inputDateRange.from, field === 'to' ? value : inputDateRange.to);
    };

    const handleFilterClick = () => {
        if (validateDates(inputDateRange.from, inputDateRange.to)) {
            setDateRange(inputDateRange);
            setPage(1);
        }
    };

    // ===== Conditional Year Display =====
    // Year display based on data range
    const showYear = useMemo(() => {
        const fromYear = dateRange.from.split('-')[0];
        const toYear = dateRange.to.split('-')[0];
        return fromYear !== toYear;
    }, [dateRange]);

    const formatDate = (dateStr) => {
        if (!dateStr || typeof dateStr !== 'string') return dateStr;
        const [year, month, day] = dateStr.split('-');
        return showYear ? `${month}/${day}/${year}` : `${month}/${day}`;
    };

    // Filter & Pagination
    const filteredGroups = useMemo(() => {
        const term = searchTerm.toLowerCase();
        return groups.filter(g =>
            g.name.toLowerCase().includes(term) || g.members.some(m => m.toLowerCase().includes(term))
        );
    }, [groups, searchTerm]);

    useEffect(() => { setTotalPages(Math.ceil(filteredGroups.length / pageSize)); }, [filteredGroups, pageSize]);
    const paginatedGroups = filteredGroups.slice((page - 1) * pageSize, page * pageSize);

    return (
        <div className="groups-page animate-fade-in">
            {/* Header */}
            <PageHeader
                title="Student Intelligence"
                icon={Users}
                description="Advanced clustering analysis for behavioral pattern identification."
                gradient="linear-gradient(to right, #10b981, #059669)"
                iconColor="#10b981"
                iconBgColor="rgba(16, 185, 129, 0.1)"
                actions={   
                    <div className="search-container">
                        <Search size={20} style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input
                            type="text"
                            className="search-input"
                            placeholder="Search groups..."
                            value={searchTerm}
                            onChange={e => { setSearchTerm(e.target.value); setPage(1); }}
                        />
                    </div>
                }
            />

            {/* Attendance Chart */}
            <Card
                title="Group Attendance History (%)"
                subtitle="Comparative presence trends for all identified clusters"
                className="full-width"
                extra={
                    <div className="date-range-picker">
                        {validationError && <div className="date-error-message"><AlertTriangle size={12} /> {validationError}</div>}
                        <div className="date-inputs-row">
                            <div className="premium-date-input">
                                <Calendar size={14} className="input-icon" />
                                <div className="input-content">
                                    <span className="input-label">From</span>
                                    <input type="date" value={inputDateRange.from} className={`date-input ${validationError ? 'error' : ''}`} onChange={e => handleInputChange('from', e.target.value)} />
                                </div>
                            </div>
                            <div className="premium-date-input">
                                <Calendar size={14} className="input-icon" />
                                <div className="input-content">
                                    <span className="input-label">To</span>
                                    <input type="date" value={inputDateRange.to} className={`date-input ${validationError ? 'error' : ''}`} onChange={e => handleInputChange('to', e.target.value)} />
                                </div>
                            </div>
                            <button className="filter-btn-premium" onClick={handleFilterClick} disabled={!!validationError}><Filter size={14} /> Apply Filter</button>
                        </div>
                    </div>
                }
            >
                <div className="chart-wrapper" style={{ height: '400px', marginTop: '1.5rem', position: 'relative' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={multiTrendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                            <defs>
                                {groups.map((g, i) => (
                                    <linearGradient key={`grad-${g.name}`} id={`color-${g.name.replace(/\s+/g, '-')}`} x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={groupColors[g.name]} stopOpacity={0.3} />
                                        <stop offset="95%" stopColor={groupColors[g.name]} stopOpacity={0} />
                                    </linearGradient>
                                ))}
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
                            <XAxis
                                dataKey="date"
                                tickFormatter={formatDate}
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                                dy={15}
                                interval="preserveStartEnd"
                                minTickGap={30}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                                domain={[0, 100]}
                                tickFormatter={(val) => `${val}%`}
                            />
                            <RechartsTooltip
                                labelFormatter={formatDate}
                                contentStyle={{
                                    backgroundColor: 'rgba(13, 17, 23, 0.95)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '12px',
                                    padding: '12px',
                                    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                                    backdropFilter: 'blur(8px)'
                                }}
                                itemStyle={{ padding: '4px 0', fontSize: '13px' }}
                                cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }}
                            />
                            <Legend
                                verticalAlign="bottom"
                                height={40}
                                iconType="circle"
                                wrapperStyle={{ paddingTop: '20px', fontSize: '12px', color: 'var(--text-secondary)' }}
                            />
                            {groups.map(g => (
                                <Area
                                    key={g.name}
                                    type="monotone"
                                    dataKey={g.name}
                                    stroke={groupColors[g.name]}
                                    fillOpacity={1}
                                    fill={`url(#color-${g.name.replace(/\s+/g, '-')})`}
                                    strokeWidth={3}
                                    activeDot={{ r: 6, strokeWidth: 0 }}
                                />
                            ))}
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </Card >

            {/* Loading / Grid */}
            {
                loading ? (
                    <div className="loading-state" style={{ padding: '8rem', textAlign: 'center' }}>
                        <div className="spinner"></div>
                        <p style={{ marginTop: '1.5rem', color: 'var(--text-muted)', fontSize: '1.1rem' }}>Processing neural clusters...</p>
                    </div>
                ) : (
                    <>
                        <div className="groups-grid">
                            {paginatedGroups.map(g => <GroupCard key={g.name} group={g} onClick={setSelectedGroup} />)}
                        </div>
                    </>
                )
            }

            {/* Modal */}
            <Modal isOpen={!!selectedGroup} onClose={() => setSelectedGroup(null)} title={selectedGroup?.name || 'Group Details'}>
                {selectedGroup && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <h3>Members ({selectedGroup.members.length})</h3>
                        <div className="members-grid" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {selectedGroup.members.map(m => (
                                <div key={m} className="member-card">
                                    <User size={20} />
                                    <span>{m}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </Modal>
        </div >
    );
};

export default Groups;
