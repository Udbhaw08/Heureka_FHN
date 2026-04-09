import json
import re
import time
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv(override=True)

class JobExtractionAgent:
    def __init__(self, model_name=None):
        """Initializes the agent with OpenRouter intelligence."""
        api_key = (
            os.getenv("OPENROUTER_API_KEY") or 
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("API_KEY")
        )
        base_url = os.getenv("OPENAI_API_BASE") or "https://openrouter.ai/api/v1"
        model_to_use = model_name or os.getenv("LLM_MODEL") or "anthropic/claude-3-haiku"
        
        if not api_key or "placeholder" in api_key.lower():
            print("[WARN] JobExtractionAgent: No valid API key found. Using MOCK mode.")
            self.model = None
            return

        self.model = ChatOpenAI(
            model=model_to_use,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=0,
            default_headers={
                "HTTP-Referer": "https://fair-hiring.network",
                "X-Title": "Fair Hiring System"
            }
        )
        
        self.system_instructions = (
            "You are a master technical intelligence agent. Your mission is to extract structured intent from a job description (JD) for a high-precision matching engine."
            
            "\n\n--- EXTRACTION RULES ---"
            "\n1. CANONICAL NORMALIZATION: All skills and requirements MUST be canonical tech terms (e.g., 'YOLOv8', not 'YOLO-based'). No vague phrases like 'One additional language' or 'Deep knowledge'."
            "\n2. BUCKETED TAXONOMY: Split skills into the categories below. If a skill doesn't fit any specific bucket, put it in 'domain_specific_skills'."
            "\n3. MANDATORY VS OPTIONAL: Problem-solving platforms (LeetCode/CP) are ONLY 'required: true' if the JD says 'Must have' or 'Required'. If 'A plus' or 'Preferred', set 'required: false'."
            "\n4. VELOCITY TUNING: 'learning_velocity_weight' MUST be between 0.1 and 0.3. Never exceed 0.3 unless it's a dedicated internship/training role."
            "\n5. COMPLETENESS: Extract ALL explicitly mentioned technologies, tools, frameworks, and libraries from the JD. Do NOT skip any skill that is named. Include both 'Required' and 'Good to have' skills."
            "\n6. strict_requirements MUST list ALL skills marked as 'Required' in the JD. soft_requirements MUST list ALL 'Good to have' / 'Nice to have' / 'Bonus' skills."
            
            "\n\n--- OUTPUT SCHEMA (JSON ONLY) ---"
            "\n{{"
            "\n  \"role\": \"Role Title\","
            "\n  \"seniority\": \"junior|junior-mid|mid|senior\","
            "\n  \"seniority_flexibility\": true/false,"
            "\n  \"languages\": [\"Python\", \"C++\", ...],"
            "\n  \"frameworks\": [\"React\", \"FastAPI\", \"PyTorch\", \"TensorFlow\", ...],"
            "\n  \"libraries_and_tools\": [\"OpenCV\", \"NumPy\", \"Pandas\", \"YOLOv8\", ...],"
            "\n  \"databases\": [\"PostgreSQL\", \"MongoDB\", ...],"
            "\n  \"infrastructure\": [\"Docker\", \"Kubernetes\", \"AWS\", \"NVIDIA Jetson\", ...],"
            "\n  \"developer_tools\": [\"Git\", \"Linux\", \"CI/CD\", \"MLflow\", ...],"
            "\n  \"domain_specific_skills\": [\"MAVLink\", \"PX4\", \"Gazebo SITL\", \"Object Tracking\", ...],"
            "\n  \"concepts\": [\"Computer Vision\", \"Deep Learning\", \"API Design\", \"Edge Deployment\", ...],"
            "\n  \"problem_solving\": {{ \"required\": true/false, \"signals\": [\"LeetCode\", \"Codeforces\", \"Hackathons\"] }},"
            "\n  \"evaluation_signals\": {{ \"github\": [\"Project Ownership\", \"Commits\"] }},"
            "\n  \"strict_requirements\": [\"Python\", \"OpenCV\", ...all skills listed as Required],"
            "\n  \"soft_requirements\": [\"Docker\", \"TensorRT\", ...all skills listed as Good to have/Bonus],"
            "\n  \"excluded_signals\": [\"Formal Job Experience\", \"College Pedigree\"],"
            "\n  \"matching_philosophy\": {{ \"partial_matches_allowed\": true/false, \"evidence_over_claims\": true/false, \"learning_velocity_weight\": 0.1-0.3 }}"
            "\n}}"
        )


    def extract(self, description, title=""):
        """Extract v2 structured intelligence from JD."""
        if self.model is None:
            print("[MOCK] Simulating extraction for placeholder key...")
            return {
                "role": title,
                "seniority": "mid",
                "languages": ["JavaScript", "TypeScript"],
                "frontend_frameworks": ["React"],
                "backend_frameworks": ["Node.js"],
                "databases": ["PostgreSQL"],
                "matching_philosophy": {"learning_velocity_weight": 0.2}
            }

        clean_text = re.sub(r'\s+', ' ', description).strip()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_instructions),
            ("human", "Role Title: {title}\n\nJob Description: {content}")
        ])
        
        chain = prompt | self.model
        
        start_time = time.time()
        try:
            print(f"Applying Intelligence v2 (OpenRouter/Claude) to job: {title}...")
            response = chain.invoke({"title": title, "content": clean_text})
            # ChatOpenAI returns a message object, content contains the JSON string
            json_text = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"OpenRouter Extraction Error: {e}")
            return {"required_skills": [], "error": str(e)}

        end_time = time.time()
        print(f"--- Intelligence extraction completed in {end_time - start_time:.2f} seconds ---")
        
        try:
            return json.loads(json_text)
        except Exception as e:
            print(f"v3 Parse Error: {e}")
            print(f"Raw Response: {json_text}")
            return {"error": "Intelligence parse failed"}