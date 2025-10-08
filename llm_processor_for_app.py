from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Initialize LLM"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY in environment variables")
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1, api_key=api_key)

def parse_process_description(process_description):
    """Use LLM to parse natural language process description with structured output"""
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """# Add this to the system prompt after the JSON structure example
Process Analysis Guidelines:
- If the user provides a detailed process description, use the provided information directly to create the JSON structure
- If the user provides minimal information or only requests to generate a specific process type (e.g., "generate a distillation process"), then internally develop a detailed process understanding including:
  1. Complete process steps and sequence
  2. All major equipment required
  3. Process conditions (temperature, pressure, flow rates)
  4. Utility requirements
  5. Safety and control systems
  6. Environmental considerations
  7. Process optimization opportunities
  8. Show the source also from where initally its coming (may be like source drum also or any unit product)

In both cases, return only the JSON structure to the user. The internal process development should only inform the JSON creation and not be shown to the user.

For industry-level PFDs, ensure to include realistic equipment specifications, operating conditions, and safety features based on the process type.
For industry-level PFDs, ensure to include:
1. Multiple process units with proper interconnections
2. Utility streams (steam, cooling water, etc.)
3. Control and safety systems (PSV, control valves)
4. Proper equipment sizing indicators
5. All major process streams with compositions
6. Heat and material balances where relevant
7. Proper recycling and purge streams
8. Energy integration opportunities
9. Safety and environmental considerations
10. Standard industrial equipment configurations



If the user only requests to generate a specific process without detailed information, infer a complete industrial process based on typical configurations for that process type. Include realistic equipment specifications, operating conditions, and safety features that would be found in actual industrial plants.
        {{
            "equipment": [
                {{"type": "pump", "id": "P-101", "spec": "Feed Pump"}},
                {{"type": "heat_exchanger", "id": "E-201", "spec": "Feed Heater"}},
                {{"type": "distillation_column", "id": "C-301", "spec": "Main Column"}}
            ],
            "streams": [
                {{"id": "S1", "from": "T-101", "to": "P-101", "flow": 100, "comp": "Water"}}, 
                {{"id": "S2", "from": "P-101", "to": "E-201", "flow": 100, "comp": "Water"}},
                {{"id": "S3", "from": "E-201", "to": "C-301", "flow": 100, "comp": "Water"}},
                {{"id": "S4", "from": "C-301", "to": "P-101", "flow": 15, "comp": "Recycle Stream"}}
            ]
        }}
        
        Guidelines for structured output:
        1. Organize equipment in logical process order (feed → pre-treatment → main process → separation → product)
        2. Keep recycling streams to minimum necessary (5-25% of main flow typically)
        3. Use clear, sequential naming (T-101, P-101, E-201, C-301, etc.)
        4. Limit to maximum 8-10 main equipment pieces for clean visualization
        5. Group related equipment together when possible
        6. Clearly identify recycling/recirculation loops
        7. Use standard chemical engineering equipment types:
           - Pumps: P-xxx
           - Heat Exchangers: E-xxx  
           - Columns: C-xxx
           - Tanks: T-xxx
           - Reactors: R-xxx
           - Compressors: K-xxx
           - Separators: S-xxx
        Include temperature and pressure values for each equipment and stream based on typical operating conditions for that equipment type:
        - Tanks: Ambient temperature (20-30°C), atmospheric pressure (1 bar)
        - Pumps: Slight temperature rise (25-35°C), increased pressure (1-10 bar)
        - Heat Exchangers: Inlet temperature to outlet temperature range, pressure drop of 0.1-0.5 bar
        - Distillation Columns: Reboiler temperature (100-300°C), operating pressure (0.5-5 bar)
        - Reactors: Reaction temperature and pressure based on reaction type
        - Compressors: Temperature rise due to compression, high pressure (3-30 bar)
         If specific values are mentioned in the process description, use those values. Otherwise, infer reasonable values based on the process and equipment type.        Pay special attention to identifying:
        - Main process flow (primary direction)
        - Recycle streams (feedback to earlier equipment)
        - Product streams (final outputs)
        - Utility connections (if mentioned)
        
        Ensure the structure will create a clean, readable flow diagram without excessive crossing lines."""),

        ("human", "Process Description: {process_desc}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        result = chain.invoke({"process_desc": process_description})
        return result
    except Exception as e:
        raise Exception(f"LLM processing error: {str(e)}")

def extract_json_from_response(response_text):
    """Extract JSON from LLM response"""
    try:
        import json
        # Find JSON in response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = response_text[start:end]
            return json.loads(json_str)
    except:
        # If JSON parsing fails, create a simple structure
        return {
            "equipment": [{"type": "tank", "id": "T-101", "spec": "Generic Tank"}],
            "streams": [{"id": "S1", "from": "T-101", "to": "T-101", "flow": 100, "comp": "Generic Stream"}]
        }
    return None
