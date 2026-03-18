
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
from ..utils.match_normalizer import MatchNormalizer

logger = logging.getLogger(__name__)

class MatchingAgent:
    """
    Stage 5: Transparent Matching Agent (v2 Gold Standard - Hardened)
    
    Architecture: Pure function matching. No file-path logic inside the core.
    Formula: Deterministic 4-pillar scoring [Core 40%, Frameworks 25%, Evidence 20%, Growth 15%]
    """
    
    def match(self, jd: Dict, candidate: Dict) -> Dict:
        """
        Main entry point for matching.
        Expects JD v3 and SkillAgent v3 (normalized) as dictionaries.
        """
        # 1. Validation & Normalization
        try:
            jd_norm = MatchNormalizer.normalize_job(jd)
            cand_norm = MatchNormalizer.normalize_candidate(candidate)
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return {"error": "Invalid Input Schema", "details": str(e)}

        # 2. Calculate Pillars (Refined Scoring Logic)
        core_score = self._score_core(jd_norm, cand_norm)
        framework_score = self._score_frameworks(jd_norm, cand_norm)
        evidence_score = self._score_evidence(jd_norm, cand_norm)
        learning_score = self._score_learning(jd_norm, cand_norm)

        # 3. Aggregate Final Score
        final_score = round(core_score + framework_score + evidence_score + learning_score, 3)
        
        # 4. Determine Decision Band (Machine-Safe Enums)
        decision_enum, status_enum = self._band_decision(final_score)

        return {
            "match_score": round(final_score * 100), # Legacy support (0-100)
            "match_status": status_enum,
            "decision_reason": decision_enum,
            "final_score": final_score,
            "breakdown": {
                "core_skills": round(core_score, 3),
                "frameworks_tools": round(framework_score, 3),
                "evidence": round(evidence_score, 3),
                "learning_velocity": round(learning_score, 3)
            },
            "analysis": {
                "matched_skills": list(set(cand_norm["verified_skills"]) & set(jd_norm["strict_requirements"])),
                "missing_skills": list(set(jd_norm["strict_requirements"]) - set(cand_norm["verified_skills"]))
            },
            "timestamp": datetime.now().isoformat()
        }

    def _score_core(self, jd: Dict, cand: Dict) -> float:
        """Pillar 1: Core Skills (40% Weight) - Refined for Correctness"""
        core_set = set(
            jd.get("strict_requirements", []) +
            jd.get("languages", []) +
            jd.get("web_fundamentals", [])
        )

        if not core_set:
            return 0.40  # Defensive default: if no core reqs defined, grant full weight

        verified = set(cand.get("verified_skills", []))
        matches = verified & core_set

        # Ratio of matched core signals to total required core signals
        ratio = len(matches) / len(core_set)
        return ratio * 0.40

    def _score_frameworks(self, jd: Dict, cand: Dict) -> float:
        """Pillar 2: Frameworks & Tools (25% Weight) - Schema Resilient"""
        frameworks = set(
            jd.get("frontend_frameworks", []) +
            jd.get("backend_frameworks", [])
        )

        # Fallback: infrastructure concepts often drift into backend_concepts
        infra = set(
            jd.get("infrastructure_concepts", []) +
            jd.get("backend_concepts", [])
        )

        tools = set(jd.get("developer_tools", []))
        verified = set(cand.get("verified_skills", []))

        fw_match = len(verified & frameworks) / max(1, len(frameworks))
        infra_match = len(verified & infra) / max(1, len(infra))
        tool_match = len(verified & tools) / max(1, len(tools))

        # Weighted Framework Score: FWs (50%) + Infra (30%) + Tools (20%)
        pillar_score = (
            0.5 * fw_match +
            0.3 * infra_match +
            0.2 * tool_match
        )

        return pillar_score * 0.25

    def _score_evidence(self, jd: Dict, cand: Dict) -> float:
        """Pillar 3: Evidence Signals (20% Weight) - Clamped & Bias-Fixed"""
        # GitHub (max 0.12) - Strict Clamping
        github_raw = cand.get("github_score", 0.0)
        github_score = min(max(github_raw, 0.0), 1.0)
        github_contrib = github_score * 0.12
        
        # CP (max 0.08) - Bias-Fixed: Only grants credit if github evidence exists
        cp_activity = cand.get("cp_activity", False)
        cp_required = jd["problem_solving"].get("required", False)
        
        if cp_activity:
            cp_contrib = 0.08
        elif not cp_required and github_score >= 0.4:
            # Grant 0.04 "plus" credit ONLY if GitHub evidence is strong (>= 0.4)
            cp_contrib = 0.04
        else:
            cp_contrib = 0.0
            
        return github_contrib + cp_contrib

    def _score_learning(self, jd: Dict, cand: Dict) -> float:
        """Pillar 4: Learning Velocity (15% Weight) - Clamped"""
        # Strict Clamping for velocity to ensure deterministic math guarantees
        velocity_raw = cand.get("learning_velocity", 0.5)
        velocity = min(max(velocity_raw, 0.0), 1.0)
        
        weight = jd["matching_philosophy"].get("learning_velocity_weight", 0.2)
        
        return velocity * weight * 0.15

    def _band_decision(self, score: float) -> (str, str):
        """Standard Junior-Safe Decision Bands (Machine-Safe Enums)"""
        if score >= 0.75: return "STRONG_MATCH", "MATCHED"
        if score >= 0.55: return "GOOD_MATCH", "CONDITIONAL_MATCH"
        if score >= 0.40: return "POTENTIAL_MATCH", "POTENTIAL"
        return "NO_MATCH", "REJECTED"

    # COMPATIBILITY LAYER (DEPRECATED)
    def _calculate_match(self, credential: Dict, job: Dict) -> Dict:
        return self.match(job, credential)

    def _load_json(self, path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
