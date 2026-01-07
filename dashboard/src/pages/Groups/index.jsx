import React, { useState, useEffect } from 'react';
import { groupService } from '../../services/api'; // Ensure this service exists and works
import Card from '../../components/Common/Card';
import Modal from '../../components/Common/Modal';
import { Users, User, ArrowRight, Layers, Search, Filter, ChevronLeft, ChevronRight, LayoutGrid } from 'lucide-react';
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

    return (
        <div className="groups-page animate-fade-in">
            <div className="page-header">
                <div>
                    <h1>
                        Student Groupings
                    </h1>
                    <p>
                        Identified clusters of students based on attendance patterns.
                    </p>
                </div>

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
            </div>

            <Card
                className="glass overflow-hidden"
                style={{ padding: '0', border: '1px solid var(--border-primary)', display: 'flex', flexDirection: 'column', height: '100%' }}
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
                        {paginatedGroups.length > 0 ? (
                            <div className="groups-grid">
                                {paginatedGroups.map((group, index) => (
                                    <div
                                        key={index}
                                        className="group-card glass"
                                    >
                                        <div style={{ padding: '1.25rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', margin: 0 }}>{group.name}</h3>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                    <Users size={14} />
                                                    {group.members.length}
                                                </div>
                                            </div>

                                            <div className="member-list">
                                                {group.members.slice(0, 3).map((member, mIdx) => (
                                                    <div key={mIdx} className="member-item">
                                                        <User size={14} className="member-icon" />
                                                        <span className="truncate">{member}</span>
                                                    </div>
                                                ))}
                                                {group.members.length > 3 && (
                                                    <div className="more-members">
                                                        +{group.members.length - 3} others
                                                    </div>
                                                )}
                                            </div>

                                            <button
                                                className="view-detail-btn"
                                                onClick={() => handleViewComposition(group)}
                                            >
                                                View Composition <ArrowRight size={16} />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
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
