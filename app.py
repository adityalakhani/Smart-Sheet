import streamlit as st
import logging
from datetime import datetime
import json
from typing import Dict, Any

from orchestrator import InterviewOrchestrator
from config import Config
from utils.tool_logger import tool_logger_instance

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Adaptive Excel Skills Assessment",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    if "interview_active" not in st.session_state:
        st.session_state.interview_active = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "candidate_name" not in st.session_state:
        st.session_state.candidate_name = ""
    if "interview_completed" not in st.session_state:
        st.session_state.interview_completed = False
    if "excel_skill_focus" not in st.session_state:
        st.session_state.excel_skill_focus = []
    if "current_dataset" not in st.session_state:
        st.session_state.current_dataset = None
    if "confirming_reset" not in st.session_state:
        st.session_state.confirming_reset = False

def display_header():
    """Display adaptive header"""
    st.title("Adaptive Microsoft Excel Skills Assessment")
    st.markdown("### AI-Powered Response-Driven Interview System")
    
    st.markdown("""
        ### Adaptive Features:

        - **Response-Driven Questions** - Questions adapt based on your performance  
        - **Dynamic Difficulty Adjustment** - Assessment level changes based on your demonstrated skills  
        - **Personalized Learning Path** - Each candidate gets a unique question sequence  
        - **Real-Time Skill Discovery** - System identifies strengths and areas for improvement  
        - **Contextual Dataset Generation** - Realistic business data matched to each scenario  

        ---

        ### Assessment Format:

        - **Adaptive Questioning** - No fixed sequence; questions generated based on your responses  
        - **Performance-Based Trajectory** - Assessment path changes based on demonstrated capabilities  
        - **Case-Based Scenarios** - Realistic business situations requiring Excel solutions  
        - **Methodology Focus** - Explain your approach; no software execution required  
        - **Intelligent Question Generation** - Maximum of 2 questions prepared at a time  
        - **Comprehensive Coverage** - Tests formulas, pivot tables, data analysis, and more  
    """)

def display_sidebar():
    """Display adaptive sidebar"""
    with st.sidebar:
        st.header("Adaptive Assessment Setup")
        
        # Excel skill focus areas
        st.subheader("Excel Skill Preferences")
        skill_options = [
            "Basic Formulas & Functions",
            "Data Manipulation & Cleaning", 
            "VLOOKUP & Lookup Functions",
            "Pivot Tables & Analysis",
            "Data Visualization", 
            "Advanced Functions",
            "Error Handling & Validation",
            "Conditional Logic"
        ]
        
        if not st.session_state.interview_started:
            st.session_state.candidate_name = st.text_input(
                "Your Name", 
                value=st.session_state.candidate_name,
                placeholder="Enter your full name"
            )
            
            role_context = st.selectbox(
                "Role Context",
                ["Business Analyst", "Data Analyst", "Financial Analyst", 
                 "Project Manager", "Operations Manager", "General Business User"],
                index=0
            )
            
            proficiency_level = st.selectbox(
                "Initial Proficiency Level",
                ["Beginner", "Intermediate", "Advanced", "Mixed Assessment"],
                index=3,
                help="Starting point for adaptive assessment - system will adjust based on your responses"
            )
            
            st.session_state.excel_skill_focus = st.multiselect(
                "Areas of Interest (optional)",
                skill_options,
                default=[],
                help="Optional focus areas - system will adapt based on performance"
            )
            
            st.subheader("Adaptive Configuration")
            max_questions = st.slider(
                "Maximum Questions", 
                6, 15, 10,
                help="Upper limit - actual number depends on your responses"
            )
            include_datasets = st.checkbox(
                "Enable Contextual Datasets", 
                True, 
                help="Generate realistic datasets for each question scenario"
            )
            
            if st.button("Start Adaptive Assessment", 
                        type="primary", 
                        disabled=not st.session_state.candidate_name.strip()):
                start_adaptive_assessment(role_context, proficiency_level, max_questions, include_datasets)
        
        else:
            # Assessment in progress
            st.write(f"**Candidate:** {st.session_state.candidate_name}")
            
            # Adaptive progress tracking
            if st.session_state.orchestrator:
                progress = st.session_state.orchestrator.get_progress()
                
                st.write(f"**Questions Completed:** {progress['questions_completed']}")
                st.write(f"**Current Question:** {progress['current_question_number']}")
                st.write(f"**Assessment Mode:** Adaptive")
                
                # Current skill and adaptive info
                if st.session_state.current_question:
                    skill = st.session_state.current_question.get('skill_target', 'N/A')
                    difficulty = st.session_state.current_question.get('difficulty', 'N/A')
                    has_dataset = st.session_state.current_question.get('requires_dataset', False)
                    
                    st.write(f"**Current Focus:** {skill}")
                    st.write(f"**Difficulty:** {difficulty}")
                    if has_dataset:
                        st.write("**Dataset:** Available")
                    
                    # Display dataset toggle
                    if has_dataset and st.button("View Current Dataset"):
                        load_current_dataset()
                
                # Adaptive insights
                if 'candidate_profile' in progress:
                    profile = progress['candidate_profile']
                    st.markdown("**Adaptive Profile:**")
                    st.write(f"- Preferred Level: {profile.get('preferred_difficulty', 'Determining')}")
                    st.write(f"- Strengths: {len(profile.get('strengths', []))}")
                    st.write(f"- Focus Areas: {len(profile.get('areas_needing_focus', []))}")
                    st.write(f"- Trend: {progress.get('performance_trend', 'Analyzing').title()}")
                    st.write(f"- Adaptations: {progress.get('trajectory_decisions', 0)}")
            
            # Assessment controls
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Hint", disabled=not st.session_state.current_question):
                    provide_methodology_hint()
            
            with col2:
                # Check if we are in the confirmation state for resetting
                if st.session_state.get('confirming_reset', False):
                    # Show Confirm and Cancel buttons
                    if st.button("Confirm Reset", type="primary"):
                        st.session_state.confirming_reset = False
                        reset_assessment()
                    if st.button("Cancel"):
                        st.session_state.confirming_reset = False
                        st.rerun()
                else:
                    # Show the initial Reset button
                    if st.button("Reset", type="secondary"):
                        st.session_state.confirming_reset = True
                        st.rerun()
        
        # System information
        st.markdown("---")
        st.subheader("System Status")
        
        if st.button("Tool Performance"):
            show_tool_performance()
        
        st.write("**AI Model:** Gemini 2.0 Flash")
        st.write("**Mode:** Adaptive Assessment")
        st.write("**Question Generation:** Dynamic")
        st.write("**Status:** Ready")

def start_adaptive_assessment(role_context: str, proficiency_level: str, 
                             max_questions: int, include_datasets: bool):
    """Initialize adaptive assessment"""
    try:
        with st.spinner("Initializing Adaptive Excel Assessment System..."):
            # Initialize adaptive orchestrator
            st.session_state.orchestrator = InterviewOrchestrator()
            
            # Start adaptive interview
            result = st.session_state.orchestrator.start_interview(
                candidate_name=st.session_state.candidate_name,
                role_type=role_context,
                difficulty_level=proficiency_level,
                excel_focus_areas=st.session_state.excel_skill_focus,
                max_questions=max_questions,
                include_datasets=include_datasets
            )
            
            if result["success"]:
                st.session_state.interview_active = True
                st.session_state.interview_started = True
                st.session_state.current_question = result.get("first_question")
                
                # Adaptive welcome message
                welcome_msg = result.get("welcome_message", 
                    f"Welcome {st.session_state.candidate_name} to your adaptive Excel skills assessment!")
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": welcome_msg,
                    "type": "adaptive_welcome"
                })
                
                # Add first question with adaptive info
                if st.session_state.current_question:
                    question_text = st.session_state.current_question.get("question", "")
                    
                    question_entry = {
                        "role": "assistant", 
                        "content": question_text,
                        "type": "adaptive_question",
                        "question_data": st.session_state.current_question
                    }
                    
                    # Include dataset information
                    if st.session_state.current_question.get("dataset_info", {}).get("generated_successfully"):
                        question_entry["has_dataset"] = True
                        question_entry["dataset_info"] = st.session_state.current_question["dataset_info"]
                    
                    st.session_state.chat_history.append(question_entry)
                
                st.success(f"Adaptive Excel assessment started! Questions will be generated based on your responses. Initial questions prepared: {result.get('questions_prepared', 2)}")
                st.rerun()
                
            else:
                st.error(f"Failed to start adaptive assessment: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        logger.error(f"Error starting adaptive Excel assessment: {str(e)}")
        st.error(f"Error starting assessment: {str(e)}")

def load_current_dataset():
    """Load and display the current question's dataset"""
    try:
        if st.session_state.orchestrator:
            dataset_result = st.session_state.orchestrator.get_current_question_dataset()
            if dataset_result["success"]:
                st.session_state.current_dataset = dataset_result
            else:
                st.error(f"Failed to load dataset: {dataset_result.get('error')}")
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")

def display_chat_interface():
    """Display adaptive chat interface with dataset support"""
    st.subheader("Adaptive Excel Assessment Conversation")
    
    # Chat container with adaptive styling
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            message_type = message.get("type", "general")
            
            with st.chat_message(message["role"]):
                if message_type == "adaptive_question":
                    # Adaptive question display
                    question_data = message.get("question_data", {})
                    
                    st.markdown(f"### Question {i//2 + 1}: {question_data.get('skill_target', 'Excel Challenge')}")
                    
                    if question_data.get("difficulty"):
                        difficulty_colors = {"Easy": "Green", "Medium": "Orange", "Hard": "Red"}
                        difficulty_color = difficulty_colors.get(question_data["difficulty"], "Gray")
                        st.markdown(f"**Difficulty:** {difficulty_color} {question_data['difficulty']}")
                    
                    # Show adaptive reasoning if available
                    if question_data.get("adaptive_reasoning"):
                        st.info(f"**Why this question:** {question_data['adaptive_reasoning']}")
                    
                    st.markdown(message["content"])
                    
                    # Dataset display
                    if message.get("has_dataset") and message.get("dataset_info", {}).get("generated_successfully"):
                        with st.expander("View Contextual Dataset", expanded=False):
                            dataset_info = message["dataset_info"]
                            
                            # Display context analysis
                            if dataset_info.get("context_analysis"):
                                context = dataset_info["context_analysis"]
                                st.info(f"**Dataset Context:** {context.get('question_type', 'Business Scenario')}")
                            
                            # Display HTML table
                            if dataset_info.get("html_table"):
                                st.markdown("**Dataset:**")
                                st.markdown(dataset_info["html_table"], unsafe_allow_html=True)
                            
                            # Dataset metadata
                            if dataset_info.get("metadata"):
                                metadata = dataset_info["metadata"]
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Rows", metadata.get("rows", 0))
                                with col2:
                                    st.metric("Columns", metadata.get("columns", 0))
                                with col3:
                                    if metadata.get("has_missing_values"):
                                        st.metric("Data Issues", "Yes", help="Contains missing/inconsistent data for practice")
                
                elif message_type == "hint":
                    st.info(f"Hint: {message['content']}")
                
                elif message_type == "adaptive_welcome":
                    st.success(message["content"])
                
                else:
                    st.markdown(message["content"])
    
    # Adaptive response input
    if st.session_state.interview_active and not st.session_state.interview_completed:
        st.markdown("### Your Excel Methodology Response")
        st.markdown("*Describe your step-by-step approach, Excel functions you'd use, and your reasoning. Reference the dataset if provided.*")
        
        # Show dataset reminder if current question has data
        if (st.session_state.current_question and 
            st.session_state.current_question.get("requires_dataset") and
            st.session_state.current_question.get("dataset_info", {}).get("generated_successfully")):
            st.info("Dataset Available: Use the 'View Current Dataset' button in the sidebar to reference the data while formulating your response.")
        
        user_input = st.chat_input("Explain your Excel approach here...")
        
        if user_input:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user", 
                "content": user_input,
                "type": "adaptive_methodology_response"
            })
            
            # Process adaptive response
            with st.spinner("Processing your response and generating adaptive follow-up..."):
                process_adaptive_response(user_input)
            
            st.rerun()
    
    elif st.session_state.interview_completed:
        st.success("Adaptive Excel assessment completed! Check your personalized results below.")
    
    elif not st.session_state.interview_started:
        st.info("Please configure your adaptive assessment settings and start the evaluation.")

def process_adaptive_response(user_input: str):
    """Process candidate's response with adaptive features"""
    try:
        if st.session_state.orchestrator:
            result = st.session_state.orchestrator.process_response(user_input)
            
            if result["success"]:
                # Add adaptive acknowledgment
                if result.get("acknowledgment"):
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": result["acknowledgment"],
                        "type": "adaptive_acknowledgment"
                    })
                
                # Check assessment completion
                if result.get("interview_complete"):
                    st.session_state.interview_completed = True
                    st.session_state.interview_active = False
                    
                    # Add adaptive conclusion
                    if result.get("conclusion_message"):
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": result["conclusion_message"],
                            "type": "adaptive_conclusion"
                        })
                
                else:
                    # Add next adaptive question
                    if result.get("next_question"):
                        st.session_state.current_question = result["next_question"]
                        question_text = result["next_question"].get("question", "")
                        
                        question_entry = {
                            "role": "assistant", 
                            "content": question_text,
                            "type": "adaptive_question",
                            "question_data": result["next_question"]
                        }
                        
                        # Include adaptive dataset info
                        if result.get("next_question_has_dataset") and result.get("dataset_info"):
                            question_entry["has_dataset"] = True
                            question_entry["dataset_info"] = result["dataset_info"]
                        
                        st.session_state.chat_history.append(question_entry)
            
            else:
                st.error(f"Error processing response: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        logger.error(f"Error processing adaptive Excel response: {str(e)}")
        st.error(f"Error processing response: {str(e)}")

def display_adaptive_results():
    """Display comprehensive adaptive Excel assessment results"""
    if st.session_state.interview_completed and st.session_state.orchestrator:
        st.markdown("---")
        st.header("Adaptive Excel Skills Assessment Results")
        
        try:
            results = st.session_state.orchestrator.get_final_results()
            
            if results["success"]:
                final_decision = results["final_decision"]
                performance_metrics = results["performance_metrics"]
                adaptive_features = results.get("adaptive_features", {})
                
                # Adaptive results display
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    score = final_decision.get('overall_score', 0)
                    st.metric("Excel Proficiency Score", f"{score}/100", 
                             help="Adaptive assessment score based on personalized trajectory")
                
                with col2:
                    decision = final_decision.get('decision', 'N/A')
                    st.metric("Assessment Result", decision)
                
                with col3:
                    st.metric("Questions Completed", performance_metrics.get('total_questions', 0))
                
                with col4:
                    adaptations = adaptive_features.get('questions_adapted', 0)
                    st.metric("Adaptive Adjustments", adaptations, 
                             help="Number of times questions were adapted based on your responses")
                
                # Adaptive analytics tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Adaptive Summary", 
                    "Skill Assessment", 
                    "Learning Trajectory",
                    "Detailed Feedback",
                    "System Performance"
                ])
                
                with tab1:
                    st.markdown("### Adaptive Excel Assessment Summary")
                    st.write(final_decision.get('recommendation_summary', 'No summary available'))
                    
                    # Adaptive insights
                    candidate_profile = results.get("candidate_profile", {})
                    
                    st.markdown("#### Adaptive Learning Insights")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Learning Trajectory:** {adaptive_features.get('questions_adapted', 0)} adaptations made")
                        st.info(f"**Final Difficulty Level:** {adaptive_features.get('final_difficulty_level', 'Medium')}")
                        
                    with col2:
                        st.info(f"**Skills Discovered:** {adaptive_features.get('skills_discovered', 0)}")
                        trend = adaptive_features.get('performance_trend', 'stable')
                        trend_indicators = {"improving": "Upward", "declining": "Downward", "stable": "Consistent"}
                        st.info(f"**Performance Trend:** {trend_indicators.get(trend, 'Stable')} {trend.title()}")
                    
                    # Strengths and areas for improvement
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Excel Strengths:**")
                        strengths = candidate_profile.get('strengths', [])
                        if strengths:
                            for strength in strengths:
                                st.write(f"• {strength}")
                        else:
                            st.write("• Strengths still being assessed")
                    
                    with col2:
                        st.markdown("**Areas for Development:**")
                        focus_areas = candidate_profile.get('areas_needing_focus', [])
                        if focus_areas:
                            for area in focus_areas:
                                st.write(f"• {area}")
                        else:
                            st.write("• Well-rounded performance across all areas")
                
                with tab2:
                    st.markdown("### Excel Skill Area Assessment")
                    
                    skill_assessment = final_decision.get('skill_assessment', {})
                    for skill, rating in skill_assessment.items():
                        skill_name = skill.replace('_', ' ').title()
                        
                        rating_values = {
                            "Excellent": 95, "Good": 80, "Fair": 65, "Poor": 40
                        }
                        
                        value = rating_values.get(rating, 50)
                        st.progress(value / 100, text=f"{skill_name}: {rating}")
                
                with tab3:
                    st.markdown("### Adaptive Learning Trajectory")
                    
                    trajectory_decisions = adaptive_features.get('trajectory_decisions', [])
                    if trajectory_decisions:
                        st.markdown("#### How the Assessment Adapted to You:")
                        for i, decision in enumerate(trajectory_decisions, 1):
                            with st.expander(f"Adaptation {i}: {decision.get('timestamp', 'Unknown time')}"):
                                st.write(f"**Reasoning:** {decision.get('reasoning', 'Adaptive adjustment made')}")
                                st.write(f"**Trajectory:** {decision.get('trajectory', 'Continued assessment')}")
                                st.write(f"**Questions Generated:** {decision.get('questions_generated', 'N/A')}")
                    else:
                        st.info("Assessment completed without major trajectory changes.")
                    
                    # Profile evolution metrics
                    st.markdown("#### Your Excel Profile Evolution")
                    profile_metrics = performance_metrics.get("candidate_profile_evolution", {})
                    
                    if profile_metrics:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Strengths Identified", profile_metrics.get("strengths_identified", 0))
                        with col2:
                            st.metric("Areas Improved", profile_metrics.get("areas_improved", 0))
                        with col3:
                            st.metric("Final Level", profile_metrics.get("final_difficulty_level", "Medium"))
                
                with tab4:
                    if st.button("Generate Adaptive Feedback Report"):
                        with st.spinner("Creating personalized adaptive assessment report..."):
                            feedback_report = st.session_state.orchestrator.generate_feedback_report()
                            if feedback_report["success"]:
                                st.text_area(
                                    "Adaptive Excel Skills Assessment Report",
                                    feedback_report["report"],
                                    height=600,
                                    help="Comprehensive feedback including adaptive learning analysis"
                                )
                                
                                # Download report
                                st.download_button(
                                    label="Download Adaptive Assessment Report",
                                    data=feedback_report["report"],
                                    file_name=f"adaptive_excel_assessment_{st.session_state.candidate_name.replace(' ', '_')}.txt",
                                    mime="text/plain"
                                )
                
                with tab5:
                    show_adaptive_system_performance()
            
            else:
                st.error("Unable to load adaptive Excel assessment results")
                
        except Exception as e:
            logger.error(f"Error displaying adaptive Excel results: {str(e)}")
            st.error(f"Error loading adaptive results: {str(e)}")

def show_adaptive_system_performance():
    """Show adaptive system performance metrics"""
    st.markdown("### Adaptive System Performance During Assessment")
    
    performance_report = tool_logger_instance.get_performance_report()
    
    # Adaptive summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tool Calls", performance_report["summary"]["total_calls"])
    with col2:
        st.metric("Success Rate", f"{performance_report['summary']['success_rate']:.1f}%")
    with col3:
        st.metric("Tools Used", performance_report["summary"]["tools_used"])
    with col4:
        # Count adaptive question generation calls
        adaptive_calls = len([call for call in tool_logger_instance.call_history 
                             if 'adaptive' in call.get('tool_name', '').lower() or 
                                'generate' in call.get('tool_name', '').lower()])
        st.metric("Adaptive Generations", adaptive_calls, help="Dynamic questions and data generated")
    
    # Tool breakdown with adaptive context
    if performance_report["per_tool_metrics"]:
        st.markdown("#### Tool Usage Breakdown")
        
        for tool_name, metrics in performance_report["per_tool_metrics"].items():
            with st.expander(f"{tool_name} - {metrics['successful_calls']}/{metrics['total_calls']} calls"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Total Calls:** {metrics['total_calls']}")
                    st.write(f"**Successful:** {metrics['successful_calls']}")
                    st.write(f"**Failed:** {metrics['failed_calls']}")
                
                with col2:
                    st.write(f"**Avg Execution Time:** {metrics['average_execution_time']:.2f}s")
                    success_rate = (metrics['successful_calls'] / metrics['total_calls'] * 100) if metrics['total_calls'] > 0 else 0
                    st.write(f"**Success Rate:** {success_rate:.1f}%")
                
                # Special handling for adaptive tools
                if any(keyword in tool_name.lower() for keyword in ['generate', 'adaptive', 'question']):
                    st.info("This tool supports adaptive question generation and personalization")

def provide_methodology_hint():
    """Provide Excel methodology hint with adaptive context"""
    if st.session_state.orchestrator and st.session_state.current_question:
        try:
            hint_result = st.session_state.orchestrator.provide_hint("methodology_focused")
            if hint_result["success"]:
                hint_msg = f"Excel Methodology Hint: {hint_result['hint_message']}"
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": hint_msg,
                    "type": "adaptive_hint"
                })
                st.rerun()
        except Exception as e:
            st.error(f"Error providing hint: {str(e)}")

def reset_assessment():
    """Reset the adaptive assessment session"""
    # Clear session state
    for key in ["orchestrator", "interview_active", "chat_history", "current_question", 
                "interview_started", "interview_completed", "excel_skill_focus", "current_dataset"]:
        if key in st.session_state:
            del st.session_state[key]
    
    initialize_session_state()
    st.rerun()

def show_tool_performance():
    """Display tool performance metrics in sidebar"""
    performance_report = tool_logger_instance.get_performance_report()
    
    with st.expander("Adaptive Tool Performance Metrics"):
        st.json(performance_report["summary"])
        
        if performance_report["per_tool_metrics"]:
            st.write("**Tools Used in Adaptive Mode:**")
            for tool_name, metrics in performance_report["per_tool_metrics"].items():
                st.write(f"- {tool_name}: {metrics['successful_calls']}/{metrics['total_calls']} successful")

def display_adaptive_tips():
    """Display adaptive Excel methodology tips"""
    if st.session_state.interview_active:
        st.markdown("### Adaptive Excel Assessment Tips")
        tips = [
            "Questions adapt based on your performance - there's no fixed sequence",
            "Reference provided datasets when explaining your approach",
            "Think step-by-step and explain your Excel methodology clearly",
            "The system learns from your responses to generate better questions",
            "Don't worry about perfect syntax - focus on logical problem-solving",
            "Each question builds on what the system learned about your skills",
            "Your performance determines the difficulty of subsequent questions"
        ]
        for tip in tips:
            st.write(f"• {tip}")
    
    elif st.session_state.interview_completed:
        st.markdown("### Your Adaptive Assessment Journey")
        if st.session_state.orchestrator:
            progress = st.session_state.orchestrator.get_progress()
            candidate_profile = progress.get('candidate_profile', {})
            
            next_steps = [
                f"Focus on {candidate_profile.get('preferred_difficulty', 'appropriate')} level Excel challenges",
                "Practice areas identified as needing development",
                "Build on strengths discovered during the assessment",
                "Work with realistic business data scenarios",
                "Consider Excel certification at your demonstrated level"
            ]
            for step in next_steps:
                st.write(f"• {step}")

def display_footer():
    """Display adaptive application footer"""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>Adaptive Microsoft Excel Skills Assessment System</strong></p>
            <p>Powered by AI • Dynamic Question Generation • Personalized Learning Paths</p>
            <p>Your responses are processed securely and used only for assessment purposes</p>
            <p><em>Assessment adapts to your performance in real-time</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """Main adaptive application function"""
    # Initialize session state
    initialize_session_state()
    
    # Display adaptive header
    display_header()
    
    # Main layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Main adaptive assessment interface
        display_chat_interface()
        display_adaptive_results()
    
    with col2:
        # Adaptive tips in main area
        display_adaptive_tips()
    
    # Adaptive sidebar
    display_sidebar()
    
    # Footer
    display_footer()

if __name__ == "__main__":
    main()