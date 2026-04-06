import { useEffect, useMemo, useState, useCallback } from "react";
import { motion } from "framer-motion";
import PipelineGrid from "./PipelineGrid";
import JobDetailsModal from "./JobDetailsModal";
import { api } from "../api/backend";

const STATUS_TO_COLUMN = {
  pending: "hidden", // We don't show the millions of raw applications
  verified: "hidden",
  matched: "selected",
  selected: "selected",
  needs_review: "selected", // Review cases also show up in the main selection hub
  rejected: "rejected",
};

const COLUMN_META = [
  { id: "selected", title: "Selection & Review Hub" },
];

export default function CompanyRolePipeline({ roleId, onBack, onSelectCandidate, onViewSelected }) {
  const companyId = localStorage.getItem("fhn_company_id") || "";
  const [jobs, setJobs] = useState([]);
  const [jobId, setJobId] = useState(roleId || null);
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  useEffect(() => {
    if (!companyId) return;
    (async () => {
      try {
        setLoading(true);
        const js = await api.listCompanyJobs(companyId);
        setJobs(Array.isArray(js) ? js : []);
        if (!jobId && Array.isArray(js) && js.length) setJobId(js[0].id);
      } catch (e) {
        console.warn("Failed to load jobs", e);
      } finally {
        setLoading(false);
      }
    })();
  }, [companyId]);

  const refreshApps = useCallback(async (jid) => {
    if (!companyId || !jid) return;
    try {
      setLoading(true);
      const data = await api.listJobApplications(companyId, jid);
      setApps(Array.isArray(data) ? data : []);
    } catch (e) {
      console.warn("Failed to load applications", e);
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => {
    if (roleId) setJobId(roleId);
  }, [roleId]);

  useEffect(() => {
    refreshApps(jobId);
  }, [jobId, refreshApps]);

  const columns = useMemo(() => {
    const byCol = {};
    COLUMN_META.forEach(c => byCol[c.id] = []);

    // Use a Map to de-duplicate by anon_id across all status stages
    const latestAppsMap = new Map();
    for (const a of apps) {
      const existing = latestAppsMap.get(a.anon_id);
      if (!existing || new Date(a.created_at) > new Date(existing.created_at)) {
        latestAppsMap.set(a.anon_id, a);
      }
    }

    const currentJob = jobs.find(j => String(j.id) === String(jobId));

    for (const a of latestAppsMap.values()) {
      const col = STATUS_TO_COLUMN[a.status] || "applied";
      if (byCol[col]) {
        byCol[col].push({
          id: a.anon_id,
          confidence: a.match_score ?? 0,
          bias: (a.feedback?.message ? "Feedback" : "—"),
          stage: col,
          breakdown: a.feedback?.breakdown,
          status: a.status,
          feedback: a.feedback,
          candidate_details: a.candidate_details,
          job_title: currentJob?.title || "Technical Role"
        });
      }
    }

    return COLUMN_META.map((c) => ({
      id: c.id,
      title: c.title,
      candidates: byCol[c.id],
    }));
  }, [apps, jobs, jobId]);

  const runMatching = async () => {
    if (!companyId || !jobId) return;
    try {
      setRunning(true);
      await api.runMatching(companyId, jobId);
      await refreshApps(jobId);
    } catch (e) {
      console.error(e);
      alert("Run matching failed. See console for details.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="h-screen overflow-y-auto bg-[#E6E6E3] text-[#1c1c1c]">
      {/* STICKY HEADER */}
      <header className="sticky top-0 left-0 w-full bg-[#E6E6E3] border-b-[3px] border-[#1c1c1c] z-50 px-6 md:px-12 py-6 flex justify-between items-center bg-opacity-95 backdrop-blur-sm">
        <div className="flex items-center gap-6">
          <button
            onClick={onBack}
            className="px-6 py-3 border-[2px] border-[#1c1c1c] font-grotesk text-[10px] font-black uppercase tracking-[0.2em] hover:bg-[#1c1c1c] hover:text-[#E6E6E3] transition-all flex items-center gap-2 group"
          >
            <span className="group-hover:-translate-x-1 transition-transform inline-block">←</span> BACK
          </button>
          <div className="h-10 w-[2px] bg-[#1c1c1c]/10 hidden md:block"></div>
          <div className="flex items-center gap-4">
            <div className="w-8 h-[2px] bg-[#1c1c1c]"></div>
            <span className="font-montreal font-black text-sm md:text-base tracking-[0.2em] uppercase text-[#1c1c1c]">
              ROLE PIPELINE: {jobs.find(j => String(j.id) === String(jobId))?.title}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="font-mono text-[9px] font-black opacity-30 uppercase tracking-widest text-[#1c1c1c]">
            ROLE REF: {jobId || 'R-101'}
          </div>
          <div className="px-3 py-1 bg-[#A7FF2E] text-black font-grotesk text-[8px] font-black uppercase tracking-widest rounded-full border border-black/10 shadow-sm">
            INTELLIGENCE v3 ACTIVE
          </div>
          <div className="h-4 w-[1px] bg-black/10" />
          <button
            onClick={runMatching}
            disabled={running}
            className={`px-4 py-2 border border-black/10 transition-all font-grotesk text-[9px] font-black uppercase tracking-widest ${running ? 'bg-gray-200 cursor-not-allowed opacity-50' : 'bg-black text-white hover:bg-[#1c1c1c]'}`}
          >
            {running ? "ENGINE RUNNING..." : "RE-RUN MATCHING ENGINE"}
          </button>
          <button
            onClick={() => setIsDetailsOpen(true)}
            className="px-6 py-2 border-2 border-black bg-white font-grotesk text-[10px] font-black uppercase tracking-widest hover:bg-black hover:text-white transition-all shadow-[4px_4px_0px_#000]"
          >
            VERIFY ROLE SPEC
          </button>
        </div>
      </header>

      <main className="max-w-[1440px] mx-auto px-6 md:px-12 py-12">
        <div className="mb-20">
          <h1 className="font-montreal font-black text-6xl md:text-8xl uppercase tracking-tighter leading-none mb-4">
            CANDIDATE FLOW
          </h1>
          <p className="font-inter text-sm font-bold opacity-60 uppercase tracking-tight max-w-2xl">
            Live technical signature matching across distributed evaluation nodes.
          </p>
        </div>

        {loading ? (
          <div className="py-24 flex items-center justify-center font-grotesk text-xs font-black uppercase tracking-[0.3em] opacity-30">
            Analyzing Data Streams...
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "circOut" }}
          >
            <PipelineGrid columns={columns} />
          </motion.div>
        )}
      </main>

      <JobDetailsModal
        isOpen={isDetailsOpen}
        onClose={() => setIsDetailsOpen(false)}
        job={jobs.find(j => String(j.id) === String(jobId))}
      />
      {/* GRID OVERLAY */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]" />
    </div>
  );
}
