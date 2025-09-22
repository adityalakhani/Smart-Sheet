"""
Excel Assessment Simulation Script with Agentic Architecture
Simulates a conversation using the actual InterviewOrchestrator and agent system
"""

import os
import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Import the actual project components
from orchestrator import InterviewOrchestrator
from config import Config
from llm_clients import LLMClients
from agents.base_agent import BaseAgent
from utils.prompts import INTERVIEWER_SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntervieweeAgent(BaseAgent):
    """
    Interviewee Agent that simulates a candidate responding to Excel assessment questions
    """
    
    def __init__(self, llm_client, candidate_profile: Dict[str, Any]):
        super().__init__("Interviewee", llm_client)
        self.candidate_profile = candidate_profile
        
    def get_system_prompt(self) -> str:
        """Get the system prompt for the simulated interviewee"""
        return f"""You are {self.candidate_profile['name']}, a {self.candidate_profile['role_context']} with {self.candidate_profile['initial_proficiency']} Excel proficiency participating in a skills assessment interview.

Your background:
- Experience level: {self.candidate_profile['initial_proficiency']}
- Role context: {self.candidate_profile['role_context']}
- Areas of expertise: {', '.join(self.candidate_profile.get('areas_of_interest', []))}
- Professional with practical business application experience
- Analytical mindset with real-world Excel usage

Response characteristics:
1. Provide detailed, methodical explanations of your Excel approach
2. Break down problems step-by-step showing your thinking process
3. Mention specific Excel functions, features, and formulas you would use
4. Consider data quality issues, edge cases, and error handling
5. Reference realistic business contexts and practical applications
6. Ask clarifying questions when scenarios need more detail
7. Show appropriate confidence level for your stated proficiency
8. Demonstrate awareness of Excel best practices and limitations
9. When datasets are mentioned, reference them specifically in your approach
10. Explain not just WHAT you would do, but WHY you would choose that approach

Proficiency-specific behavior:
- Advanced: Show sophisticated understanding, mention multiple approaches, consider performance implications
- Intermediate: Demonstrate solid fundamentals with some advanced concepts
- Beginner: Focus on basic approaches but show eagerness to learn

Respond naturally as a professional being interviewed, explaining your Excel methodology clearly and thoroughly. Reference any datasets provided to show how you would use the specific data in your solution."""

class ExcelAssessmentSimulator:
    """
    Simulates the complete Excel assessment using the actual agentic architecture
    """
    
    def __init__(self):
        # Validate configuration
        Config.validate_config()
        
        # Initialize LLM clients (using actual system)
        self.llm_clients = LLMClients()
        
        # Assessment configuration
        self.candidate_details = {
            "name": "Aditya Lakhani",
            "role_context": "Data Analyst", 
            "initial_proficiency": "Advanced",
            "areas_of_interest": [
                "Basic Formulas & Functions",
                "Data Manipulation & Cleaning", 
                "VLOOKUP & Lookup Functions",
                "Pivot Tables & Analysis",
                "Data Visualization", 
                "Advanced Functions",
                "Error Handling & Validation",
                "Conditional Logic"
            ],
            "max_questions": 6,
            "include_datasets": True
        }
        
        # Initialize the actual orchestrator
        self.orchestrator = InterviewOrchestrator()
        
        # Initialize interviewee agent
        self.interviewee_agent = IntervieweeAgent(
            self.llm_clients.get_lite_client(),
            self.candidate_details
        )
        
        # Transcript management
        self.transcript = []
        self.assessment_data = {}
        
        # Create comprehensive transcript file
        self.transcript_file = f"excel_assessment_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.initialize_transcript_file()
        
        logger.info("Excel Assessment Simulator initialized with agentic architecture")
    
    def initialize_transcript_file(self):
        """Initialize the comprehensive transcript file"""
        header = f"""
=================================================================
EXCEL SKILLS ASSESSMENT - COMPREHENSIVE SIMULATION TRANSCRIPT
=================================================================

Assessment Date: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
Candidate: {self.candidate_details['name']}
Role Context: {self.candidate_details['role_context']}
Initial Proficiency: {self.candidate_details['initial_proficiency']}
Maximum Questions: {self.candidate_details['max_questions']}
Dataset Generation: {'Enabled' if self.candidate_details['include_datasets'] else 'Disabled'}

Areas of Interest: {', '.join(self.candidate_details['areas_of_interest'])}

System Architecture:
- InterviewOrchestrator: Active
- QueCraftAgent: Question generation and data integration
- ReviewerAgent: Response evaluation
- RecruiterAgent: Final assessment
- InterviewerAgent: Conversational management
- IntervieweeAgent: Simulated candidate responses

=================================================================
SIMULATION TRANSCRIPT
=================================================================

"""
        with open(self.transcript_file, 'w', encoding='utf-8') as f:
            f.write(header)
        
        logger.info(f"Comprehensive transcript file initialized: {self.transcript_file}")
    
    def log_to_transcript(self, entry_type: str, speaker: str, content: str, metadata: Dict = None):
        """Log comprehensive information to transcript"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Create entry
        entry = {
            "timestamp": timestamp,
            "type": entry_type,
            "speaker": speaker,
            "content": content,
            "metadata": metadata or {}
        }
        
        # Add to memory
        self.transcript.append(entry)
        
        # Format for file output
        formatted_entry = f"[{timestamp}] {entry_type.upper()}"
        if speaker:
            formatted_entry += f" - {speaker.upper()}"
        formatted_entry += f":\n{content}\n"
        
        # Add metadata if present
        if metadata:
            formatted_entry += f"METADATA: {json.dumps(metadata, indent=2)}\n"
        
        formatted_entry += "\n" + "-"*80 + "\n\n"
        
        # Write to file
        with open(self.transcript_file, 'a', encoding='utf-8') as f:
            f.write(formatted_entry)
        
        # Console output with color coding
        if entry_type == "CONVERSATION":
            print(f"\n{speaker.upper()}: {content}")
        elif entry_type == "SYSTEM":
            print(f"\n[SYSTEM] {content}")
        elif entry_type in ["EVALUATION", "DATASET", "PROFILE_UPDATE"]:
            print(f"\n[{entry_type}] {content}")
    
    def log_dataset_info(self, question_data: Dict, dataset_info: Dict):
        """Log dataset generation information including the actual dataset content"""
        if dataset_info.get("generated_successfully"):
            metadata_summary = dataset_info.get("metadata", {})
            context_analysis = dataset_info.get("context_analysis", {})
            
            # Build comprehensive dataset log
            content = f"""Dataset generated for question: {question_data.get('skill_target', 'Unknown skill')}

DATASET SUMMARY:
Rows: {metadata_summary.get('rows', 'N/A')}
Columns: {metadata_summary.get('columns', 'N/A')}
Column names: {', '.join(metadata_summary.get('column_names', []))}
Has missing values: {metadata_summary.get('has_missing_values', False)}
Context: {context_analysis.get('question_type', 'Business scenario')}
Data challenges: {', '.join(context_analysis.get('specific_challenges', []))}

ACTUAL DATASET (HTML TABLE):
{dataset_info.get('html_table', 'No HTML table available')}

DATASET (CSV FORMAT):
{dataset_info.get('csv_data', 'No CSV data available')}

CONTEXT ANALYSIS:
Question type: {context_analysis.get('question_type', 'N/A')}
Key skills tested: {', '.join(context_analysis.get('key_skills_tested', []))}
Data context: {context_analysis.get('data_context', 'N/A')}
Specific challenges: {', '.join(context_analysis.get('specific_challenges', []))}"""
        else:
            content = f"Dataset generation failed: {dataset_info.get('error', 'Unknown error')}"
        
        self.log_to_transcript("DATASET", "System", content, {
            "question_id": question_data.get("question_id"),
            "skill_target": question_data.get("skill_target"),
            "dataset_success": dataset_info.get("generated_successfully", False),
            "rows": metadata_summary.get('rows', 0),
            "columns": metadata_summary.get('columns', 0)
        })
    
    def log_evaluation_details(self, evaluation: Dict, question_data: Dict):
        """Log detailed evaluation information"""
        eval_data = evaluation.get("evaluation", {})
        
        content = f"""Response Evaluation for {question_data.get('skill_target', 'Unknown skill')}
Grade: {eval_data.get('grade', 'N/A')}
Score: {eval_data.get('score', 'N/A')}/100
Justification: {eval_data.get('justification', 'No justification provided')}

Strengths identified:
{chr(10).join('• ' + strength for strength in eval_data.get('strengths', []))}

Areas for improvement:
{chr(10).join('• ' + weakness for weakness in eval_data.get('weaknesses', []))}

Alternative approaches suggested:
{chr(10).join('• ' + alt for alt in eval_data.get('alternative_solutions', []))}"""
        
        self.log_to_transcript("EVALUATION", "ReviewerAgent", content, {
            "question_id": question_data.get("question_id"),
            "grade": eval_data.get("grade"),
            "score": eval_data.get("score"),
            "follow_up_needed": eval_data.get("follow_up_needed", False)
        })
    
    def log_profile_evolution(self, progress_data: Dict):
        """Log candidate profile evolution"""
        candidate_profile = progress_data.get("candidate_profile", {})
        
        content = f"""Candidate Profile Update
Strengths discovered: {', '.join(candidate_profile.get('strengths', []))}
Areas needing focus: {', '.join(candidate_profile.get('areas_needing_focus', []))}
Preferred difficulty: {candidate_profile.get('preferred_difficulty', 'Unknown')}
Performance trend: {progress_data.get('performance_trend', 'Unknown')}
Adaptive decisions made: {progress_data.get('trajectory_decisions', 0)}"""
        
        self.log_to_transcript("PROFILE_UPDATE", "Orchestrator", content, progress_data)
    
    def generate_candidate_response(self, current_question: Dict, has_dataset: bool = False) -> str:
        """Generate candidate response using IntervieweeAgent"""
        
        # Prepare context for the candidate
        question_text = current_question.get("question", "")
        skill_target = current_question.get("skill_target", "")
        scenario_context = current_question.get("scenario_context", "")
        
        # Build comprehensive context
        context_parts = [
            f"Current question focuses on: {skill_target}",
            f"Business scenario: {scenario_context}",
            f"Question: {question_text}"
        ]
        
        if has_dataset:
            context_parts.append("Note: A contextual dataset has been provided for this question. Reference it specifically in your Excel approach.")
        
        # Include recent conversation for context
        recent_conversation = []
        for entry in self.transcript[-3:]:  # Last 3 entries
            if entry["type"] == "CONVERSATION":
                recent_conversation.append(f"{entry['speaker']}: {entry['content']}")
        
        if recent_conversation:
            context_parts.append(f"Recent conversation context:\n{chr(10).join(recent_conversation)}")
        
        full_context = "\n\n".join(context_parts)
        
        # Generate response using IntervieweeAgent
        response = self.interviewee_agent.generate_response(
            user_input=f"Please respond to this Excel assessment question: {question_text}",
            context={"full_context": full_context, "has_dataset": has_dataset}
        )
        
        if response["success"]:
            return response["response"]
        else:
            logger.error(f"Error generating candidate response: {response.get('error')}")
            return "I apologize, but I'm having difficulty formulating my response right now. Could you please repeat the question?"
    
    def run_assessment(self):
        """Run the complete assessment simulation using the orchestrator"""
        logger.info("Starting comprehensive Excel assessment simulation...")
        
        try:
            # Step 1: Initialize the interview
            print("\n" + "="*80)
            print("STARTING COMPREHENSIVE EXCEL SKILLS ASSESSMENT SIMULATION")
            print("USING FULL AGENTIC ARCHITECTURE")
            print("="*80)
            
            self.log_to_transcript("SYSTEM", "Simulator", 
                                 "Starting adaptive Excel interview with orchestrator and agents", 
                                 {"candidate_details": self.candidate_details})
            
            # Start interview using orchestrator
            start_result = self.orchestrator.start_interview(
                candidate_name=self.candidate_details["name"],
                role_type=self.candidate_details["role_context"],
                difficulty_level=self.candidate_details["initial_proficiency"],
                excel_focus_areas=self.candidate_details["areas_of_interest"],
                max_questions=self.candidate_details["max_questions"],
                include_datasets=self.candidate_details["include_datasets"]
            )
            
            if not start_result["success"]:
                raise Exception(f"Failed to start interview: {start_result.get('error')}")
            
            # Log welcome message
            welcome_message = start_result.get("welcome_message", "Welcome to the assessment!")
            self.log_to_transcript("CONVERSATION", "InterviewerAgent", welcome_message)
            
            # Log first question
            first_question = start_result.get("first_question", {})
            question_presentation = start_result.get("question_presentation", first_question.get("question", ""))
            
            self.log_to_transcript("CONVERSATION", "InterviewerAgent", question_presentation, {
                "question_number": 1,
                "skill_target": first_question.get("skill_target"),
                "difficulty": first_question.get("difficulty"),
                "adaptive_reasoning": first_question.get("adaptive_reasoning")
            })
            
            # Log dataset if generated
            if first_question.get("dataset_info", {}).get("generated_successfully"):
                self.log_dataset_info(first_question, first_question["dataset_info"])
            
            time.sleep(60)  # Realistic delay
            
            # Step 2: Assessment loop
            question_count = 1
            
            while True:
                # Get current question
                progress = self.orchestrator.get_progress()
                current_question = self.orchestrator.current_questions[self.orchestrator.current_question_index] if self.orchestrator.current_questions else None
                
                if not current_question:
                    self.log_to_transcript("SYSTEM", "Orchestrator", "No current question available")
                    break
                
                # Check if dataset is available
                has_dataset = current_question.get("dataset_info", {}).get("generated_successfully", False)
                
                # Generate candidate response
                candidate_response = self.generate_candidate_response(current_question, has_dataset)
                self.log_to_transcript("CONVERSATION", "Interviewee", candidate_response, {
                    "question_number": question_count,
                    "skill_target": current_question.get("skill_target"),
                    "response_to_dataset": has_dataset
                })
                
                time.sleep(60)
                
                # Process response through orchestrator
                process_result = self.orchestrator.process_response(candidate_response)
                
                if not process_result["success"]:
                    self.log_to_transcript("SYSTEM", "Orchestrator", 
                                         f"Error processing response: {process_result.get('error')}")
                    break
                
                # Log evaluation details
                if process_result.get("evaluation"):
                    self.log_evaluation_details({"evaluation": process_result["evaluation"]}, current_question)
                
                # Log acknowledgment
                if process_result.get("acknowledgment"):
                    self.log_to_transcript("CONVERSATION", "InterviewerAgent", process_result["acknowledgment"])
                
                # Check if interview is complete
                if process_result.get("interview_complete"):
                    # Log conclusion
                    if process_result.get("conclusion_message"):
                        self.log_to_transcript("CONVERSATION", "InterviewerAgent", process_result["conclusion_message"])
                    
                    self.log_to_transcript("SYSTEM", "Orchestrator", "Assessment completed by orchestrator decision")
                    break
                
                # Log next question if available
                if process_result.get("next_question"):
                    next_question = process_result["next_question"]
                    question_presentation = process_result.get("question_presentation", next_question.get("question", ""))
                    question_count += 1
                    
                    self.log_to_transcript("CONVERSATION", "InterviewerAgent", question_presentation, {
                        "question_number": question_count,
                        "skill_target": next_question.get("skill_target"),
                        "difficulty": next_question.get("difficulty"),
                        "adaptive_reasoning": next_question.get("adaptive_reasoning")
                    })
                    
                    # Log dataset if generated for next question
                    if process_result.get("next_question_has_dataset") and process_result.get("dataset_info"):
                        self.log_dataset_info(next_question, process_result["dataset_info"])
                
                # Log profile evolution
                updated_progress = self.orchestrator.get_progress()
                self.log_profile_evolution(updated_progress)
                
                time.sleep(60)
                
                # Safety check
                if question_count > self.candidate_details["max_questions"] + 2:
                    self.log_to_transcript("SYSTEM", "Safety", "Maximum question limit exceeded, ending assessment")
                    break
            
            # Step 3: Get final results
            final_results = self.orchestrator.get_final_results()
            
            if final_results["success"]:
                self.log_comprehensive_results(final_results)
            else:
                self.log_to_transcript("SYSTEM", "Error", f"Failed to get final results: {final_results.get('error')}")
            
            # Summary
            self.log_to_transcript("SYSTEM", "Simulator", 
                                 f"Assessment simulation completed. Questions completed: {question_count}. Full transcript available in {self.transcript_file}")
            
            print("\n" + "="*80)
            print("COMPREHENSIVE ASSESSMENT SIMULATION COMPLETED")
            print(f"Questions Completed: {question_count}")
            print(f"Transcript saved to: {self.transcript_file}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Error during assessment: {e}")
            self.log_to_transcript("SYSTEM", "Error", f"Assessment failed: {str(e)}")
            raise
    
    def log_comprehensive_results(self, final_results: Dict):
        """Log comprehensive final assessment results"""
        final_decision = final_results.get("final_decision", {})
        performance_metrics = final_results.get("performance_metrics", {})
        adaptive_features = final_results.get("adaptive_features", {})
        candidate_profile = final_results.get("candidate_profile", {})
        
        # Final decision
        decision_content = f"""FINAL ASSESSMENT DECISION
Decision: {final_decision.get('decision', 'N/A')}
Overall Score: {final_decision.get('overall_score', 'N/A')}/100
Confidence Level: {final_decision.get('confidence_level', 'N/A')}

Recommendation Summary:
{final_decision.get('recommendation_summary', 'No summary provided')}

Skill Assessment:
{chr(10).join(f'• {skill}: {rating}' for skill, rating in final_decision.get('skill_assessment', {}).items())}

Key Strengths:
{chr(10).join('• ' + strength for strength in final_decision.get('strengths', []))}

Areas for Improvement:
{chr(10).join('• ' + weakness for weakness in final_decision.get('weaknesses', []))}

Improvement Recommendations:
{chr(10).join('• ' + rec for rec in final_decision.get('improvement_areas', []))}"""
        
        self.log_to_transcript("FINAL_DECISION", "RecruiterAgent", decision_content, final_decision)
        
        # Performance metrics
        metrics_content = f"""PERFORMANCE METRICS SUMMARY
Total Questions: {performance_metrics.get('total_questions', 0)}
Average Score: {performance_metrics.get('average_score', 0)}/100
Performance Trend: {performance_metrics.get('performance_trend', 'Unknown')}
Skills Assessed: {', '.join(performance_metrics.get('skills_assessed', []))}"""
        
        self.log_to_transcript("METRICS", "System", metrics_content, performance_metrics)
        
        # Adaptive features summary
        adaptive_content = f"""ADAPTIVE FEATURES SUMMARY
Questions Adapted: {adaptive_features.get('questions_adapted', 0)}
Skills Discovered: {adaptive_features.get('skills_discovered', 0)}
Final Difficulty Level: {adaptive_features.get('final_difficulty_level', 'Unknown')}
Performance Trend: {adaptive_features.get('performance_trend', 'Unknown')}
Dynamic Question Generation: {adaptive_features.get('dynamic_question_generation', False)}
Trajectory Decisions: {len(adaptive_features.get('trajectory_decisions', []))}"""
        
        self.log_to_transcript("ADAPTIVE_SUMMARY", "System", adaptive_content, adaptive_features)
        
        # Candidate profile evolution
        profile_content = f"""FINAL CANDIDATE PROFILE
Discovered Strengths: {', '.join(candidate_profile.get('strengths', []))}
Areas Needing Focus: {', '.join(candidate_profile.get('areas_needing_focus', []))}
Final Preferred Difficulty: {candidate_profile.get('preferred_difficulty', 'Unknown')}
Skill Trajectory Length: {len(candidate_profile.get('skill_trajectory', []))}"""
        
        self.log_to_transcript("FINAL_PROFILE", "System", profile_content, candidate_profile)
        
        # System performance
        llm_stats = self.llm_clients.get_client_stats()
        system_content = f"""SYSTEM PERFORMANCE
Total LLM Requests: {llm_stats.get('total_requests', 0)}
Total Errors: {llm_stats.get('total_errors', 0)}
Pro Client Requests: {llm_stats.get('pro_client', {}).get('request_count', 0)}
Lite Client Requests: {llm_stats.get('lite_client', {}).get('request_count', 0)}"""
        
        self.log_to_transcript("SYSTEM_PERFORMANCE", "System", system_content, llm_stats)

def main():
    """Main function to run the comprehensive simulation"""
    # Verify environment
    if not Config.GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY environment variable not found!")
        print("Please set your Gemini API key in a .env file or environment variable.")
        return
    
    print("Initializing Comprehensive Excel Assessment Simulation...")
    print("Using full agentic architecture with InterviewOrchestrator")
    
    try:
        # Create and run simulator
        simulator = ExcelAssessmentSimulator()
        simulator.run_assessment()
        
        print(f"\nComprehensive simulation complete!")
        print(f"Check the transcript file: {simulator.transcript_file}")
        print("The transcript includes:")
        print("- Complete conversation flow")
        print("- Dataset generation logs")
        print("- Response evaluations")
        print("- Candidate profile evolution")
        print("- Final assessment results")
        print("- System performance metrics")
        
    except Exception as e:
        logger.error(f"Failed to run comprehensive simulation: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()