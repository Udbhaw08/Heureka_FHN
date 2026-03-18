"""Zynd webhook wrapper for ats agent.

This exposes the agent on Zynd's standard webhook endpoints:
  - POST /webhook (async)
  - POST /webhook/sync (sync, waits for set_response)
  - GET  /health

The business logic is reused from your existing codebase (no rewrite).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from zyndai_agent.agent import AgentConfig, ZyndAIAgent
from zyndai_agent.message import AgentMessage

from .common import parse_json_content, dump_json

load_dotenv()

# 2026 Fix: Force UTF-8 encoding for stdout/stderr on Windows to prevent charmap errors
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure the Clean_Hiring_System package is importable when running from repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
CLEAN_SYS = REPO_ROOT / "agents_files" / "Clean_Hiring_System"
if str(CLEAN_SYS) not in sys.path:
    sys.path.insert(0, str(CLEAN_SYS))
# Some modules expect skill_verification_agent on path for utils imports
SKILL_DIR = CLEAN_SYS / "skill_verification_agent"
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

def build_agent() -> ZyndAIAgent:
    cfg = AgentConfig(
        name="Ats Agent",
        description="Runs ATS-style checks (fraud/blacklist/policy gating) and produces a transparent pass/fail decision.",
        capabilities={"ai": ["ats_screening", "policy_checks"], "protocols": ["http"], "services": ["fair_hiring", "ats"]},
        webhook_host=os.getenv("ZYND_WEBHOOK_HOST", "0.0.0.0"),
        webhook_port=int(os.getenv("ATS_ZYND_PORT", "5104")),
        registry_url=os.getenv("ZYND_REGISTRY_URL", "https://registry.zynd.ai"),
        api_key=os.getenv("ZYND_API_KEY"),
        identity_credential_path=os.path.abspath(os.path.join(REPO_ROOT, os.getenv("ATS_ZYND_VC", "credentials/ats_vc.json"))),
        config_dir=os.getenv("ATS_ZYND_CONFIG_DIR", f".agent-ats"),
    )

    agent = ZyndAIAgent(agent_config=cfg)
    return agent

def attach_handler(agent: ZyndAIAgent) -> None:
    def handler(message: AgentMessage, topic: str):
        payload = parse_json_content(message.content)

        try:
            resume_path = payload.get("resume_path")
            resume_text = payload.get("resume_text")
            application_id = payload.get("application_id")
            
            if not resume_path and not resume_text:
                result = {"error": "Missing resume_path AND resume_text in payload", "agent": "ats"}
            else:
                from skill_verification_agent.agents.ats_guard import run_ats_guard
                from skill_verification_agent.agents.ats import ATSEvidenceAgent
                
                # Step 1: Run Security Guard
                guard_result = {}
                if resume_path:
                    guard_result = run_ats_guard(resume_path)
                
                # Step 2: Run Evidence Extraction
                # Initialize agent (lazy-load style)
                ats_impl = ATSEvidenceAgent(llm=None)
                extraction_result = ats_impl.extract_evidence(
                    pdf_path=resume_path,
                    resume_text=resume_text,
                    evaluation_id=str(application_id) if application_id else None
                )
                
                # Merge Results
                result = {
                    "success": True,
                    "action": guard_result.get("security_status", "OK"),
                    "trust_score": guard_result.get("trust_score", 100),
                    "flags": [f["type"] for f in guard_result.get("flags", [])] if guard_result.get("flags") else [],
                    "evidence": extraction_result,
                    "skills": extraction_result.get("skills", []),
                    "experience": extraction_result.get("experience", []),
                    "identity": extraction_result.get("identity", {})
                }
                print(f"[ats-debug] Extraction complete. Skills found: {len(result['skills'])}")
                if result['skills']:
                    print(f"[ats-debug] First 3 skills: {result['skills'][:3]}")
        except Exception as e:
            import traceback
            print(f"[ats] Error in handler: {str(e)}")
            traceback.print_exc()
            result = {"error": str(e), "agent": "ats"}

        # Sync callers wait on this
        agent.set_response(message.message_id, dump_json(result))

    agent.add_message_handler(handler)

def main():
    agent = build_agent()
    attach_handler(agent)

    print(f"[ats] Agent ID: {agent.agent_id}")
    print(f"[ats] Webhook URL: {agent.webhook_url}")
    print(f"[ats] Registry URL: {agent.agent_config.registry_url}")
    print(f"[ats] Capabilities: {agent.agent_config.capabilities}")

    # Keep the process alive (Flask server runs in background thread)
    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
