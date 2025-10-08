import streamlit as st
from llm_processor_for_app import parse_process_description, extract_json_from_response, get_llm
from high_quality_generator import generate_high_quality_pfd_image  # Updated import
from pfd_analyzer import analyze_uploaded_pfd, analyze_pfd_image
from PIL import Image
import base64
from io import BytesIO
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time

# Increase image pixel limit to avoid decompression bomb warnings
Image.MAX_IMAGE_PIXELS = 200000000

def main():
    st.title("🏭 AI-Powered PFD Generator & Analyzer")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose a feature:",
        ["PFD Generator", "PFD Analyzer", "PFD Verifier"]  # Added PFD Verifier option
    )
    
    if page == "PFD Generator":
        pfd_generator_page()
    elif page == "PFD Analyzer":
        pfd_analyzer_page()
    else:  # PFD Verifier
        pfd_verifier_page()
def pfd_analyzer_page():
    st.header("🔍 PFD Analyzer")
    st.subheader("Upload a PFD image and ask questions about it!")
    
    # Initialize session state for uploaded PFD chat
    if 'uploaded_pfd_image' not in st.session_state:
        st.session_state.uploaded_pfd_image = None
    if 'uploaded_pfd_chat_history' not in st.session_state:
        st.session_state.uploaded_pfd_chat_history = []
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload PFD Image", 
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of your Process Flow Diagram"
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.session_state.uploaded_pfd_image = image
        st.image(image, caption="Uploaded PFD", use_column_width=True)
        
        # Display chat messages
        for message in st.session_state.uploaded_pfd_chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Create columns for predefined questions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Explain Process Flow", key="explain_flow_btn"):
                question = "Can you explain how this process works from feed to product?"
                
                # Add user message to chat
                st.session_state.uploaded_pfd_chat_history.append({
                    "role": "user",
                    "content": question
                })
                
                with st.spinner("Analyzing PFD..."):
                    try:
                        answer = analyze_pfd_image(image, question)
                        
                        # Add AI response to chat
                        st.session_state.uploaded_pfd_chat_history.append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                        # Rerun to update the chat
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        with col2:
            if st.button("Safety Analysis", key="safety_analysis_btn"):
                question = "What safety considerations should I be aware of in this process?"
                
                # Add user message to chat
                st.session_state.uploaded_pfd_chat_history.append({
                    "role": "user",
                    "content": question
                })
                
                with st.spinner("Analyzing PFD..."):
                    try:
                        answer = analyze_pfd_image(image, question)
                        
                        # Add AI response to chat
                        st.session_state.uploaded_pfd_chat_history.append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                        # Rerun to update the chat
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        with col3:
            if st.button("Optimization Tips", key="optimization_tips_btn"):
                question = "How can this process be optimized for energy efficiency?"
                
                # Add user message to chat
                st.session_state.uploaded_pfd_chat_history.append({
                    "role": "user",
                    "content": question
                })
                
                with st.spinner("Analyzing PFD..."):
                    try:
                        answer = analyze_pfd_image(image, question)
                        
                        # Add AI response to chat
                        st.session_state.uploaded_pfd_chat_history.append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                        # Rerun to update the chat
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Question input
        question_input = st.text_input(
            "Ask a question about the PFD:",
            placeholder="What would you like to know about this PFD?",
            key="question_text_input"
        )
        
        if st.button("Send Question", key="send_question_analyzer_btn"):
            if question_input and st.session_state.uploaded_pfd_image:
                # Add user message to chat
                st.session_state.uploaded_pfd_chat_history.append({
                    "role": "user",
                    "content": question_input
                })
                
                with st.spinner("Analyzing PFD..."):
                    try:
                        answer = analyze_pfd_image(st.session_state.uploaded_pfd_image, question_input)
                        
                        # Add AI response to chat
                        st.session_state.uploaded_pfd_chat_history.append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                        # Rerun to update the chat
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            elif not st.session_state.uploaded_pfd_image:
                st.warning("Please upload a PFD image first")
            else:
                st.warning("Please enter a question")
    
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
def pfd_generator_page():
    st.header("🤖 PFD Generator")
    st.subheader("Describe your process in natural language, and AI will generate the PFD!")
    
    # Initialize session state
    if 'generated_pfd' not in st.session_state:
        st.session_state.generated_pfd = None
    if 'process_data' not in st.session_state:
        st.session_state.process_data = None
    if 'generated_pfd_image' not in st.session_state:
        st.session_state.generated_pfd_image = None
    if 'pfd_text_description' not in st.session_state:
        st.session_state.pfd_text_description = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_generation_form' not in st.session_state:
        st.session_state.show_generation_form = True
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if "download_button" in message and message["download_button"]:
                # Display message content
                st.write(message["content"])
                # Add download button
                st.download_button(
                    label="📥 Download PFD",
                    data=message["image_data"],
                    file_name=message["filename"],
                    mime="image/png",
                    key=message.get("key", f"download_{id(message)}")
                )
            elif "image" in message and message["image"]:
                st.image(message["image"], caption=message.get("caption", "Generated PFD"), use_column_width=True)
            elif "process_summary" in message:
                # Display process summary
                st.write(message["content"])
                
                # Count equipment and streams for quality info
                num_equipment = len(message["process_data"]['equipment'])
                num_streams = len(message["process_data"]['streams'])
                
                # Analyze for recycling
                process_streams = message["process_data"]['streams']
                recycles = set()
                for stream in process_streams:
                    for other_stream in process_streams:
                        if stream['to'] == other_stream['from'] and stream['from'] == other_stream['to']:
                            pair = tuple(sorted([stream['from'], stream['to']]))
                            recycles.add(pair)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Equipment Count", num_equipment)
                with col2:
                    st.metric("Stream Count", num_streams)
                with col3:
                    st.metric("Recycle Loops", len(recycles))
                
                st.subheader("Equipment")
                for equip in message["process_data"]['equipment']:
                    st.write(f"**{equip['id']}**: {equip['type']} - {equip['spec']}")
                    
                    # Show parameters if available
                    params = []
                    if 'temperature' in equip and equip['temperature']:
                        params.append(f"T: {equip['temperature']}°C")
                    if 'pressure' in equip and equip['pressure']:
                        params.append(f"P: {equip['pressure']} bar")
                    if 'flow_rate' in equip and equip['flow_rate']:
                        params.append(f"Flow: {equip['flow_rate']} kg/hr")
                    if 'duty' in equip and equip['duty']:
                        params.append(f"Duty: {equip['duty']} kW")
                    if 'efficiency' in equip and equip['efficiency']:
                        params.append(f"Eff: {equip['efficiency']}%")
                    if 'stages' in equip and equip['stages']:
                        params.append(f"Stages: {equip['stages']}")
                    
                    if params:
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;Parameters: {', '.join(params)}")
            elif "streams" in message:
                # Display streams
                st.write(message["content"])
                
                # Analyze for recycling
                process_streams = message["process_data"]['streams']
                recycles = set()
                for stream in process_streams:
                    for other_stream in process_streams:
                        if stream['to'] == other_stream['from'] and stream['from'] == other_stream['to']:
                            pair = tuple(sorted([stream['from'], stream['to']]))
                            recycles.add(pair)
                
                for stream in process_streams:
                    stream_pair = tuple(sorted([stream['from'], stream['to']]))
                    is_recycle = stream_pair in recycles
                    if is_recycle:
                        st.write(f"**🔄 {stream['id']}**: {stream['from']} → {stream['to']} ({stream['flow']} units) [RECYCLE]")
                    else:
                        st.write(f"**{stream['id']}**: {stream['from']} → {stream['to']} ({stream['flow']} units)")
                    
                    # Show stream parameters
                    params = []
                    if 'temperature' in stream and stream['temperature']:
                        params.append(f"T: {stream['temperature']}°C")
                    if 'pressure' in stream and stream['pressure']:
                        params.append(f"P: {stream['pressure']} bar")
                    if 'flow_rate' in stream and stream['flow_rate']:
                        params.append(f"Flow: {stream['flow_rate']} kg/hr")
                    if 'composition' in stream and stream['composition']:
                        comp = stream['composition'][:20] + "..." if len(stream['composition']) > 20 else stream['composition']
                        params.append(f"Comp: {comp}")
                    
                    if params:
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;Parameters: {', '.join(params)}")
            elif "equipment" in message:
                # Display equipment
                st.write(message["content"])
                for equip in message["process_data"]['equipment']:
                    st.write(f"**{equip['id']}**: {equip['type']} - {equip['spec']}")
                    
                    # Show parameters if available
                    params = []
                    if 'temperature' in equip and equip['temperature']:
                        params.append(f"T: {equip['temperature']}°C")
                    if 'pressure' in equip and equip['pressure']:
                        params.append(f"P: {equip['pressure']} bar")
                    if 'flow_rate' in equip and equip['flow_rate']:
                        params.append(f"Flow: {equip['flow_rate']} kg/hr")
                    if 'duty' in equip and equip['duty']:
                        params.append(f"Duty: {equip['duty']} kW")
                    if 'efficiency' in equip and equip['efficiency']:
                        params.append(f"Eff: {equip['efficiency']}%")
                    if 'stages' in equip and equip['stages']:
                        params.append(f"Stages: {equip['stages']}")
                    
                    if params:
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;Parameters: {', '.join(params)}")
            else:
                st.write(message["content"])
    
    # Show generation form only if no PFD is generated or user wants to generate again
    if st.session_state.show_generation_form:
        # Process description input
        process_description = st.text_area(
            "Describe your process (e.g., 'Feed water is pumped from a tank to a heater, then to a distillation column where it's separated into top and bottom products')",
            height=150,
            placeholder="Example: Water from feed tank T-101 is pumped by P-101 to heat exchanger E-201, then to distillation column C-301 where vapor and liquid are separated..."
        )
        
        # Show example processes with recycling
        with st.expander("💡 Example processes with recycling (click to see examples)"):
            st.write("**Example 1:** Feed water is pumped from tank T-101 to pump P-101, then to heat exchanger E-201, then to reactor R-301. The reactor effluent goes to separator S-401 where 80% goes to product tank and 20% recycles back to pump P-101.")
            
            st.write("**Example 2:** Crude oil is pumped from feed tank to preheater, then to fractionator column. The bottom product is partially recycled back to the feed pump to improve heat recovery.")
            
            st.write("**Example 3:** Gas stream is compressed, cooled, and sent to absorption column. The lean solvent from the bottom is heated and sent to stripping column. The rich solvent from the top of stripping column is recycled back to absorption column.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate PFD with AI", type="primary") and process_description:
                with st.spinner("AI is analyzing your process description and generating PFD..."):
                    try:
                        # Parse process description using LLM
                        llm_response = parse_process_description(process_description)
                        if llm_response:
                            process_data = extract_json_from_response(llm_response)

                            if process_data:
                                st.session_state.process_data = process_data
                                
                                # Generate HIGH-QUALITY PFD image
                                pfd_image_bytes = generate_high_quality_pfd_image(process_data)
                                st.session_state.generated_pfd = pfd_image_bytes
                                
                                # Store the image for analysis
                                st.session_state.generated_pfd_image = Image.open(BytesIO(pfd_image_bytes))
                                
                                # Generate text description of the PFD for efficient chat
                                text_description = generate_text_description(process_data)
                                st.session_state.pfd_text_description = text_description
                                
                                # Add generated PFD to chat
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": "I've generated the PFD based on your description. Here it is:",
                                    "image": pfd_image_bytes,
                                    "caption": "AI-Generated PFD (Ultra High Quality)"
                                })
                                
                                # Add download button to chat
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": "📥 Download your PFD",
                                    "download_button": True,
                                    "image_data": pfd_image_bytes,
                                    "filename": f"ai_generated_pfd_ultra_{int(time.time())}.png",
                                    "key": f"download_{int(time.time() * 1000000)}"
                                })
                                
                                # Add success message to chat
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": "✅ Process data extracted successfully! You can now ask questions about your PFD."
                                })
                                
                                # Hide generation form
                                st.session_state.show_generation_form = False
                                
                                # Rerun to update the chat
                                st.rerun()
                                
                            else:
                                st.error("❌ Could not extract process data from description")
                        else:
                            st.error("❌ LLM response was empty")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col2:
            if st.button("Reset"):
                st.session_state.generated_pfd = None
                st.session_state.process_data = None
                st.session_state.generated_pfd_image = None
                st.session_state.pfd_text_description = ""
                st.session_state.chat_history = []
                st.session_state.show_generation_form = True
                st.rerun()
    
    # Chat section - always visible after PFD generation
    if not st.session_state.show_generation_form:
        # Create a chat input area 
        st.markdown("---")
        
        # Create columns for text input and send button
        col1, col2 = st.columns([9, 1])
        
        with col1:
            question_input = st.text_input("", key="question_input", placeholder="Ask a question about your PFD:")
        
        with col2:
            if st.button("↑", key="send_question_btn", help="Send question"):
                if question_input:
                    with st.spinner("Analyzing your PFD..."):
                        try:
                            # Add user message to chat history
                            st.session_state.chat_history.append({
                                "role": "user",
                                "content": question_input
                            })
                            
                            # Use text-based analysis for efficiency
                            answer = analyze_pfd_text(
                                st.session_state.pfd_text_description, 
                                question_input, 
                                st.session_state.chat_history,
                                st.session_state.generated_pfd_image  # Pass image for visual questions
                            )
                            
                            # Add AI response to chat history
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": answer
                            })
                            
                            # Rerun to update the chat
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error analyzing PFD: {str(e)}")
                else:
                    st.warning("Please enter a question")
        
        # Create columns for buttons
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
        
        with col1:
            if st.button("Generate New PFD", key="generate_new_pfd_btn"):
                # Clear only PFD-specific data, keep chat history
                st.session_state.generated_pfd = None
                st.session_state.process_data = None
                st.session_state.generated_pfd_image = None
                st.session_state.pfd_text_description = ""
                st.session_state.show_generation_form = True
                st.rerun()
        
        with col2:
            if st.button("Process Summary", key="process_summary_btn"):
                # Add user message to chat
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "Process Summary"
                })
                
                # Add process summary to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "### Process Summary",
                    "process_summary": True,
                    "process_data": st.session_state.process_data
                })
                
                # Rerun to update the chat
                st.rerun()
        
        with col3:
            if st.button("Equipment", key="equipment_btn"):
                # Add user message to chat
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "Equipment"
                })
                
                # Add equipment to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "### Equipment Details",
                    "equipment": True,
                    "process_data": st.session_state.process_data
                })
                
                # Rerun to update the chat
                st.rerun()
        
        with col4:
            if st.button("Streams", key="streams_btn"):
                # Add user message to chat
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "Streams"
                })
                
                # Add streams to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "### Stream Details",
                    "streams": True,
                    "process_data": st.session_state.process_data
                })
                
                # Rerun to update the chat
                st.rerun()
def generate_text_description(process_data):
    """Generate a text description of the PFD for efficient chat"""
    description = "Process Flow Diagram Description:\n\n"
    
    # Equipment
    description += "Equipment:\n"
    for equip in process_data['equipment']:
        description += f"- {equip['id']}: {equip['type']} - {equip['spec']}\n"
        # Add parameters
        params = []
        if 'temperature' in equip and equip['temperature']:
            params.append(f"T: {equip['temperature']}°C")
        if 'pressure' in equip and equip['pressure']:
            params.append(f"P: {equip['pressure']} bar")
        if 'flow_rate' in equip and equip['flow_rate']:
            params.append(f"Flow: {equip['flow_rate']} kg/hr")
        if 'duty' in equip and equip['duty']:
            params.append(f"Duty: {equip['duty']} kW")
        if 'efficiency' in equip and equip['efficiency']:
            params.append(f"Eff: {equip['efficiency']}%")
        if 'stages' in equip and equip['stages']:
            params.append(f"Stages: {equip['stages']}")
        if params:
            description += f"  Parameters: {', '.join(params)}\n"
    
    description += "\nStreams:\n"
    for stream in process_data['streams']:
        description += f"- {stream['id']}: {stream['from']} → {stream['to']} ({stream['flow']} units)\n"
        # Add stream parameters
        params = []
        if 'temperature' in stream and stream['temperature']:
            params.append(f"T: {stream['temperature']}°C")
        if 'pressure' in stream and stream['pressure']:
            params.append(f"P: {stream['pressure']} bar")
        if 'flow_rate' in stream and stream['flow_rate']:
            params.append(f"Flow: {stream['flow_rate']} kg/hr")
        if 'composition' in stream and stream['composition']:
            comp = stream['composition'][:30] + "..." if len(stream['composition']) > 30 else stream['composition']
            params.append(f"Comp: {comp}")
        if params:
            description += f"  Parameters: {', '.join(params)}\n"
    
    return description

def analyze_pfd_text(pfd_text, question, chat_history, image=None):
    """Analyze PFD using text description, with fallback to image when needed"""
    # Keywords that suggest visual analysis is needed
    visual_keywords = [
        # Layout and position
        'layout', 'position', 'location', 'top-left', 'top-right', 'bottom-left', 'bottom-right',
        'left side', 'right side', 'top side', 'bottom side', 'middle', 'center', 'corner',
        'arranged', 'placed', 'situated', 'oriented', 'direction', 'orientation',
        
        # Visual appearance
        'visually', 'appearance', 'shape', 'color', 'colored', 'look', 'looks like',
        'appears', 'seen', 'saw', 'see', 'view', 'perspective', 'diagram',
        
        # Spatial relationships
        'where is', 'next to', 'adjacent', 'beside', 'near', 'close to', 'far from',
        'above', 'below', 'under', 'over', 'across', 'between', 'surrounding',
        
        # Visual patterns
        'pattern', 'design', 'configuration', 'structure', 'form', 'layout',
        'alignment', 'symmetry', 'asymmetry', 'proportion', 'dimension',
        
        # Visual elements
        'symbol', 'icon', 'marking', 'label', 'text', 'font', 'size', 'scale',
        'line', 'arrow', 'connection', 'link', 'path', 'route',
        
        # Visual comparisons
        'bigger', 'smaller', 'larger', 'taller', 'wider', 'narrower', 'thicker', 'thinner',
        'compare', 'comparison', 'difference', 'similar', 'resemble', 'match',
        
        # Visual analysis
        'analyze visually', 'visual analysis', 'visual inspection', 'visual check',
        'examine visually', 'visual examination', 'visual review',
        
        # Specific visual queries
        'what does it look like', 'how does it look', 'visualize', 'visualization',
        'show me', 'point out', 'indicate', 'highlight', 'circle', 'mark',
        
        # Directional terms
        'horizontal', 'vertical', 'diagonal', 'parallel', 'perpendicular', 'angled',
        'upward', 'downward', 'forward', 'backward', 'sideways', 'circular',
        
        # Visual features
        'border', 'outline', 'edge', 'corner', 'surface', 'face', 'side',
        'front', 'back', 'top', 'bottom', 'interior', 'exterior'
    ]
    
    # Check if question requires visual analysis
    question_lower = question.lower()
    needs_visual = any(keyword in question_lower for keyword in visual_keywords)
    
    if needs_visual and image is not None:
        # Use image analysis for visual questions
        return analyze_pfd_image(image, question)
    else:
        # Use text analysis for efficiency with existing LLM processor
        try:
            llm = get_llm()
            
            # Format chat history for context (use last 12 queries)
            history_context = ""
            if chat_history:
                history_context = "Previous conversation:\n"
                for msg in chat_history[-12:]:  # Use last 12 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_context += f"{role}: {msg['content']}\n"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert chemical process engineer. You have detailed knowledge of Process Flow Diagrams (PFDs) and can answer questions about them. Use the provided PFD description to answer questions accurately. When relevant, consider:
            1. Equipment identification and function
            2. Process flow direction
            3. Stream connections and relationships
            4. Equipment specifications and parameters
            5. Process safety considerations
            6. Energy efficiency and optimization
            7. Common industrial practices"""),
                ("human", f"""PFD Description:
{pfd_text}

{history_context}

Question: {question}

Please provide a detailed, accurate, and helpful answer.""")
            ])
            
            chain = prompt | llm | StrOutputParser()
            result = chain.invoke({})
            return result
            
        except Exception as e:
            return f"Error analyzing PFD: {str(e)}"
def pfd_verifier_page():
    st.header("✅ PFD Verifier")
    st.subheader("Upload your PFD and process description to verify correctness!")
    
    # Initialize session state for verifier
    if 'uploaded_pfd_for_verification' not in st.session_state:
        st.session_state.uploaded_pfd_for_verification = None
    if 'process_description_for_verification' not in st.session_state:
        st.session_state.process_description_for_verification = ""
    if 'verification_result' not in st.session_state:
        st.session_state.verification_result = None
    if 'verification_chat_history' not in st.session_state:
        st.session_state.verification_chat_history = []
    
    col1, col2 = st.columns(2)
    
    with col1:
        # File uploader for PFD
        uploaded_pfd = st.file_uploader(
            "Upload PFD Image", 
            type=['png', 'jpg', 'jpeg'],
            key="verifier_pfd_upload",
            help="Upload a clear image of your Process Flow Diagram"
        )
        
        if uploaded_pfd is not None:
            image = Image.open(uploaded_pfd)
            st.image(image, caption="Uploaded PFD", use_column_width=True)
            st.session_state.uploaded_pfd_for_verification = image

    with col2:
        # Process description input
        process_description = st.text_area(
            "Process Description:",
            value=st.session_state.process_description_for_verification,
            height=200,
            placeholder="Describe your process (e.g., 'Feed water is pumped from a tank to a heater, then to a distillation column...')",
            key="verifier_process_desc"
        )
        st.session_state.process_description_for_verification = process_description
    
    # Verify button
    if st.button("Verify PFD Against Process Description"):
        if st.session_state.uploaded_pfd_for_verification and st.session_state.process_description_for_verification:
            with st.spinner("Verifying PFD against process description..."):
                try:
                    # Create verification question
                    verification_question = f"Verify if this PFD matches the following process description: {st.session_state.process_description_for_verification}. Identify any discrepancies, missing equipment, or incorrect connections."
                    
                    # Add verification request to chat
                    st.session_state.verification_chat_history.append({
                        "role": "user",
                        "content": verification_question
                    })
                    
                    # Analyze the PFD with the verification question
                    verification_result = analyze_pfd_image(
                        st.session_state.uploaded_pfd_for_verification, 
                        verification_question
                    )
                    
                    # Add verification result to chat
                    st.session_state.verification_chat_history.append({
                        "role": "assistant",
                        "content": verification_result
                    })
                    
                    st.success("Verification Complete!")
                    
                    # Rerun to update the chat
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error during verification: {str(e)}")
        else:
            st.warning("Please upload both PFD image and process description")
    
    # Display chat history
    for message in st.session_state.verification_chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat section for additional questions
    if st.session_state.uploaded_pfd_for_verification:
        # Input for new question
        verification_question_input = st.text_input(
            "Ask any other questions about your PFD:", 
            key="verifier_question_input"
        )
        
        if st.button("Send Question", key="verifier_send_btn"):
            if verification_question_input:
                with st.spinner("Analyzing your PFD..."):
                    try:
                        # Add user message to chat history
                        st.session_state.verification_chat_history.append({
                            "role": "user",
                            "content": verification_question_input
                        })
                        
                        # For uploaded PFDs, we still need to use image analysis
                        answer = analyze_pfd_image(
                            st.session_state.uploaded_pfd_for_verification, 
                            verification_question_input
                        )
                        
                        # Add AI response to chat history
                        st.session_state.verification_chat_history.append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                        # Rerun to update the chat
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error analyzing PFD: {str(e)}")
            else:
                st.warning("Please enter a question")
    
    # Reset button
    if st.button("Reset Verification"):
        st.session_state.uploaded_pfd_for_verification = None
        st.session_state.process_description_for_verification = ""
        st.session_state.verification_result = None
        st.session_state.verification_chat_history = []
        st.rerun()


if __name__ == "__main__":
    main()