import { useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

/**
 * CandidateAuth — Auth0 powered sign-in / sign-up for candidates.
 *
 * Flow:
 *  1. User lands here unauthenticated  → shows two buttons (Log In / Sign Up)
 *  2. Auth0 redirects back             → isAuthenticated = true
 *  3. syncWithBackend()               → POST /auth/candidate/auth0-sync
 *  4. Stores anon_id in localStorage  → navigates to /candidate
 *
 * The existing layout / styling is preserved so the design looks identical.
 */
export default function CandidateAuth({ onExit }) {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, user, loginWithRedirect, logout, syncWithBackend } = useAuth();

  // After Auth0 redirects back, automatically sync with the backend
  useEffect(() => {
    if (!isAuthenticated || isLoading) return;

    // If already synced in this session, skip
    if (localStorage.getItem("fhn_candidate_anon_id")) {
      navigate("/candidate");
      return;
    }

    syncWithBackend()
      .then((data) => {
        localStorage.setItem("fhn_role", "candidate");
        localStorage.setItem("fhn_candidate_anon_id", data.anon_id);
        localStorage.setItem("fhn_candidate_email", data.email);
        navigate("/candidate");
      })
      .catch((err) => {
        console.error("[Auth0 Sync Error]", err);
        // Don't block — navigate anyway and let pages handle missing data
        navigate("/candidate");
      });
  }, [isAuthenticated, isLoading, navigate, syncWithBackend]);

  // ── Loading state (Auth0 initialising or syncing) ────────────────────────
  if (isLoading) {
    return (
      <motion.div
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
        className="fixed inset-0 z-[150] bg-[#E6E6E3] text-[#1c1c1c] flex items-center justify-center"
        data-lenis-prevent
      >
        <div className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] opacity-40">
          AUTHENTICATING...
        </div>
      </motion.div>
    );
  }

  // ── Already authenticated (edge case: navigated here while logged in) ────
  if (isAuthenticated) {
    return (
      <motion.div
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
        className="fixed inset-0 z-[150] bg-[#E6E6E3] text-[#1c1c1c] flex items-center justify-center"
        data-lenis-prevent
      >
        <div className="font-grotesk text-[10px] font-black uppercase tracking-[0.3em] opacity-40">
          SYNCING ACCOUNT...
        </div>
      </motion.div>
    );
  }

  // ── Unauthenticated: show the Auth0 login/signup options ─────────────────
  return (
    <motion.div
      initial={{ x: "100%" }}
      animate={{ x: 0 }}
      exit={{ x: "100%" }}
      transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
      className="fixed inset-0 z-[150] bg-[#E6E6E3] text-[#1c1c1c] overflow-y-auto selection:bg-black selection:text-white"
      style={{ willChange: "transform" }}
      data-lenis-prevent
    >
      {/* Header */}
      <header className="sticky top-0 left-0 w-full bg-[#E6E6E3] border-b-[3px] border-[#1c1c1c] z-50 px-6 md:px-12 py-6 flex justify-between items-center bg-opacity-95 backdrop-blur-sm">
        <div className="flex items-center gap-6">
          <button
            onClick={onExit}
            className="px-6 py-3 border-[2px] border-[#1c1c1c] font-grotesk text-[11px] font-black uppercase tracking-[0.2em] hover:bg-[#1c1c1c] hover:text-[#E6E6E3] transition-all flex items-center gap-2 group"
          >
            <span className="group-hover:-translate-x-1 transition-transform inline-block">←</span>{" "}
            BACK
          </button>
          <div className="h-10 w-[2px] bg-[#1c1c1c]/10 hidden md:block" />
          <span className="font-montreal font-black text-sm md:text-base tracking-[0.2em] uppercase text-[#1c1c1c]">
            CANDIDATE AUTH
          </span>
        </div>

        {/* Auth0 badge */}
        <div className="hidden md:flex items-center gap-2 opacity-40">
          <div className="w-2 h-2 bg-[#1c1c1c] rounded-full" />
          <span className="font-grotesk text-[9px] font-black uppercase tracking-[0.25em]">
            SECURED BY AUTH0
          </span>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-[980px] mx-auto px-6 md:px-12 py-14 space-y-10">
        <div className="space-y-2">
          <h1 className="font-montreal font-black text-5xl md:text-7xl uppercase tracking-tighter leading-[0.9]">
            CREATE OR ACCESS
            <br />CANDIDATE ID
          </h1>
          <p className="font-inter text-sm font-bold opacity-70">
            Secure authentication via Auth0. Your ID is generated once and remains
            consistent across the platform.
          </p>
        </div>

        {/* Auth action card */}
        <div className="relative group">
          <div className="absolute inset-0 bg-black translate-x-1 translate-y-1 transition-transform group-hover:translate-x-2 group-hover:translate-y-2" />
          <div className="relative bg-white border-2 border-black p-6 md:p-10 space-y-8">
            {/* Sign In button */}
            <div className="flex flex-col md:flex-row gap-4">
              <button
                onClick={() =>
                  loginWithRedirect({
                    appState: { returnTo: "/candidate" },
                    authorizationParams: { screen_hint: "login" },
                  })
                }
                className="flex-1 bg-black text-white px-10 py-5 font-grotesk text-[10px] font-black uppercase tracking-[0.3em] hover:bg-black/80 transition-all shadow-[0_10px_25px_rgba(0,0,0,0.2)]"
              >
                LOG IN
              </button>
 
              {/* Sign Up button */}
              <button
                onClick={() =>
                  loginWithRedirect({
                    appState: { returnTo: "/candidate" },
                    authorizationParams: { screen_hint: "signup" },
                  })
                }
                className="flex-1 bg-transparent border-2 border-black text-black px-10 py-5 font-grotesk text-[10px] font-black uppercase tracking-[0.3em] hover:bg-black hover:text-white transition-all"
              >
                CREATE ACCOUNT
              </button>
            </div>

            {/* Info strip */}
            <div className="border-t-2 border-black/10 pt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { icon: "🔒", label: "SECURE", desc: "Auth0 enterprise grade" },
                { icon: "⚡", label: "INSTANT", desc: "One-click login" },
                { icon: "🛡️", label: "PRIVACY", desc: "Anonymous scoring" },
              ].map((item) => (
                <div key={item.label} className="flex items-start gap-3">
                  <span className="text-lg">{item.icon}</span>
                  <div>
                    <div className="font-grotesk text-[8px] font-black uppercase tracking-[0.3em]">
                      {item.label}
                    </div>
                    <div className="font-inter text-[10px] opacity-50 mt-0.5">
                      {item.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="font-inter text-[10px] font-bold uppercase tracking-widest opacity-50">
              We store protected attributes only for audit/reporting — not for scoring.
            </div>
          </div>
        </div>
      </main>
    </motion.div>
  );
}
