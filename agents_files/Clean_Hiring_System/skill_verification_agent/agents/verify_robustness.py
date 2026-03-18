
import logging
import sys
from typing import Dict, List
import os

# Add relevant paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../agents_files/Clean_Hiring_System/skill_verification_agent/agents")))

from skill_verification_agent_v2 import SkillVerificationAgentV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_robustness():
    agent = SkillVerificationAgentV2()
    
    print("\n=== TEST 1: Partial GitHub Analysis (Time-boxed) ===")
    # Scenario: GitHub scraper timed out early, returning partial=True but no repos
    github_partial = {
        "success": True,
        "github_status": "partial",
        "activity_score": 50,
        "repos": [] # No repos found before timeout
    }
    
    score = agent._calculate_portfolio_score(
        github_data=github_partial,
        leetcode_data=None,
        codeforces_data=None,
        ats_data=None
    )
    print(f"Partial GitHub ONLY Score: {score}")
    assert score >= 35, f"Expected floor of 35 for partial data, got {score}"

    print("\n=== TEST 2: Missing Signals Weight Normalization ===")
    # Normalization: GH = 0.45/0.70 = 0.643, ATS = 0.25/0.70 = 0.357
    # GH Score = 80*0.643 + 16*0.357 = 51.44 + 5.71 = 57.15
    github_full = {
        "success": True,
        "github_status": "complete",
        "activity_score": 80,
        "repos": [{"best_repo_score": 80}]
    }
    # GH Score = 80*0.6 + 80*0.4 = 80
    
    ats_data = {
        "evidence": {
            "skills": ["Python", "React"],
            "experience": [{"title": "Dev"}],
            "semantic_flags": []
        }
    }
    # ATS Score = min(60, 2*3 + 1*10) = 16
    
    score = agent._calculate_portfolio_score(
        github_data=github_full,
        ats_data=ats_data
    )
    # Expected: 80 * 0.643 + 16 * 0.357 = 51.4 + 5.7 = 57.1 -> ~57
    print(f"Normalized GH+ATS Score: {score}")
    assert 55 <= score <= 60, f"Expected normalized score around 57, got {score}"

    print("\n=== TEST 3: Heartbeat for Any Evidence (Zero-Score Prevention) ===")
    # Scenario: Extremely weak evidence across multiple sources
    github_weak = {
        "success": True,
        "github_status": "complete",
        "activity_score": 0,
        "repos": []
    }
    ats_weak = {
        "evidence": {
            "skills": [],
            "experience": [],
            "semantic_flags": ["extremely_short"]
        }
    }
    
    score = agent._calculate_portfolio_score(
        github_data=github_weak,
        ats_data=ats_weak
    )
    print(f"Weak Evidence Heartbeat Score: {score}")
    assert score == 10, f"Expected heartbeat of 10 for weak but present evidence, got {score}"

    print("\n=== TEST 4: Unavailable Signal Handling ===")
    # Scenario: GitHub is unavailable (404/deleted)
    github_unavailable = {
        "success": False,
        "github_status": "unavailable"
    }
    # ATS only
    score = agent._calculate_portfolio_score(
        github_data=github_unavailable,
        ats_data=ats_data
    )
    # Weight for ATS becomes 1.0 (since it's the only one)
    # Score should be 16 (ATS only)
    print(f"ATS-only (GH Unavailable) Score: {score}")
    assert score == 16, f"Expected score of 16 (ATS only), got {score}"

    print("\n✅ ALL ROBUSTNESS TESTS PASSED")

if __name__ == "__main__":
    test_robustness()
