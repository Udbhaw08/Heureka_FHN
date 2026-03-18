import os
import json
import re
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class JobBiasAgent:
    def __init__(self, model_name=None):
        """Initializes the agent with OpenRouter Claude for speed and accuracy."""
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = "https://openrouter.ai/api/v1"
        model_to_use = model_name or os.getenv("LLM_MODEL", "anthropic/claude-3-haiku")
        
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
        
        # Double curly braces {{ }} are used to prevent LangChain KeyErrors
        self.system_instructions = (
            "You are an objective AI Audit Agent. Analyze the provided Job Description (JD) text for socio-economic, educational, or demographic biases."
            "\nFocus on factual identification of biased language, regardless of text length."
            
            "\n\n--- THE 'NEUTRAL' LIST (DO NOT FLAG) ---"
            "\n- Technical Skills: 'Java', 'Python', 'AWS', 'Automation', 'Coding'."
            "\n- Professionalism: 'Technical competence', 'Senior', '7 years experience'."
            "\n- These are requirements, NOT biases. bias_score: 0."

            "\n\n--- THE 'BIAS' LIST (FLAG THESE) ---"
            "\n- Gender/Identity: 'girl', 'boy', 'male preferred', 'female candidate', 'men only'."
            "\n- Social Elitism: 'Ivy League', 'Top-tier university', 'Elite school'."
            "\n- Demographic Proxies: 'Digital Native', 'Fresh blood', 'Rockstar', 'Ninja'."
            "\n- Mismatches: Requiring a 'Physics degree' for a Sales role."

            "\n\n--- LOGIC RULE ---"
            "\n- If you find ANY phrase from the 'Bias' list (especially explicit gender requests), the bias_score MUST be 8-10."
            "\n- If you find NO bias, return bias_score: 0 and findings: []."
            
            "\n\n--- OUTPUT FORMAT ---"
            "\nReturn ONLY valid JSON. Your entire response must be a single JSON object."
            "\n{{ \"bias_score\": <int>, \"reasoning\": \"...\", \"findings\": [{{ \"phrase\": \"...\", \"category\": \"...\", \"fix\": \"...\" }}] }}"
        )

    def analyze(self, raw_text):
        """Main method to perform bias detection. All variables are scoped here."""
        # 1. Prepare the text
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # 2. Define the prompt and chain
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_instructions),
            ("human", "Audit this JD for Bias: {content}")
        ])
        
        chain = prompt | self.model
        
        # 3. Execution
        start_time = time.time()
        try:
            response_obj = chain.invoke({"content": clean_text})
            response = response_obj.content if hasattr(response_obj, 'content') else str(response_obj)
        except Exception as e:
             # Fallback if AI service is unavailable
             print(f"LLM Error: {e}")
             return {"bias_score": 0, "reasoning": "Error connecting to AI service", "findings": []}

        end_time = time.time()
        print(f"--- Audit completed in {end_time - start_time:.2f} seconds ---")
        
        try:
            # 4. ROBUST JSON PARSING
            # Find the first { and last } to extract JSON block, even if preamble exists
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON object found in response")
            
            # 5. Logic Guard
            if not data.get("findings"):
                data["bias_score"] = 0
            elif data.get("bias_score") == 0 and data.get("findings"):
                data["bias_score"] = 5 
                
            return data
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw Response: {response}")
            
            # HEURISTIC FALLBACK: Check if response contains bias keywords
            bias_score = 0
            reasoning = f"Failed to parse AI response. Raw: {response[:50]}..."
            findings = []
            
            if any(word in response.lower() for word in ["gender", "girl", "male", "female", "bias", "discrimination"]):
                bias_score = 8
                reasoning = "Bias detected but AI response was not in perfect format."
                findings = [{"phrase": raw_text, "category": "General Bias", "fix": "Rewrite to be gender-neutral."}]
                
            return {"bias_score": bias_score, "reasoning": reasoning, "findings": findings}
