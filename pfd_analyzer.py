import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
Image.MAX_IMAGE_PIXELS = 200000000

def analyze_pfd_image(image, question):
    """Analyze PFD image and answer questions about it"""
    try:
        # Convert image to base64 for API
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Please set GOOGLE_API_KEY in environment variables")
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1, api_key=api_key)
        
        # Create a prompt that combines image analysis with PFD knowledge
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert chemical process engineer. You can analyze Process Flow Diagrams (PFDs) and answer questions about them. When analyzing PFDs, consider:
            1. Equipment identification and function
            2. Process flow direction
            3. Stream connections and relationships
            4. Equipment specifications and parameters
            5. Process safety considerations
            6. Energy efficiency and optimization
            7. Common industrial practices
            
            Provide detailed, accurate, and helpful answers to questions about PFDs."""),
            ("human", [
                {"type": "text", "text": f"Analyze this PFD image and answer the following question: {question}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
            ])
        ])
        
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({})
        return result
        
    except Exception as e:
        return f"Error analyzing PFD: {str(e)}"

def suggest_equipment_improvements(equipment_type, current_specs=None):
    """Provide suggestions for equipment improvements"""
    improvements = {
        'pump': {
            'advantages': [
                'Variable speed drives for energy savings',
                'Improved impeller design for higher efficiency',
                'Better materials for corrosion resistance',
                'Smart monitoring systems'
            ],
            'disadvantages': [
                'Higher initial cost',
                'Complexity in control systems',
                'Requires skilled maintenance'
            ],
            'alternatives': [
                'Positive displacement pumps for high viscosity',
                'Centrifugal pumps for high flow rates',
                'Peristaltic pumps for shear-sensitive fluids'
            ]
        },
        'heat_exchanger': {
            'advantages': [
                'Plate heat exchangers for compact design',
                'Enhanced surface area for better heat transfer',
                'Fouling-resistant materials',
                'Thermal expansion compensation'
            ],
            'disadvantages': [
                'Higher pressure drop',
                'Gasket maintenance requirements',
                'Potential for leakage'
            ],
            'alternatives': [
                'Spiral heat exchangers for viscous fluids',
                'Air-cooled heat exchangers for water scarcity',
                'Double pipe heat exchangers for small applications'
            ]
        },
        'distillation_column': {
            'advantages': [
                'Structured packing for higher efficiency',
                'Advanced control systems',
                'Heat integration with other units',
                'Improved tray designs'
            ],
            'disadvantages': [
                'High energy consumption',
                'Complex control requirements',
                'Large footprint'
            ],
            'alternatives': [
                'Packed columns for lower pressure drop',
                'Extractive distillation for azeotropes',
                'Pressure swing distillation for separation'
            ]
        },
        'compressor': {
            'advantages': [
                'Variable speed drives for capacity control',
                'Improved blade design for efficiency',
                'Advanced sealing systems',
                'Condition monitoring capabilities'
            ],
            'disadvantages': [
                'High power consumption',
                'Vibration and noise',
                'Complex maintenance'
            ],
            'alternatives': [
                'Centrifugal for high flow, low pressure',
                'Reciprocating for high pressure, low flow',
                'Screw compressors for medium applications'
            ]
        }
    }
    
    return improvements.get(equipment_type.lower(), {
        'advantages': ['Efficiency improvements', 'Smart monitoring', 'Material upgrades'],
        'disadvantages': ['Higher cost', 'Complexity', 'Maintenance needs'],
        'alternatives': ['Alternative equipment types available']
    })

def analyze_process_flow(process_description):
    """Analyze process flow for optimization"""
    analysis = {
        'energy_efficiency': [
            'Heat integration opportunities',
            'Pressure drop optimization',
            'Equipment efficiency improvements'
        ],
        'safety_considerations': [
            'Emergency shutdown systems',
            'Pressure relief provisions',
            'Material compatibility checks'
        ],
        'optimization_opportunities': [
            'Recycle stream optimization',
            'Utility consumption reduction',
            'Process intensification possibilities'
        ]
    }
    return analysis

def analyze_uploaded_pfd():
    st.title("🔍 PFD Image Analyzer")
    st.subheader("Upload a PFD image and ask questions about it!")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload PFD Image", 
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of your Process Flow Diagram"
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded PFD", use_container_width=True)  # Updated parameter
        
        # Question input
        question = st.text_area(
            "Ask a question about the PFD:",
            placeholder="Examples:\n- What is the purpose of this equipment?\n- How does this process work?\n- What are the safety considerations?\n- Can you suggest improvements for this heat exchanger?",
            height=100
        )
        
        # Predefined questions for quick access
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Explain Process Flow"):
                question = "Can you explain how this process works from feed to product?"
        with col2:
            if st.button("Safety Analysis"):
                question = "What safety considerations should I be aware of in this process?"
        with col3:
            if st.button("Optimization Tips"):
                question = "How can this process be optimized for energy efficiency?"
        
        if question:
            with st.spinner("Analyzing PFD and preparing answer..."):
                try:
                    answer = analyze_pfd_image(image, question)
                    st.success("Analysis Complete!")
                    st.write("### Answer:")
                    st.write(answer)
                    
                    # If question is about equipment improvements
                    if "improve" in question.lower() or "replace" in question.lower() or "alternative" in question.lower():
                        # Extract equipment type from question
                        import re
                        equipment_types = ['pump', 'compressor', 'heat exchanger', 'distillation column', 'reactor', 'separator', 'tank']
                        found_equipment = None
                        for eq_type in equipment_types:
                            if eq_type in question.lower():
                                found_equipment = eq_type
                                break
                        
                        if found_equipment:
                            improvements = suggest_equipment_improvements(found_equipment)
                            with st.expander("Equipment Improvement Suggestions"):
                                st.write("### Advantages:")
                                for adv in improvements['advantages']:
                                    st.write(f"- {adv}")
                                
                                st.write("### Disadvantages:")
                                for disadv in improvements['disadvantages']:
                                    st.write(f"- {disadv}")
                                
                                st.write("### Alternatives:")
                                for alt in improvements['alternatives']:
                                    st.write(f"- {alt}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    else:
        st.info("Please upload a PFD image to start analysis")
        
        # Show example questions
        with st.expander("💡 Example Questions You Can Ask"):
            st.write("""
            **Process Understanding:**
            - How does this process work step by step?
            - What is the purpose of each piece of equipment?
            - Can you explain the flow sequence?
            
            **Equipment Analysis:**
            - What type of heat exchanger is this?
            - How does this distillation column work?
            - What pump type is shown here?
            
            **Improvement Suggestions:**
            - How can I improve the efficiency of this heat exchanger?
            - What are alternatives to this compressor?
            - Can this process be optimized?
            
            **Safety & Operations:**
            - What safety features should be included?
            - What are the operational challenges?
            - How to maintain this equipment?
            """)

def main():
    analyze_uploaded_pfd()

if __name__ == "__main__":
    main()