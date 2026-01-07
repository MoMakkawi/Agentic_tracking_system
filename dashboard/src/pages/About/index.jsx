import React from 'react';
import {
    Github,
    GraduationCap,
    Users,
    Code2,
    Server,
    Database,
    Layout,
    GitBranch,
    Mail,
    ExternalLink,
    Info
} from 'lucide-react';
import './About.css';
import PageHeader from '../../components/Common/PageHeader';

const About = () => {
    // Placeholder data - replace with actual values
    const projectInfo = {
        name: "Agentic Tracking System",
        version: "1.0.0",
        description: "An advanced student tracking and monitoring system leveraging agentic AI behaviors to ensure academic integrity and provide real-time insights.",
        university: "University Name",
        universityUrl: "#"
    };

    const team = {
        student: {
            name: "Student Name",
            role: "Frontend Engineer & Researcher",
            github: "https://github.com/yourusername",
            email: "student@university.edu"
        },
        supervisors: [
            { name: "Supervisor Name 1", title: "Project Supervisor" },
            { name: "Supervisor Name 2", title: "Technical Advisor" }
        ]
    };

    const techStack = [
        { icon: Layout, name: "React + Vite", type: "Frontend" },
        { icon: Code2, name: "Modern JavaScript", type: "Language" },
        { icon: Server, name: "Python FastAPI", type: "Backend" },
        { icon: Database, name: "Data Processing", type: "Analytics" }
    ];

    return (
        <div className="about-container fade-in">
            {/* Hero Section */}
            {/* Hero Section */}
            <PageHeader
                title={projectInfo.name}
                icon={Info}
                description={projectInfo.description}
                gradient="linear-gradient(to right, #22d3ee, #67e8f9)"
                iconColor="#22d3ee"
                iconBgColor="rgba(34, 211, 238, 0.1)"
                actions={
                    <div className="version-badge" style={{ alignSelf: 'center', padding: '0.5rem 1rem', background: 'var(--bg-card)', borderRadius: '20px', border: '1px solid var(--border-primary)', fontWeight: '600' }}>
                        v{projectInfo.version}
                    </div>
                }
            />

            <div className="about-grid">
                {/* Team Section */}
                <div className="about-card team-card">
                    <div className="card-header">
                        <Users className="card-icon" />
                        <h2>Project Team</h2>
                    </div>

                    <div className="team-member main-member">
                        <div className="member-avatar">
                            <span className="initials">{team.student.name.charAt(0)}</span>
                        </div>
                        <div className="member-info">
                            <h3>{team.student.name}</h3>
                            <span className="role">{team.student.role}</span>
                            <div className="member-links">
                                <a href={team.student.github} target="_blank" rel="noopener noreferrer" className="link-button">
                                    <Github size={16} /> GitHub
                                </a>
                                <a href={`mailto:${team.student.email}`} className="link-button">
                                    <Mail size={16} /> Contact
                                </a>
                            </div>
                        </div>
                    </div>

                    <div className="supervisors-list">
                        <h3>Supervised By</h3>
                        {team.supervisors.map((sup, index) => (
                            <div key={index} className="supervisor-item">
                                <GraduationCap size={18} className="supervisor-icon" />
                                <div>
                                    <span className="supervisor-name">{sup.name}</span>
                                    <span className="supervisor-title">{sup.title}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Tech Stack & Links */}
                <div className="about-right-column">
                    <div className="about-card tech-card">
                        <div className="card-header">
                            <Code2 className="card-icon" />
                            <h2>Technical Stack</h2>
                        </div>
                        <div className="tech-grid">
                            {techStack.map((tech, index) => (
                                <div key={index} className="tech-item">
                                    <tech.icon size={20} />
                                    <div className="tech-info">
                                        <span className="tech-name">{tech.name}</span>
                                        <span className="tech-type">{tech.type}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="about-card links-card">
                        <div className="card-header">
                            <GitBranch className="card-icon" />
                            <h2>Project Resources</h2>
                        </div>
                        <div className="links-list">
                            <a href={team.student.github} target="_blank" rel="noopener noreferrer" className="resource-link">
                                <Github size={20} />
                                <div>
                                    <span className="link-title">Source Code</span>
                                    <span className="link-desc">View repository on GitHub</span>
                                </div>
                                <ExternalLink size={16} className="arrow-icon" />
                            </a>
                            <a href={projectInfo.universityUrl} target="_blank" rel="noopener noreferrer" className="resource-link">
                                <GraduationCap size={20} />
                                <div>
                                    <span className="link-title">{projectInfo.university}</span>
                                    <span className="link-desc">University details</span>
                                </div>
                                <ExternalLink size={16} className="arrow-icon" />
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
