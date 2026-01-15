import React, { useState, useEffect, useMemo } from 'react';
import { analyticsService } from '../../services/api';
import Card from '../../components/Common/Card';
import PageHeader from '../../components/Common/PageHeader';
import Modal from '../../components/Common/Modal';
import {
    Users,
    User,
    Layers,
    Search,
    ChevronLeft,
    ChevronRight,
    Filter,
    AlertTriangle,
    Zap,
    Cpu,
    Activity,
    Target,
    Calendar
} from 'lucide-react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    Legend
} from 'recharts';
import './Groups.css';

const GroupCard = ({ group, color, onClick }) => (
    <div className="group-card-liquid animate-fade-in"
        onClick={() => onClick(group)}
        style={{ '--card-accent': color, '--card-accent-rgb': color.includes('var') ? (color.includes('success') ? '63, 185, 80' : '88, 166, 255') : (color === '#f59e0b' ? '245, 158, 11' : (color === '#3b82f6' ? '59, 130, 246' : '63, 185, 80')) }}>

        <div className="card-liquid-glow"></div>

        <div className="card-header-pro">
            <div className="title-section">
                <h3 className="group-name-text">{group.name}</h3>
                <span className="pro-status-tag">Cluster</span>
            </div>
            <div className="pro-icon-box">
                <Cpu size={32} strokeWidth={1.5} />
            </div>
        </div>

        <div className="pro-stats-column">
            <div className="pro-stat-info">
                <span className="label">Cohort</span>
                <span className="value">{group.members.length}</span>
            </div>
            <div className="pro-stat-info">
                <span className="label">Sync</span>
                <span className="value" style={{ color: 'var(--card-accent)' }}>{group.avgAttendance || 0}%</span>
            </div>
        </div>

        <div className="attendance-sparkline-integrated">
            <div className="spark-meta">
                <Activity size={12} style={{ marginRight: '0.5rem' }} />
                <span>Continuity Signal</span>
            </div>
            <div style={{ width: '100%', height: 70, marginTop: '0.5rem' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={group.attendanceTrend}>
                        <defs>
                            <linearGradient id={`spark-grad-${group.name.replace(/\s+/g, '-')}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="var(--card-accent)" stopOpacity={0.6} />
                                <stop offset="95%" stopColor="var(--card-accent)" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <Area
                            type="step"
                            dataKey="presence"
                            stroke="var(--card-accent)"
                            strokeWidth={3}
                            fillOpacity={1}
                            fill={`url(#spark-grad-${group.name.replace(/\s+/g, '-')})`}
                            dot={false}
                            isAnimationActive={true}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>

        <div className="avatar-peek">
            {group.members.slice(0, 5).map((m, idx) => (
                <div key={idx} className="peek-avatar" style={{ zIndex: 10 - idx }}>
                    <User size={14} />
                </div>
            ))}
            {group.members.length > 5 && (
                <div className="peek-avatar more" style={{ zIndex: 1 }}>+{group.members.length - 5}</div>
            )}
        </div>
    </div>
);

const Groups = () => {
    const [groups, setGroups] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedGroup, setSelectedGroup] = useState(null);
    const scrollRef = React.useRef(null);

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
        if (!from || !to) { setValidationError('Selection required'); return false; }
        const f = new Date(from), t = new Date(to);
        if (f > t) { setValidationError('Range error'); return false; }
        setValidationError(''); return true;
    };

    const handleInputChange = (field, value) => {
        setInputDateRange(prev => ({ ...prev, [field]: value }));
        validateDates(field === 'from' ? value : inputDateRange.from, field === 'to' ? value : inputDateRange.to);
    };

    const handleFilterClick = () => {
        if (validateDates(inputDateRange.from, inputDateRange.to)) {
            setDateRange(inputDateRange);
        }
    };

    // Check if range spans multiple years
    const showYear = useMemo(() => {
        if (!dateRange.from || !dateRange.to) return false;
        const fromYear = dateRange.from.split('-')[0];
        const toYear = dateRange.to.split('-')[0];
        return fromYear !== toYear;
    }, [dateRange]);

    const formatDateTooltip = (dateStr) => {
        const d = new Date(dateStr);
        // Tooltip can be more verbose, but let's match the requested logic for consistency if desired,
        // or keep it full. User asked for "diagram", usually axis. 
        // Let's make it consistent.
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const year = d.getFullYear();
        return showYear ? `${month}/${day}/${year}` : `${month}/${day}`;
    };

    const formatDateAxis = (dateStr) => {
        const d = new Date(dateStr);
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const year = d.getFullYear();
        return showYear ? `${month}/${day}/${year}` : `${month}/${day}`;
    };

    // Filter
    const filteredGroups = useMemo(() => {
        const term = searchTerm.toLowerCase();
        return groups.filter(g =>
            g.name.toLowerCase().includes(term) || g.members.some(m => m.toLowerCase().includes(term))
        );
    }, [groups, searchTerm]);

    const scroll = (direction) => {
        if (scrollRef.current) {
            const { scrollLeft, clientWidth } = scrollRef.current;
            const scrollTo = direction === 'left' ? scrollLeft - clientWidth * 0.8 : scrollLeft + clientWidth * 0.8;
            scrollRef.current.scrollTo({ left: scrollTo, behavior: 'smooth' });
        }
    };

    return (
        <div className="groups-page animate-fade-in">
            {/* Header */}
            <PageHeader
                title="Clustering Analysis"
                icon={Target}
                description="High-fidelity behavioral segmentation and predictive continuity tracking."
                gradient="linear-gradient(135deg, #10b981 0%, #3b82f6 100%)"
                iconColor="#10b981"
                iconBgColor="rgba(16, 185, 129, 0.05)"
                actions={
                    <div className="search-container" style={{ width: '400px' }}>
                        <Search size={20} style={{ position: 'absolute', left: '1.5rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input
                            type="text"
                            className="search-input"
                            placeholder="Scan neural patterns..."
                            style={{
                                padding: '1.25rem 1.5rem 1.25rem 4rem',
                                background: 'rgba(0,0,0,0.3)',
                                border: '1px solid rgba(255,255,255,0.08)',
                                borderRadius: '20px',
                                fontSize: '1rem'
                            }}
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                        />
                    </div>
                }
            />

            {/* Engagement Chart */}
            <Card
                title="Engagement Matrix"
                subtitle="Comparative cluster dynamics over temporal dimensions."
                className="full-width adaptive-chart-card"
                extra={
                    <div className="vision-date-picker">
                        {validationError && <div className="date-error-message"><AlertTriangle size={12} /> {validationError}</div>}
                        <div className="vision-inputs-row">
                            <div className="vision-date-entry" onClick={(e) => e.target.tagName !== 'INPUT' && document.getElementById('group-date-from').showPicker()}>
                                <Calendar size={14} className="input-icon" />
                                <div className="input-content">
                                    <span className="input-label">From</span>
                                    <input
                                        id="group-date-from"
                                        type="date"
                                        value={inputDateRange.from}
                                        max={new Date().toISOString().split('T')[0]}
                                        className={`date-input ${validationError ? 'error' : ''}`}
                                        onChange={e => handleInputChange('from', e.target.value)}
                                    />
                                </div>
                            </div>
                            <div className="vision-date-entry" onClick={(e) => e.target.tagName !== 'INPUT' && document.getElementById('group-date-to').showPicker()}>
                                <Calendar size={14} className="input-icon" />
                                <div className="input-content">
                                    <span className="input-label">To</span>
                                    <input
                                        id="group-date-to"
                                        type="date"
                                        value={inputDateRange.to}
                                        max={new Date().toISOString().split('T')[0]}
                                        className={`date-input ${validationError ? 'error' : ''}`}
                                        onChange={e => handleInputChange('to', e.target.value)}
                                    />
                                </div>
                            </div>
                            <button className="filter-btn-visionary" onClick={handleFilterClick} disabled={!!validationError}>
                                <Filter size={14} /> <span>Apply Filter</span>
                            </button>
                        </div>
                    </div>
                }
            >
                <div className="chart-wrapper adaptive-chart">
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
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                            <XAxis
                                dataKey="date"
                                tickFormatter={formatDateAxis}
                                stroke="var(--text-secondary)"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                dy={10}
                                minTickGap={30}
                            />
                            <YAxis
                                stroke="var(--text-secondary)"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(val) => `${val}%`}
                            />
                            <RechartsTooltip
                                labelFormatter={formatDateTooltip}
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
                                content={({ payload }) => (
                                    <div style={{
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                                        gap: '1rem',
                                        padding: '1rem 1.5rem 0.5rem 1.5rem',
                                        marginTop: '0.5rem',
                                        maxWidth: '1000px',
                                        margin: '0.5rem auto 0 auto'
                                    }}>
                                        {payload.map((entry, index) => (
                                            <div key={`legend-${index}`} style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '1rem',
                                                padding: '0.75rem 1.25rem',
                                                background: 'rgba(255, 255, 255, 0.02)',
                                                borderRadius: '16px',
                                                border: `1px solid ${entry.color}20`,
                                                transition: 'all 0.3s ease',
                                                backdropFilter: 'blur(5px)'
                                            }}>
                                                <div style={{
                                                    width: '12px',
                                                    height: '12px',
                                                    borderRadius: '4px',
                                                    backgroundColor: entry.color,
                                                    boxShadow: `0 0 12px ${entry.color}`,
                                                    flexShrink: 0
                                                }} />
                                                <span style={{
                                                    fontWeight: 800,
                                                    fontSize: '0.85rem',
                                                    color: '#f0f6fc',
                                                    letterSpacing: '0.03em',
                                                    whiteSpace: 'nowrap'
                                                }}>
                                                    {entry.value}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}
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
            </Card>

            {/* Clusters Browsing */}
            {loading ? (
                <div className="loading-state" style={{ padding: '10rem', textAlign: 'center' }}>
                    <div className="spinner" style={{ width: '60px', height: '60px' }}></div>
                    <p style={{ marginTop: '2rem', color: '#8b949e', fontSize: '1.25rem', fontWeight: 600 }}>Deciphering neural signatures...</p>
                </div>
            ) : (
                <div className="groups-browsing-section">
                    <div className="section-header-pro">
                        <div className="section-title">
                            Identified Clusters
                            <span className="count-badge">{filteredGroups.length}</span>
                        </div>
                        <div className="carousel-controls">
                            <button className="carousel-btn prev" onClick={() => scroll('left')}>
                                <ChevronLeft size={28} />
                            </button>
                            <button className="carousel-btn next" onClick={() => scroll('right')}>
                                <ChevronRight size={28} />
                            </button>
                        </div>
                    </div>

                    <div className="groups-carousel-container" ref={scrollRef}>
                        <div className="groups-horizontal-grid">
                            {filteredGroups.map(group => (
                                <GroupCard
                                    key={group.name}
                                    group={group}
                                    color={groupColors[group.name] || 'var(--page-accent)'}
                                    onClick={setSelectedGroup}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Modal */}
            <Modal isOpen={!!selectedGroup} onClose={() => setSelectedGroup(null)} title={selectedGroup?.name || 'Cluster Insights'}>
                {selectedGroup && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '2rem', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.05)' }}>
                                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 800, textTransform: 'uppercase' }}>COHORT POPULATION</div>
                                <div style={{ fontSize: '3rem', fontWeight: 900 }}>{selectedGroup.members.length}</div>
                            </div>
                            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '2rem', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.05)' }}>
                                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 800, textTransform: 'uppercase' }}>AGGREGATE SYNC</div>
                                <div style={{ fontSize: '3rem', fontWeight: 900, color: '#10b981' }}>{selectedGroup.avgAttendance}%</div>
                            </div>
                        </div>

                        <div>
                            <h4 style={{ marginBottom: '1.5rem', fontSize: '1rem', fontWeight: 800, color: '#f0f6fc', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <Users size={20} />
                                ENROLLED OPERATIVES
                            </h4>
                            <div className="members-grid" style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                                gap: '1rem',
                                maxHeight: '400px',
                                overflowY: 'auto',
                                paddingRight: '1rem'
                            }}>
                                {selectedGroup.members.map(m => (
                                    <div key={m} style={{
                                        background: 'rgba(255,255,255,0.02)',
                                        padding: '1.25rem',
                                        borderRadius: '20px',
                                        border: '1px solid rgba(255,255,255,0.05)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '1rem'
                                    }}>
                                        <div style={{
                                            width: '40px',
                                            height: '40px',
                                            borderRadius: '12px',
                                            background: 'rgba(16, 185, 129, 0.1)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            color: '#10b981'
                                        }}>
                                            <User size={20} />
                                        </div>
                                        <span style={{ fontWeight: 700, color: '#f0f6fc' }}>{m}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default Groups;
