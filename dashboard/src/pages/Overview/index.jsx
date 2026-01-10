import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { attendanceService, alertService, groupService, chatService, analyticsService } from '../../services/api';
import Card from '../../components/Common/Card';
import PageHeader from '../../components/Common/PageHeader';
import {
    Calendar,
    Filter,
    AlertTriangle,
    Layers,
    TrendingUp,
    ArrowUpRight,
    LayoutDashboard,
    Sparkles,
    Activity,
    Users
} from 'lucide-react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import './Overview.css';

const Overview = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        sessions: 0,
        alerts: 0,
        groups: 0,
        chats: 0,
        loading: true
    });
    const [dateRange, setDateRange] = useState(() => {
        const now = new Date();
        const fromDate = new Date();
        fromDate.setMonth(now.getMonth() - 1);

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
    // Separate state for inputs to allow manual filtering
    const [inputDateRange, setInputDateRange] = useState(dateRange);
    const [validationError, setValidationError] = useState('');


    const [trendData, setTrendData] = useState([]);
    const [alertDistribution, setAlertDistribution] = useState([]);

    useEffect(() => {
        fetchAllData();
    }, []);

    // Only fetch when dateRange (the committed filter) changes
    useEffect(() => {
        fetchTrendData();
    }, [dateRange]);

    const showYear = useMemo(() => {
        const fromYear = dateRange.from ? dateRange.from.split('-')[0] : null;
        const toYear = dateRange.to ? dateRange.to.split('-')[0] : null;
        return fromYear !== toYear;
    }, [dateRange]);

    const formatDate = (isoDate) => {
        if (!isoDate) return '';
        const [year, month, day] = isoDate.split('-');
        return showYear ? `${month}/${day}/${year}` : `${month}/${day}`;
    };

    const validateDates = (from, to) => {
        const fromDate = new Date(from);
        const toDate = new Date(to);
        const today = new Date();
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(today.getFullYear() - 1);

        if (fromDate > toDate) {
            return "Start date cannot be after End date";
        }

        if (fromDate < oneYearAgo || toDate < oneYearAgo) {
            return "Dates cannot be more than 1 year in the past";
        }

        return "";
    };

    const handleInputChange = (type, value) => {
        const newRange = { ...inputDateRange, [type]: value };
        setInputDateRange(newRange);

        // validate immediately on change to provide smart feedback
        const error = validateDates(newRange.from, newRange.to);
        setValidationError(error);
    };

    const handleFilterClick = () => {
        const error = validateDates(inputDateRange.from, inputDateRange.to);
        if (error) {
            setValidationError(error);
            return;
        }
        // Commit the input changes to trigger fetch
        setDateRange(inputDateRange);
        setValidationError('');
    };

    const fetchAllData = async () => {
        setStats(prev => ({ ...prev, loading: true }));
        try {
            // Fetch all required data
            const [sessionsRes, deviceAlertsRes, identityAlertsRes, timestampAlertsRes, groupsRes, chatStatsRes] = await Promise.all([
                attendanceService.getStats(),
                alertService.getDeviceAlerts({ page_size: 5 }),
                alertService.getIdentityAlerts({ page_size: 5 }),
                alertService.getTimestampAlerts({ page_size: 5 }),
                groupService.getGroups({ page_size: 1 }),
                chatService.getStats().catch(() => ({ data: { total_conversations: 0 } }))
            ]);

            // Backend totals for count accuracy
            setStats({
                sessions: sessionsRes.data.total,
                alerts: deviceAlertsRes.data.total + identityAlertsRes.data.total + timestampAlertsRes.data.total,
                groups: groupsRes.data.total,
                chats: chatStatsRes.data.total_conversations,
                loading: false
            });

            // Set alert distribution for charts
            setAlertDistribution([
                { name: 'Device', value: deviceAlertsRes.data.total, color: '#3b82f6' },
                { name: 'Identity', value: identityAlertsRes.data.total, color: '#f59e0b' },
                { name: 'Timestamp', value: timestampAlertsRes.data.total, color: '#ef4444' }
            ]);

            // Consolidate recent alerts for the feed


        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            setStats(prev => ({ ...prev, loading: false }));
        }
    };

    const fetchTrendData = async () => {
        try {
            const res = await analyticsService.getAttendanceTrend({
                received_at_from: dateRange.from,
                received_at_to: dateRange.to
            });
            setTrendData(res.data || []);
        } catch (error) {
            console.error("Error fetching trend data:", error);
            setTrendData([]);
        }
    };


    const statCards = [
        {
            title: 'Monitoring Active',
            value: stats.sessions,
            icon: <Calendar />,
            color: 'primary',
            trend: 'Live',
            desc: 'Total sessions tracked',
            link: '/attendance',
            linkText: 'View Sessions'
        },
        {
            title: 'System Anomalies',
            value: stats.alerts,
            icon: <AlertTriangle />,
            color: 'warning',
            trend: stats.alerts > 0 ? 'Critical' : 'Secure',
            desc: 'Security incidents detected',
            link: '/alerts',
            linkText: 'Show Details'
        },
        {
            title: 'Student Groups',
            value: stats.groups,
            icon: <Users />,
            color: 'success',
            trend: 'Classified',
            desc: 'Pattern-based identifiers',
            link: '/groups',
            linkText: 'View Groups'
        },
        {
            title: 'AI Agent',
            value: stats.chats,
            icon: <Sparkles />,
            color: 'primary',
            trend: 'Online',
            desc: 'Total chat conversations',
            link: '/agent',
            linkText: 'Ask AI'
        },
    ];

    return (
        <div className="overview-container">
            <PageHeader
                title="System Overview"
                icon={Activity}
                description="Real-time insights and monitoring status."
                gradient="linear-gradient(to right, #8b5cf6, #ec4899)"
                iconColor="#8b5cf6"
                iconBgColor="rgba(139, 92, 246, 0.1)"
            />

            <div className="professional-stats-grid">
                {statCards.map((stat, index) => (
                    <div
                        key={index}
                        className={`professional-stat-card ${stat.color} animate-fade-in`}
                        style={{ animationDelay: `${index * 0.1}s`, cursor: 'pointer' }}
                        onClick={() => navigate(stat.link)}
                    >
                        <div className="card-icon-wrapper">
                            {stat.icon}
                        </div>
                        <div className="stat-info-v3">
                            <span className="stat-label-v3">{stat.title}</span>
                            <div className="stat-main-v3">
                                <span className="stat-value-v3">{stats.loading && stat.value !== 'Ready' ? '...' : stat.value}</span>
                                <div className={`stat-trend-v3 ${stat.trend === 'Critical' ? 'down' : 'up'}`}>
                                    {stat.trend === 'Critical' ? <AlertTriangle size={14} /> : <TrendingUp size={14} />}
                                    <span>{stat.trend}</span>
                                </div>
                            </div>
                        </div>
                        <div className="stat-footer-v3">
                            <span className="stat-desc-v3">{stat.desc}</span>
                            <div className="stat-link-v3">
                                {stat.linkText} <ArrowUpRight size={14} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="dashboard-layout">
                <section className="main-charts">
                    <Card
                        title="Attendance Performance"
                        subtitle="Engagement and match rate trends"
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
                        <div className="chart-container" style={{ height: '400px', marginTop: '1.5rem' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorAttendance" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorUnassigned" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                                    <XAxis
                                        dataKey="name"
                                        stroke="var(--text-muted)"
                                        fontSize={11}
                                        tickLine={false}
                                        axisLine={false}
                                        dy={15}
                                        interval="preserveStartEnd"
                                        minTickGap={30}
                                    />
                                    <YAxis
                                        stroke="var(--text-muted)"
                                        fontSize={11}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(val) => `${val}`}
                                    />
                                    <RechartsTooltip
                                        labelFormatter={(label, payload) => {
                                            if (payload && payload.length > 0 && payload[0].payload.fullDate) {
                                                return formatDate(payload[0].payload.fullDate);
                                            }
                                            return label;
                                        }}
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
                                    <Area
                                        type="monotone"
                                        dataKey="attendance"
                                        name="Total Attendance"
                                        stroke="#3b82f6"
                                        fillOpacity={1}
                                        fill="url(#colorAttendance)"
                                        strokeWidth={3}
                                        activeDot={{ r: 6, strokeWidth: 0 }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="unassigned"
                                        name="Unassigned Users"
                                        stroke="#ef4444"
                                        fillOpacity={1}
                                        fill="url(#colorUnassigned)"
                                        strokeWidth={3}
                                        activeDot={{ r: 6, strokeWidth: 0 }}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                            <div className="chart-legend" style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '24px' }}>
                                <div className="legend-item" style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <span className="legend-dot" style={{ background: '#3b82f6', width: '10px', height: '10px', borderRadius: '50%' }}></span>
                                    <span>Daily Total Attendance (Unique)</span>
                                </div>
                                <div className="legend-item" style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <span className="legend-dot" style={{ background: '#ef4444', width: '10px', height: '10px', borderRadius: '50%' }}></span>
                                    <span>Unassigned Users</span>
                                </div>
                            </div>
                        </div>
                    </Card>



                    <Card title="Alert Distribution" subtitle="Composition by error type">
                        <div className="pie-chart-container">
                            <ResponsiveContainer width="100%" height={200}>
                                <PieChart>
                                    <Pie
                                        data={alertDistribution}
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {alertDistribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <RechartsTooltip />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="pie-legend">
                                {alertDistribution.map(item => (
                                    <div key={item.name} className="legend-item">
                                        <div className="dot" style={{ backgroundColor: item.color }}></div>
                                        <span>{item.name}: <strong>{item.value}</strong></span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </Card>
                </section >


            </div >
        </div >
    );
};

export default Overview;
