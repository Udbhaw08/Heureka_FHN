
import sys
import os
import time
import logging
import json

# Add relevant paths
current_dir = os.path.dirname(os.path.abspath(__file__))
# agents_services is at Agents-main/agents_services
# current_dir is Agents-main/agents_files/Clean_Hiring_System/skill_verification_agent/agents
sys.path.append(os.path.abspath(os.path.join(current_dir, "../../../../agents_services")))
sys.path.append(os.path.abspath(os.path.join(current_dir, "../scraper")))

from github_api import GitHubAPIClient
from github_service import analyze_github_optimized

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def debug_scrape(username):
    token = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
    client = GitHubAPIClient(token=token)
    
    start_time = time.time()
    max_time = 120
    
    print(f"🧐 Starting local debug analysis for: {username}")
    print(f"Token: {'Set' if token else 'Not Set'}")
    
    try:
        result = analyze_github_optimized(client, username, max_time, start_time)
        print("\n=== GITHUB ANALYSIS RESULT ===")
        print(f"Status: {result.get('github_status')}")
        print(f"Credibility Score: {result.get('credibility_signal', {}).get('score')}")
        print(f"Verified Languages: {result.get('skill_signal', {}).get('verified_languages', [])}")
        
        # 2. Run Skill Verification Agent
        print("\n🧠 Processing through Skill Verification Agent...")
        sys.path.append(os.path.abspath(os.path.join(current_dir, ".")))
        from skill_verification_agent_v2 import SkillVerificationAgentV2
        
        agent = SkillVerificationAgentV2()
        evidence_graph = {
            "evaluation_id": f"debug_{username}",
            "signals": {
                "github": result
            }
        }
        
        credential = agent.issue_credential(evidence_graph)
        output = credential.get("output", {})
        
        print("\n=== FINAL CREDENTIAL ===")
        print(f"🏆 Portfolio Score: {output.get('skill_confidence')}")
        print(f"🔗 Signal Strength: {output.get('signal_strength')}")
        print(f"✅ Verified Skills: {json.dumps(output.get('verified_skills'), indent=2)}")
        print(f"📝 Confidence Explanation: {output.get('confidence_explanation')}")
        print(f"⚠️ Test Required: {output.get('test_required')}")
        
        # Save to file
        with open("debug_results.json", "w") as f:
            json.dump(credential, f, indent=4)
        print("\n💾 Results saved to debug_results.json")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_scrape("udbhaw08")
