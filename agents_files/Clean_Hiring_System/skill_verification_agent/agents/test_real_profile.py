
import requests
import json
import logging
import sys
import os

# Add relevant paths for Skill Agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../agents_files/Clean_Hiring_System/skill_verification_agent/agents")))

from skill_verification_agent_v2 import SkillVerificationAgentV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_real_profile(github_url):
    print(f"\n🚀 TESTING REAL PROFILE: {github_url}")
    
    # 1. Call GitHub Service
    service_url = "http://localhost:8005/scrape"
    try:
        print(f"📡 Calling GitHub Service at {service_url}...")
        response = requests.post(service_url, json={"github_url": github_url}, timeout=120)
        github_data = response.json()
        
        if not github_data.get("success"):
            print(f"❌ Error from GitHub Service: {github_data.get('error')}")
            return
            
        print(f"✅ Received GitHub Data. Status: {github_data.get('github_status')}")
        print(f"📊 Activity Score: {github_data.get('activity_score')}")
        
    except Exception as e:
        print(f"❌ Failed to reach GitHub Service: {e}")
        return

    # 2. Run Skill Verification Agent
    print("\n🧠 Processing through Skill Verification Agent...")
    agent = SkillVerificationAgentV2()
    
    # Wrap in evidence graph structure
    evidence_graph = {
        "evaluation_id": "test_ayazxdev",
        "signals": {
            "github": github_data
        }
    }
    
    # We also need to test with EvidenceGraphBuilder for the complete flow
    # but since we want to see the score specifically:
    try:
        result = agent.issue_credential(evidence_graph)
        output = result.get("output", {})
        
        print("\n=== FINAL CREDENTIAL ===")
        print(f"👤 Candidate: {github_url.split('/')[-1]}")
        print(f"🏆 Portfolio Score: {output.get('skill_confidence')}")
        print(f"🔗 Signal Strength: {output.get('signal_strength')}")
        print(f"✅ Verified Skills: {json.dumps(output.get('verified_skills'), indent=2)}")
        print(f"📝 Confidence Explanation: {output.get('confidence_explanation')}")
        print(f"⚠️ Test Required: {output.get('test_required')}")
        
    except Exception as e:
        print(f"❌ Skill Agent failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    profile_url = "https://github.com/udbhaw08"
    test_real_profile(profile_url)
