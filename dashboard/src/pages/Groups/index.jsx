import React, { useState, useEffect } from 'react';
import { groupService } from '../../services/api'; // Ensure this service exists and works
import Card from '../../components/Common/Card';
import PageHeader from '../../components/Common/PageHeader';
import Modal from '../../components/Common/Modal';
import { Users, User, ArrowRight, Layers, Search, Filter, ChevronLeft, ChevronRight, LayoutGrid, Info } from 'lucide-react';
import Table from '../../components/Common/Table';
import Badge from '../../components/Common/Badge';
import './Groups.css';

const Groups = () => {
    const [groups, setGroups] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [showModal, setShowModal] = useState(false);

    // Pagination state
    const [page, setPage] = useState(1);
    const [pageSize] = useState(10);
    const [totalPages, setTotalPages] = useState(0);

    useEffect(() => {
        fetchGroups();
    }, []);

    const fetchGroups = async () => {
        setLoading(true);
        try {
            const response = await groupService.getGroups();
            // Assuming response.data.items is the list of groups
            // If the API supports server-side pagination, we should use it. 
            // Based on previous analysis, we'll do client-side pagination for now or if API returns all.
            setGroups(response.data.items);
            // setTotal(response.data.total); // If needed
        } catch (error) {
            console.error('Error fetching groups:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleViewComposition = (group) => {
        setSelectedGroup(group);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setSelectedGroup(null);
    };

    // Filter Logic
    const filteredGroups = groups.filter(group => {
        const searchLower = searchTerm.toLowerCase();
        const matchesName = group.name.toLowerCase().includes(searchLower);
        const matchesMember = group.members.some(member => member.toLowerCase().includes(searchLower));
        return matchesName || matchesMember;
    });

    // Pagination Logic
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

    const columns = [
        {
            title: 'Group Name',
            key: 'name',
            render: (val) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Layers size={16} color="var(--accent-success)" />
                    <span style={{ fontWeight: '700', fontSize: '1rem' }}>{val}</span>
                </div>
            )
        },
        {
            title: 'Members',
            key: 'members',
            render: (members) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Users size={14} color="var(--text-secondary)" />
                    <Badge type="info">{members.length} Identifiers</Badge>
                </div>
            )
        },
        {
            title: 'Composition Preview',
            key: 'members',
            sortable: false,
            render: (members) => (
                <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', maxWidth: '400px' }}>
                    {members.slice(0, 3).map((m, idx) => (
                        <div key={idx} style={{
                            fontSize: '0.8rem',
                            padding: '0.2rem 0.5rem',
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '4px',
                            color: 'var(--text-secondary)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem'
                        }}>
                            <User size={10} />
                            {m}
                        </div>
                    ))}
                    {members.length > 3 && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>+{members.length - 3} more</span>}
                </div>
            )
        },
        {
            title: 'Actions',
            key: 'actions',
            sortable: false,
            render: (_, group) => (
                <button
                    className="view-detail-btn"
                    style={{ marginTop: 0, padding: '0.5rem 1rem', width: 'auto' }}
                    onClick={(e) => {
                        e.stopPropagation();
                        handleViewComposition(group);
                    }}
                >
                    Details <ArrowRight size={14} />
                </button>
            )
        }
    ];

    return (
        <div className="groups-page animate-fade-in">
            <PageHeader
                title="Student Groupings"
                icon={Users}
                description="Identified clusters of students based on attendance patterns."
                gradient="linear-gradient(to right, #10b981, #34d399)"
                iconColor="#10b981"
                iconBgColor="rgba(16, 185, 129, 0.1)"
                actions={
                    <div className="search-container">
                        <Filter style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} size={20} />
                        <input
                            type="text"
                            placeholder="Search groups..."
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value);
                                setPage(1); // Reset to page 1 on search
                            }}
                            className="search-input"
                        />
                    </div>
                }
            />

            <Card
                className="glass overflow-hidden"
                style={{ padding: '0', border: '1px solid var(--border-primary)', display: 'flex', flexDirection: 'column', height: '100%' }}
                theme="success"
                title="Active Groups"
                subtitle={`Total ${filteredGroups.length} groups found`}
                extra={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', fontSize: '0.9rem', fontWeight: '600' }}>
                        <LayoutGrid size={18} />
                        Clustering Active
                    </div>
                }
            >
                {loading ? (
                    <div className="loading-state" style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                        Loading groups...
                    </div>
                ) : (
                    <>
                        <Table
                            columns={columns}
                            data={paginatedGroups}
                            loading={loading}
                            onRowClick={handleViewComposition}
                        />

                        {paginatedGroups.length === 0 && (
                            <div className="no-results">
                                <Search size={48} />
                                <p style={{ fontSize: '1.1rem' }}>No groups found for "{searchTerm}"</p>
                                <button
                                    className="view-detail-btn"
                                    style={{ width: 'auto', padding: '0.75rem 2rem' }}
                                    onClick={() => setSearchTerm('')}
                                >
                                    Clear Search
                                </button>
                            </div>
                        )}

                        <div className="pagination">
                            <button
                                disabled={page === 1}
                                onClick={() => setPage(p => p - 1)}
                                className={`icon-btn hover-lift ${page === 1 ? 'disabled' : ''}`}
                            >
                                <ChevronLeft size={20} />
                            </button>
                            <div className="page-indicator">
                                Page <span className="current-page">{page}</span> of <span className="total-pages">{totalPages || 1}</span>
                            </div>
                            <button
                                disabled={page === totalPages || totalPages === 0}
                                onClick={() => setPage(p => p + 1)}
                                className={`icon-btn hover-lift ${page === totalPages || totalPages === 0 ? 'disabled' : ''}`}
                            >
                                <ChevronRight size={20} />
                            </button>
                        </div>
                    </>
                )}
            </Card>

            <Modal
                isOpen={showModal}
                onClose={closeModal}
                title={selectedGroup ? selectedGroup.name : 'Group Details'}
            >
                {selectedGroup && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <div className="section-title">
                            <h3>Member Composition ({selectedGroup.members.length})</h3>
                            <div className="line"></div>
                        </div>

                        <div className="members-grid" style={{ maxHeight: '400px', overflowY: 'auto', paddingRight: '0.5rem' }}>
                            {selectedGroup.members.map((member, idx) => (
                                <div key={idx} className="member-card glass hover-lift">
                                    <div className="member-avatar-placeholder">
                                        <User size={18} />
                                    </div>
                                    <div className="member-details">
                                        <span className="uid">{member}</span>
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
