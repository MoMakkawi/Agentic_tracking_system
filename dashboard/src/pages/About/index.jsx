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
    Info,
    Smartphone,
    Cpu,
    Sparkles,
    ShieldCheck,
    ChevronRight
} from 'lucide-react';
import './About.css';
import PageHeader from '../../components/Common/PageHeader';
import Card from '../../components/Common/Card';

const About = () => {
    const projectInfo = {
        name: "Agentic Tracking System",
        version: "1.0.0",
        description: "An advanced student tracking and monitoring system leveraging agentic AI behaviors to ensure academic integrity and provide deep insights.",
        university: "IMT Atlantique",
        universityUrl: "https://www.imt-atlantique.fr/fr"
    };

    const team = {
        student: {
            name: "Mohamad Faraj MAKKAWI",
            role: "Software Engineer",
            github: "https://github.com/MoMakkawi",
            email: "MoMakkawi@hotmail.com"
        },
        supervisors: [
            { name: "Laurent TOUTAIN", title: "IoT Professor" },
            { name: "Baptiste GAULTIER", title: "Research Support Engineer" }
        ]
    };

    const techStack = [
        { icon: Layout, name: "React 18", type: "Framework", color: "#61DAFB" },
        { icon: Cpu, name: "FastAPI", type: "Backend", color: "#009688" },
        { icon: Database, name: "SmolAgents", type: "AI Engine", color: "#FF9800" },
        { icon: Code2, name: "Python DSL", type: "Language", color: "#3776AB" },
        { icon: Server, name: "Vite", type: "Build Tool", color: "#646CFF" },
        { icon: Smartphone, name: "IoT Integration", type: "Hardware", color: "#4CAF50" }
    ];

    return (
        <div className="about-page animate-fade-in">
            <PageHeader
                title="System Intelligence"
                icon={Info}
                description="Behind the scenes of the Agentic Tracking System."
                gradient="linear-gradient(to right, var(--accent-primary), var(--accent-success))"
                iconColor="var(--accent-primary)"
                iconBgColor="rgba(var(--accent-primary-rgb), 0.1)"
                actions={
                    <div className="badge-premium" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>
                        Version {projectInfo.version}
                    </div>
                }
            />

            <div className="about-layout">
                {/* Left Column: Team & Bio */}
                <div className="about-left">
                    <div className="profile-card">
                        <div className="profile-avatar-wrapper">
                            <div className="profile-avatar">
                                <Users size={48} color="var(--accent-primary)" />
                            </div>
                        </div>
                        <div className="profile-info">
                            <span className="role">IT Engineer</span>
                            <h2>{team.student.name}</h2>
                            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
                                <a href={team.student.github} target="_blank" rel="noopener noreferrer" className="icon-btn" style={{ width: '40px', height: '40px' }}>
                                    <Github size={18} />
                                </a>
                                <a href={`mailto:${team.student.email}`} className="icon-btn" style={{ width: '40px', height: '40px' }}>
                                    <Mail size={18} />
                                </a>
                            </div>
                        </div>
                        <Sparkles size={120} style={{ position: 'absolute', right: '-20px', top: '-20px', opacity: 0.03, pointerEvents: 'none' }} />
                    </div>

                    <Card title="Project Foundation" subtitle="Supervision and Academic Context">
                        <div className="details-scrollable">
                            {team.supervisors.map((sup, index) => (
                                <div key={index} className="supervisor-pro-card">
                                    <div className="supervisor-icon-box">
                                        <GraduationCap size={24} />
                                    </div>
                                    <div className="supervisor-pro-info">
                                        <span className="name">{sup.name}</span>
                                        <span className="title">{sup.title}</span>
                                    </div>
                                </div>
                            ))}

                            <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(var(--accent-primary-rgb), 0.05)', borderRadius: '16px', border: '1px solid rgba(var(--accent-primary-rgb), 0.1)' }}>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                                    Developed as a specialized research project at <strong>{projectInfo.university}</strong>, focusing on the intersection of IoT data and Agentic AI behaviors.
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Right Column: Tech & Resources */}
                <div className="about-right">
                    <Card title="Technology Matrix" subtitle="The core architecture fuels the agent's logic">
                        <div className="tech-grid-premium">
                            {techStack.map((tech, index) => (
                                <div key={index} className="tech-card-pro">
                                    <div className="tech-icon-box" style={{ color: tech.color }}>
                                        <tech.icon size={20} />
                                    </div>
                                    <div className="stack-item-info">
                                        <span className="stack-label">{tech.type}</span>
                                        <span className="stack-name">{tech.name}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>

                    <Card title="Open Intelligence" subtitle="Access repository and documentation">
                        <div className="resources-grid">
                            <a href="https://github.com/MoMakkawi/Agentic_tracking_system" target="_blank" rel="noopener noreferrer" className="resource-pro-link">
                                <GitBranch size={24} color="var(--accent-primary)" />
                                <div className="resource-content">
                                    <span className="title">Main Repository</span>
                                    <span className="desc">Explore the core source code on GitHub</span>
                                </div>
                                <ChevronRight size={18} className="arrow-icon-pro" />
                            </a>
                            <a href={projectInfo.universityUrl} target="_blank" rel="noopener noreferrer" className="resource-pro-link">
                                <ShieldCheck size={24} color="var(--accent-success)" />
                                <div className="resource-content">
                                    <span className="title">Academic Partner</span>
                                    <span className="desc">Vist IMT Atlantique University profile</span>
                                </div>
                                <ChevronRight size={18} className="arrow-icon-pro" />
                            </a>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default About;
