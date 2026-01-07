import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { attendanceService, alertService, groupService } from '../../services/api';
import Card from '../../components/Common/Card';
import {
    Calendar,
    AlertTriangle,
    Layers,
    TrendingUp,
    ArrowUpRight,
    Sparkles
} from 'lucide-react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
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
        loading: true
    });
    const [dateRange, setDateRange] = useState({
        from: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        to: new Date().toISOString().split('T')[0]
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
            const [sessionsRes, deviceAlertsRes, identityAlertsRes, timestampAlertsRes, groupsRes] = await Promise.all([
                attendanceService.getStats(), // Use dedicated stats endpoint if available or just get totals
                alertService.getDeviceAlerts({ page_size: 5 }),
                alertService.getIdentityAlerts({ page_size: 5 }),
                alertService.getTimestampAlerts({ page_size: 5 }),
                groupService.getGroups({ page_size: 1 }) // Just for total
            ]);

            // Backend totals for count accuracy
            setStats({
                sessions: sessionsRes.data.total,
                alerts: deviceAlertsRes.data.total + identityAlertsRes.data.total + timestampAlertsRes.data.total,
                groups: groupsRes.data.total,
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
            const sessionsRes = await attendanceService.filterSessions({
                received_at_from: dateRange.from,
                received_at_to: dateRange.to,
                page_size: 1000
            });

            const filteredSessions = sessionsRes.data.items || [];

            // Generate labels for each day in the range
            const days = [];
            const startDate = new Date(dateRange.from + 'T00:00:00');
            const endDate = new Date(dateRange.to + 'T00:00:00');

            const oneDay = 24 * 60 * 60 * 1000;
            for (let ts = startDate.getTime(); ts <= endDate.getTime(); ts += oneDay) {
                const d = new Date(ts);
                const isoDate = d.toISOString().split('T')[0];
                days.push(isoDate);
            }

            const trend = days.map(isoDate => {
                const daySessions = filteredSessions.filter(s => {
                    const sessionDate = s.received_at || s.logs_date;
                    if (!sessionDate) return false;
                    return sessionDate.startsWith(isoDate);
                });

                // Sum up attendance metrics for all sessions in this day
                const totalAttendance = daySessions.reduce((sum, s) => sum + (s.unique_count || 0), 0);
                const totalRecorded = daySessions.reduce((sum, s) => sum + (s.recorded_count || 0), 0);
                const sessionCount = daySessions.length;

                const [year, month, day] = isoDate.split('-');
                const displayLabel = `${day}/${month}`;

                return {
                    name: displayLabel,
                    attendance: totalAttendance,
                    recorded: totalRecorded,
                    sessions: sessionCount
                };
            });

            setTrendData(trend);
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
            icon: <Layers />,
            color: 'success',
            trend: 'Classified',
            desc: 'Pattern-based identifiers',
            link: '/groups',
            linkText: 'View Groups'
        },
        {
            title: 'AI Agent',
            value: 'Ready',
            icon: <Sparkles />,
            color: 'primary',
            trend: 'Online',
            desc: 'Ask Agent for insights',
            link: '/agent',
            linkText: 'Ask AI'
        },
    ];

    return (
        <div className="overview-container">
            <header className="overview-header v2">
                <div className="header-main">
                    <div className="header-info">
                        <h1>System Dashboard</h1>
                        <p>Overview of the Tracking System</p>
                    </div>

                </div>
            </header>

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
                                    <div className="date-input-group">
                                        <span className="date-label">From:</span>
                                        <input
                                            type="date"
                                            className={`date-input ${validationError ? 'error' : ''}`}
                                            value={inputDateRange.from}
                                            onChange={(e) => handleInputChange('from', e.target.value)}
                                        />
                                    </div>
                                    <div className="date-input-group">
                                        <span className="date-label">To:</span>
                                        <input
                                            type="date"
                                            className={`date-input ${validationError ? 'error' : ''}`}
                                            value={inputDateRange.to}
                                            onChange={(e) => handleInputChange('to', e.target.value)}
                                        />
                                    </div>
                                    <button
                                        className="filter-btn"
                                        onClick={handleFilterClick}
                                        disabled={!!validationError}
                                    >
                                        Filter
                                    </button>
                                </div>
                            </div>
                        }
                    >
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={trendData}>
                                    <defs>
                                        <linearGradient id="colorAttendance" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                    <XAxis dataKey="name" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1a1b1e', border: 'none', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }}
                                        itemStyle={{ color: '#fff' }}
                                        formatter={(value) => [value, 'Participants']}
                                    />
                                    <Area type="monotone" dataKey="attendance" name="attendance" stroke="#3b82f6" fillOpacity={1} fill="url(#colorAttendance)" strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                            <div className="chart-legend">
                                <div className="legend-item"><span className="legend-dot" style={{ background: '#3b82f6' }}></span> Participants</div>
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
                                    <Tooltip />
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
