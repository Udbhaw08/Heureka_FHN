import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GridPlus from './GridPlus';
import { api } from '../api/backend';

// Preview data — used when no company session or no real cases exist
const PREVIEW_QUEUE = [
    {
        id: 'PRV-1',
        application_id: 101,
        job_id: 5,
        role: 'Senior Frontend Engineer',
        candidate_anon_id: 'ANON-X7F29A3B1C',
        severity: 'high',
        reason: 'Bias loop stuck after 4 re-evaluations — GitHub evidence conflicts with resume claims on React expertise',
        status: 'pending',
        triggered_by: 'bias_agent',
        created_at: new Date().toISOString(),
        skills: ['React', 'TypeScript', 'Node.js', 'GraphQL', 'AWS'],
        evidence_sources: ['GITHUB', 'ATS', 'RESUME'],
        confidence: 72,
        match_score: 68,
        evidence_json: {
            manipulation: { severity: 'medium', flags: ['commit_frequency_spike', 'repo_freshness_anomaly'] },
            integrity_check: { discrepancy_detected: true, type: 'skill_inflation' },
            ats_semantic_flags: ['keyword_stuffing_detected']
        },
        feedback: { message: 'Under review' }
    },
    {
        id: 'PRV-2',
        application_id: 102,
        job_id: 5,
        role: 'Backend Systems Engineer',
        candidate_anon_id: 'ANON-B2K8Z4M1P',
        severity: 'critical',
        reason: 'Resume manipulation detected — claimed contributions to open-source repos do not exist',
        status: 'pending',
        triggered_by: 'skill_agent',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        skills: ['Python', 'Django', 'PostgreSQL', 'Docker'],
        evidence_sources: ['GITHUB', 'LINKEDIN', 'ATS'],
        confidence: 34,
        match_score: 41,
        evidence_json: {
            manipulation: { severity: 'critical', flags: ['fabricated_repos', 'identity_mismatch'] },
            integrity_check: { discrepancy_detected: true, type: 'fabricated_evidence' },
            ats_semantic_flags: ['experience_inflation', 'role_mismatch']
        },
        feedback: { message: 'Under review' }
    },
    {
        id: 'PRV-3',
        application_id: 103,
        job_id: 8,
        role: 'ML / Data Engineer',
        candidate_anon_id: 'ANON-C9D4E7F2Q',
        severity: 'medium',
        reason: 'Skill verification ambiguity — TensorFlow usage claimed but only tutorial-level repos found',
        status: 'pending',
        triggered_by: 'bias_agent',
        created_at: new Date(Date.now() - 7200000).toISOString(),
        skills: ['Python', 'TensorFlow', 'SQL', 'Pandas', 'NumPy'],
        evidence_sources: ['GITHUB', 'RESUME'],
        confidence: 55,
        match_score: 52,
        evidence_json: {
            manipulation: { severity: 'low', flags: ['skill_depth_uncertain'] },
            integrity_check: { discrepancy_detected: false },
            ats_semantic_flags: []
        },
        feedback: { message: 'Under review' }
    }
];

export default function ReviewerExperience({ onExit }) {
    const [queue, setQueue] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isPreview, setIsPreview] = useState(false);
    const [activePage, setActivePage] = useState('dashboard');
    const [selectedCase, setSelectedCase] = useState(null);
    const [actionLoading, setActionLoading] = useState(null);

    const companyId = localStorage.getItem("fhn_company_id") || "";

    useEffect(() => {
        (async () => {
            try {
                if (companyId) {
                    const data = await api.reviewQueue(companyId);
                    const realCases = Array.isArray(data) ? data : [];
                    if (realCases.length > 0) {
                        setQueue(realCases);
                        setIsPreview(false);
                    } else {
                        setQueue(PREVIEW_QUEUE);
                        setIsPreview(true);
                    }
                } else {
                    setQueue(PREVIEW_QUEUE);
                    setIsPreview(true);
                }
            } catch (e) {
                console.warn("Failed to load review queue, using preview data", e);
                setQueue(PREVIEW_QUEUE);
                setIsPreview(true);
            } finally {
                setIsLoading(false);
            }
        })();
    }, [companyId]);

    const handleReview = (item) => {
        setSelectedCase(item);
        setActivePage('review');
    };

    const handleAction = async (action) => {
        if (!selectedCase) return;
        setActionLoading(action);
        try {
            if (isPreview) {
                // Preview mode: simulate action locally
                await new Promise(r => setTimeout(r, 800));
                setQueue(prev => prev.filter(c => c.id !== selectedCase.id));
            } else {
                await api.reviewAction(companyId, selectedCase.id, {
                    action,
                    note: `${action === 'clear' ? 'Cleared' : 'Blacklisted'} by reviewer via UI`
                });
                const data = await api.reviewQueue(companyId);
                setQueue(Array.isArray(data) ? data : []);
            }
            setSelectedCase(null);
            setActivePage('dashboard');
        } catch (e) {
            console.error("Review action failed:", e);
            alert("Action failed. Check console.");
        } finally {
            setActionLoading(null);
        }
    };

    const getSeverityColor = (severity) => {
        if (severity === 'critical') return 'bg-red-600';
        if (severity === 'high') return 'bg-orange-600';
        if (severity === 'medium') return 'bg-yellow-600';
        return 'bg-blue-600';
    };

    const pageTransition = {
        initial: { x: 20, opacity: 0 },
        animate: { x: 0, opacity: 1 },
        exit: { x: -20, opacity: 0 },
        transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] }
    };

    return (
        <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
            className="fixed inset-0 z-[160] bg-[#E6E6E3] text-[#1c1c1c] overflow-y-auto selection:bg-black selection:text-white custom-scrollbar-reviewer"
            style={{ willChange: 'transform' }}
            data-lenis-prevent
        >
            {/* STICKY HEADER */}
            <header className="sticky top-0 left-0 w-full bg-[#E6E6E3] border-b-[3px] border-[#1c1c1c] z-50 px-6 md:px-12 py-5 flex justify-between items-center bg-opacity-95 backdrop-blur-sm">
                <div className="flex items-center gap-6">
                    <button
                        onClick={activePage === 'review' ? () => { setActivePage('dashboard'); setSelectedCase(null); } : onExit}
                        className="px-6 py-2.5 border-[2px] border-[#1c1c1c] font-grotesk text-[10px] font-black uppercase tracking-[0.2em] hover:bg-[#1c1c1c] hover:text-[#E6E6E3] transition-all flex items-center gap-2 group"
                    >
                        <span className="group-hover:-translate-x-1 transition-transform inline-block">←</span>
                        {activePage === 'review' ? 'BACK' : 'EXIT'}
                    </button>
                    <div className="h-10 w-[2px] bg-[#1c1c1c]/10 hidden md:block"></div>
                    <span className="font-montreal font-black text-sm tracking-[0.2em] uppercase text-[#1c1c1c]">
                        REVIEW TERMINAL
                    </span>
                </div>
                <div className="font-grotesk text-[11px] font-black tracking-[0.1em] uppercase opacity-100 text-[#1c1c1c]">
                    AUTH: HUMAN_VERIFIER
                </div>
            </header>

            <main className="max-w-[1280px] mx-auto px-6 md:px-12 py-16 min-h-[90vh]">
                <AnimatePresence mode="wait">
                    {/* ═══════════════════════════════════════ */}
                    {/* DASHBOARD: QUEUE LIST                   */}
                    {/* ═══════════════════════════════════════ */}
                    {activePage === 'dashboard' && (
                        <motion.div key="dashboard" {...pageTransition} className="space-y-16">
                            <div className="space-y-4">
                                <h1 className="font-montreal font-black text-5xl md:text-8xl uppercase tracking-tighter leading-none">
                                    PENDING <br />QUEUE
                                </h1>
                                <p className="font-inter text-[11px] font-black opacity-40 uppercase tracking-[0.2em]">
                                    {isLoading ? 'LOADING...' : `${queue.length} ANOMALIES ESCALATED FOR HUMAN VERIFICATION`}
                                </p>
                            </div>

                            {isPreview && (
                                <div className="px-6 py-4 bg-[#1c1c1c] text-white flex items-center gap-4 rounded-sm">
                                    <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse shrink-0" />
                                    <span className="font-grotesk text-[10px] font-black uppercase tracking-[0.2em]">
                                        PREVIEW MODE — Showing simulated review cases. Real cases appear when the bias agent escalates anomalies.
                                    </span>
                                </div>
                            )}

                            {isLoading ? (
                                <div className="py-24 text-center">
                                    <div className="font-grotesk text-[10px] font-black uppercase tracking-[0.5em] animate-pulse">
                                        CONNECTING TO REVIEW PIPELINE...
                                    </div>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 gap-6">
                                    {queue.map((item) => (
                                        <div
                                            key={item.id}
                                            className="group bg-white border-[2px] border-[#1c1c1c] p-8 flex flex-col md:flex-row md:items-center justify-between gap-8 hover:shadow-[12px_12px_0px_rgba(0,0,0,0.03)] transition-all duration-300 rounded-sm"
                                        >
                                            <div className="space-y-6">
                                                <div className="space-y-2">
                                                    <div className="flex items-center gap-4 flex-wrap">
                                                        <span className="font-montreal font-black text-2xl md:text-4xl uppercase tracking-tight text-[#1c1c1c]">
                                                            {item.role || 'Technical Role'}
                                                        </span>
                                                        <span className={`px-3 py-1 ${getSeverityColor(item.severity)} text-white text-[9px] font-grotesk font-black uppercase tracking-widest rounded-sm`}>
                                                            {item.severity || 'MEDIUM'}
                                                        </span>
                                                        <span className="px-3 py-1 bg-[#1c1c1c] text-white border border-[#1c1c1c] text-[10px] font-grotesk font-black uppercase tracking-widest rounded-sm">
                                                            {item.candidate_anon_id}
                                                        </span>
                                                    </div>
                                                    <div className="font-inter text-xs font-bold text-orange-700 uppercase tracking-widest flex items-center gap-2">
                                                        <span className="w-1.5 h-1.5 bg-orange-600 rounded-full animate-pulse" />
                                                        {item.reason || 'Anomaly detected by pipeline'}
                                                    </div>
                                                    {item.triggered_by && (
                                                        <div className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-30">
                                                            TRIGGERED BY: {item.triggered_by}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => handleReview(item)}
                                                className="px-10 py-5 bg-[#1c1c1c] text-white font-grotesk text-[11px] tracking-[0.3em] font-black uppercase hover:bg-black hover:scale-[1.02] transition-all flex items-center gap-3 group/btn shrink-0"
                                            >
                                                REVIEW <span className="text-xl group-hover/btn:translate-x-1 transition-transform">→</span>
                                            </button>
                                        </div>
                                    ))}

                                    {queue.length === 0 && (
                                        <div className="py-24 text-center space-y-4">
                                            <div className="font-montreal font-black text-4xl opacity-20 italic">QUEUE DEPLETED</div>
                                            <p className="font-inter text-[10px] font-black uppercase tracking-widest opacity-40">
                                                {companyId ? 'All system anomalies have been verified.' : 'No company session. Log in as a company first.'}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* ═══════════════════════════════════════ */}
                    {/* REVIEW: CASE DETAIL + ACTIONS            */}
                    {/* ═══════════════════════════════════════ */}
                    {activePage === 'review' && selectedCase && (
                        <motion.div key="review" {...pageTransition} className="space-y-16 pb-24">
                            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b-[2px] border-[#1c1c1c] pb-8">
                                <div className="space-y-3">
                                    <div className="flex items-center gap-4">
                                        <span className="font-grotesk text-[10px] uppercase font-black tracking-widest opacity-40">REVIEW SESSION</span>
                                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                        <span className={`px-3 py-1 ${getSeverityColor(selectedCase.severity)} text-white text-[9px] font-grotesk font-black uppercase tracking-widest rounded-sm`}>
                                            {selectedCase.severity}
                                        </span>
                                    </div>
                                    <h2 className="font-montreal font-black text-4xl md:text-6xl uppercase tracking-tighter leading-none">
                                        {selectedCase.candidate_anon_id}
                                    </h2>
                                    <p className="font-inter text-[10px] font-black uppercase tracking-widest opacity-40">
                                        {selectedCase.role || 'Technical Role'} · Case #{selectedCase.id}
                                    </p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                                {/* LEFT: EVIDENCE */}
                                <div className="lg:col-span-5 space-y-12">
                                    {/* Skills */}
                                    <div className="space-y-6">
                                        <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] text-[#1c1c1c]/40">VERIFIED SKILLS</label>
                                        <div className="flex flex-wrap gap-2">
                                            {(selectedCase.skills || []).length > 0 ? (
                                                selectedCase.skills.map(skill => (
                                                    <span key={skill} className="px-4 py-2 bg-white border-[2px] border-[#1c1c1c] font-grotesk text-[10px] font-black uppercase tracking-widest shadow-[4px_4px_0px_rgba(0,0,0,0.05)]">
                                                        {skill}
                                                    </span>
                                                ))
                                            ) : (
                                                <span className="font-inter text-xs opacity-40 italic">No skills data available</span>
                                            )}
                                        </div>
                                    </div>

                                    {/* Evidence Sources */}
                                    <div className="p-8 bg-white border-[2px] border-[#1c1c1c] space-y-8 shadow-[8px_8px_0px_rgba(0,0,0,0.02)]">
                                        <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] text-[#1c1c1c]/40">EVIDENCE CHANNELS</label>
                                        <div className="space-y-4">
                                            {(selectedCase.evidence_sources || ['ATS', 'GITHUB']).map(source => (
                                                <div key={source} className="p-5 bg-[#F9F9F7] border border-[#1c1c1c]/10 flex items-center justify-between group cursor-pointer hover:border-[#1c1c1c] transition-all">
                                                    <span className="font-grotesk text-[11px] font-black uppercase tracking-widest text-[#1c1c1c]">{source}</span>
                                                    <span className="font-mono text-[9px] opacity-20 group-hover:opacity-60 transition-opacity">SIGNAL</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Stats */}
                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="p-6 bg-white border-[2px] border-[#1c1c1c] space-y-2">
                                            <label className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">CONFIDENCE</label>
                                            <div className="font-montreal font-black text-3xl">{selectedCase.confidence || 0}%</div>
                                        </div>
                                        <div className="p-6 bg-white border-[2px] border-[#1c1c1c] space-y-2">
                                            <label className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">MATCH SCORE</label>
                                            <div className="font-montreal font-black text-3xl">{selectedCase.match_score || 0}%</div>
                                        </div>
                                    </div>
                                </div>

                                {/* RIGHT: ANOMALY ANALYSIS */}
                                <div className="lg:col-span-7 space-y-12 bg-white border-[2px] border-[#1c1c1c] p-8 md:p-12 shadow-[12px_12px_0px_rgba(0,0,0,0.03)]">
                                    <div className="space-y-10">
                                        {/* Reason / Anomaly */}
                                        <div className="space-y-4">
                                            <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] text-orange-600">ESCALATION REASON</label>
                                            <div className="flex gap-6 items-start">
                                                <div className="w-1 h-12 bg-orange-600 shrink-0" />
                                                <p className="font-inter text-base font-bold leading-relaxed text-[#1c1c1c]">
                                                    {selectedCase.reason}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Evidence Details */}
                                        {selectedCase.evidence_json && (
                                            <div className="space-y-4">
                                                <label className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] text-[#1c1c1c]/40">EVIDENCE DATA</label>
                                                <div className="space-y-4">
                                                    {selectedCase.evidence_json.manipulation && (
                                                        <div className="flex gap-6 items-start">
                                                            <div className="w-1 h-6 bg-red-500 shrink-0" />
                                                            <div>
                                                                <span className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">Manipulation</span>
                                                                <p className="font-inter text-sm font-bold text-[#1c1c1c]">
                                                                    Severity: {selectedCase.evidence_json.manipulation.severity || 'Unknown'}
                                                                    {selectedCase.evidence_json.manipulation.flags?.length > 0 && (
                                                                        <span className="opacity-60"> · {selectedCase.evidence_json.manipulation.flags.join(', ')}</span>
                                                                    )}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )}
                                                    {selectedCase.evidence_json.integrity_check?.discrepancy_detected && (
                                                        <div className="flex gap-6 items-start">
                                                            <div className="w-1 h-6 bg-yellow-500 shrink-0" />
                                                            <div>
                                                                <span className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">Integrity</span>
                                                                <p className="font-inter text-sm font-bold text-[#1c1c1c]">
                                                                    Type: {selectedCase.evidence_json.integrity_check.type || 'Discrepancy'}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )}
                                                    {selectedCase.evidence_json.ats_semantic_flags?.length > 0 && (
                                                        <div className="flex gap-6 items-start">
                                                            <div className="w-1 h-6 bg-amber-500 shrink-0" />
                                                            <div>
                                                                <span className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">ATS Flags</span>
                                                                <p className="font-inter text-sm font-bold text-[#1c1c1c]">
                                                                    {selectedCase.evidence_json.ats_semantic_flags.length} semantic flag(s) detected
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}

                                        {/* Triggered By */}
                                        <div className="grid grid-cols-2 gap-8 pt-10 border-t-[2px] border-[#1c1c1c]/5">
                                            <div className="space-y-2">
                                                <label className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">TRIGGERED BY</label>
                                                <div className="font-montreal font-black text-xl uppercase">{selectedCase.triggered_by || 'PIPELINE'}</div>
                                            </div>
                                            <div className="space-y-2">
                                                <label className="font-grotesk text-[9px] font-black uppercase tracking-widest opacity-40">ESCALATED AT</label>
                                                <div className="font-inter text-sm font-bold">
                                                    {selectedCase.created_at ? new Date(selectedCase.created_at).toLocaleString() : '—'}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Human Protocol Message */}
                                        <div className="p-6 bg-[#1c1c1c] text-white space-y-3">
                                            <span className="font-grotesk text-[9px] font-black uppercase tracking-[0.3em] opacity-40">HUMAN PROTOCOL</span>
                                            <p className="font-inter text-xs leading-relaxed font-medium opacity-80">
                                                Review the evidence signals above. If the anomaly is a false positive and the candidate's data is legitimate,
                                                click <strong>CLEAR EVIDENCE</strong> to pass them through. If the manipulation is confirmed,
                                                click <strong>BLACKLIST</strong> to reject and flag the candidate.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* ═══ DECISION BUTTONS ═══ */}
                            <div className="w-full flex flex-col md:flex-row gap-6 justify-center items-center py-12 border-t-[3px] border-[#1c1c1c] mt-20">
                                <button
                                    onClick={() => handleAction('clear')}
                                    disabled={!!actionLoading}
                                    className="w-full md:w-auto px-16 py-6 bg-green-700 text-white font-grotesk font-black text-xs tracking-[0.4em] uppercase hover:bg-green-800 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[8px_8px_0px_rgba(0,0,0,0.1)] disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {actionLoading === 'clear' ? 'PROCESSING...' : 'CLEAR EVIDENCE'}
                                </button>
                                <button
                                    onClick={() => handleAction('blacklist')}
                                    disabled={!!actionLoading}
                                    className="w-full md:w-auto px-16 py-6 bg-red-700 text-white font-grotesk font-black text-xs tracking-[0.4em] uppercase hover:bg-red-800 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[8px_8px_0px_rgba(0,0,0,0.1)] disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {actionLoading === 'blacklist' ? 'PROCESSING...' : 'BLACKLIST CANDIDATE'}
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

            <GridPlus className="fixed inset-0 pointer-events-none opacity-5 z-0" />
            <style>{`
                .custom-scrollbar-reviewer::-webkit-scrollbar { width: 6px; }
                .custom-scrollbar-reviewer::-webkit-scrollbar-thumb { background: #1c1c1c; border-radius: 10px; }
                .custom-scrollbar-reviewer::-webkit-scrollbar-track { background: rgba(0,0,0,0.05); }
            `}</style>
        </motion.div>
    );
}
