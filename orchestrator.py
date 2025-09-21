# Updated orchestrator.py - Adaptive Interview System

"""
Updated Orchestrator with adaptive question generation based on candidate responses
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from llm_clients import LLMClients
from agents import ReviewerAgent, RecruiterAgent, InterviewerAgent
from agents.quecraft_agent import QueCraftAgent
from utils.mock_data_generator import MockDataGenerator
from utils.web_search import WebSearchTool
from utils.report_generator import ReportGenerator
from utils.tool_logger import tool_logger_instance
from config import Config

logger = logging.getLogger(__name__)

class InterviewOrchestrator:
    """
    Adaptive orchestrator that generates questions dynamically based on candidate responses
    """
    
    def __init__(self):
        """Initialize the adaptive orchestrator"""
        try:
            logger.info("Initializing Adaptive Interview Orchestrator for Excel assessment")
            
            # Initialize LLM clients
            self.llm_clients = LLMClients()
            
            # Initialize enhanced tools
            self._enhanced_data_generator = MockDataGenerator(
                llm_client=self.llm_clients.get_pro_client()
            )
            self.web_search_tool = WebSearchTool()
            self.report_generator = ReportGenerator()
            
            # Initialize enhanced agents
            self._initialize_enhanced_agents()
            
            # Adaptive interview state
            self.interview_state = "not_started"
            self.current_questions = []  # Current batch of questions (max 2)
            self.current_question_index = 0
            self.chat_history = []
            self.assessment_results = []
            self.candidate_data = {}
            self.interview_metadata = {}
            self.is_awaiting_follow_up = False
            
            # Adaptive tracking
            self.excel_skills_tested = set()
            self.excel_performance_by_skill = {}
            self.candidate_profile = {
                "strengths": [],
                "weaknesses": [],
                "skill_trajectory": [],
                "preferred_difficulty": "Medium",
                "areas_needing_focus": []
            }
            self.trajectory_decisions = []
            
            # Session tracking
            self.session_id = f"adaptive_excel_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.start_time = None
            self.end_time = None
            
            logger.info("Adaptive Excel Interview Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize adaptive orchestrator: {str(e)}")
            raise
    
    def _initialize_enhanced_agents(self):
        """Initialize enhanced agents with proper data integration"""
        try:
            # Enhanced QueCraft Agent with adaptive capabilities
            self.quecraft_agent = QueCraftAgent(
                self.llm_clients.get_pro_client(),
                self._enhanced_data_generator,
                self.web_search_tool
            )
            
            # Reviewer Agent
            self.reviewer_agent = ReviewerAgent(
                self.llm_clients.get_pro_client()
            )
            self.reviewer_agent.add_tool("search_excel_practices", self.web_search_tool.search_excel_best_practices)
            
            # Recruiter Agent  
            self.recruiter_agent = RecruiterAgent(
                self.llm_clients.get_pro_client()
            )
            
            # Interviewer Agent
            self.interviewer_agent = InterviewerAgent(
                self.llm_clients.get_lite_client()
            )
            
            logger.info("All adaptive agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize adaptive agents: {str(e)}")
            raise
    
    def start_interview(self, 
                       candidate_name: str, 
                       role_type: str = "Business Analyst",
                       difficulty_level: str = "Mixed Assessment", 
                       excel_focus_areas: List[str] = None,
                       max_questions: int = 10,
                       include_datasets: bool = True) -> Dict[str, Any]:
        """
        Start adaptive Excel interview with initial question generation
        """
        try:
            logger.info(f"Starting adaptive Excel interview for {candidate_name}")
            
            # Set up candidate data
            self.candidate_data = {
                "name": candidate_name,
                "role_type": role_type,
                "difficulty_level": difficulty_level,
                "excel_focus_areas": excel_focus_areas or [],
                "max_questions": max_questions,
                "include_datasets": include_datasets
            }
            
            # Initialize candidate profile
            self.candidate_profile.update({
                "role_context": role_type,
                "initial_difficulty": difficulty_level,
                "focus_areas": excel_focus_areas or [],
                "preferred_difficulty": "Medium"  # Start with medium
            })
            
            # Enhanced interview metadata
            self.interview_metadata = {
                "session_id": self.session_id,
                "candidate": candidate_name,
                "role_context": role_type,
                "assessment_type": "adaptive_excel_methodology",
                "start_time": datetime.now().isoformat(),
                "max_questions": max_questions,
                "data_generation_enabled": include_datasets,
                "adaptive_features": True
            }
            
            self.start_time = datetime.now()
            
            # Generate initial 2 questions based on profile
            logger.info("Generating initial adaptive questions...")
            initial_questions = self._generate_next_questions(
                context="initial_assessment",
                count=2
            )
            
            if not initial_questions["success"]:
                return {
                    "success": False,
                    "error": f"Failed to generate initial questions: {initial_questions.get('error')}"
                }
            
            self.current_questions = initial_questions["questions"]
            
            # Start interview
            welcome_result = self.interviewer_agent.start_interview(candidate_name)
            if not welcome_result["success"]:
                return {"success": False, "error": f"Failed to start interview: {welcome_result.get('error')}"}
            
            # Present first question
            first_question_result = self.interviewer_agent.present_question(
                self.current_questions[0], 1, "?"  # Don't show total as it's adaptive
            )
            
            if not first_question_result["success"]:
                return {"success": False, "error": f"Failed to present first question: {first_question_result.get('error')}"}
            
            # Update state
            self.interview_state = "in_progress"
            self.current_question_index = 0
            
            # Track skill being tested
            first_skill = self.current_questions[0].get("skill_target", "Unknown")
            self.excel_skills_tested.add(first_skill)
            
            # Chat history
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "adaptive_excel_interview_start",
                "content": welcome_result["welcome_message"],
                "metadata": {"assessment_type": "adaptive_excel_methodology"}
            })
            
            first_question_chat = {
                "timestamp": datetime.now().isoformat(),
                "type": "adaptive_question",
                "question_id": self.current_questions[0]["question_id"],
                "content": first_question_result["question_presentation"],
                "question_data": self.current_questions[0]
            }
            
            # Include dataset info if available
            if self.current_questions[0].get("dataset_info", {}).get("generated_successfully"):
                first_question_chat["dataset_available"] = True
                first_question_chat["dataset_preview"] = self.current_questions[0]["dataset_info"].get("metadata", {})
            
            self.chat_history.append(first_question_chat)
            
            logger.info("Adaptive Excel interview started successfully")
            
            return {
                "success": True,
                "welcome_message": f"Welcome to your adaptive Excel skills assessment, {candidate_name}! This evaluation will adjust to your responses and focus on areas that need the most attention.",
                "first_question": self.current_questions[0],
                "question_presentation": first_question_result["question_presentation"],
                "interview_metadata": self.interview_metadata,
                "adaptive_mode": True,
                "questions_prepared": len(self.current_questions)
            }
            
        except Exception as e:
            logger.error(f"Error starting adaptive Excel interview: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_next_questions(self, 
                                context: str = "continuation",
                                count: int = 2,
                                response_analysis: Dict = None) -> Dict[str, Any]:
        """
        Generate next batch of questions based on current context and candidate profile
        """
        try:
            # Prepare context for question generation
            generation_context = {
                "candidate_profile": self.candidate_profile,
                "assessment_results": self.assessment_results[-3:] if self.assessment_results else [],  # Last 3 results
                "skills_tested": list(self.excel_skills_tested),
                "response_analysis": response_analysis or {},
                "generation_context": context,
                "role_context": self.candidate_data["role_type"],
                "adaptive_mode": True
            }
            
            # Create adaptive prompt for question generation
            adaptive_prompt = self._create_adaptive_generation_prompt(generation_context, count)
            
            # Generate questions using QueCraft agent
            response = self.quecraft_agent.generate_response(
                user_input=adaptive_prompt,
                context=generation_context
            )
            
            if not response["success"]:
                return {"success": False, "error": "Failed to generate adaptive questions"}
            
            # Parse response
            json_result = self.quecraft_agent.parse_json_response(response["response"])
            if not json_result["success"]:
                return {"success": False, "error": "Failed to parse question generation response"}
            
            questions = json_result["data"].get("questions", [])
            
            # Enhance questions with datasets if needed
            enhanced_questions = []
            for question in questions:
                enhanced_question = self._enhance_question_with_data(question)
                enhanced_questions.append(enhanced_question)
            
            return {
                "success": True,
                "questions": enhanced_questions,
                "generation_reasoning": json_result["data"].get("reasoning", ""),
                "trajectory_decision": json_result["data"].get("trajectory_decision", "")
            }
            
        except Exception as e:
            logger.error(f"Error generating next questions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_adaptive_generation_prompt(self, context: Dict, count: int) -> str:
        """Create adaptive prompt for question generation"""
        
        prompt = f"""Generate {count} adaptive Excel interview questions based on the candidate's performance profile and responses.

CANDIDATE PROFILE:
{json.dumps(context["candidate_profile"], indent=2)}

RECENT ASSESSMENT RESULTS:
{json.dumps(context["assessment_results"], indent=2)}

SKILLS ALREADY TESTED:
{context["skills_tested"]}

GENERATION CONTEXT: {context["generation_context"]}

ADAPTIVE REQUIREMENTS:
1. Analyze the candidate's performance trajectory
2. Identify skill gaps and strengths from previous responses
3. Generate questions that target areas needing improvement
4. Adjust difficulty based on demonstrated capability
5. Ensure logical progression and skill building

RESPONSE FORMAT:
{{
    "reasoning": "Explain why these specific questions were chosen based on candidate profile",
    "trajectory_decision": "Describe the adaptive trajectory being taken",
    "questions": [
        {{
            "question_id": "generated_id",
            "question": "How would you... [adaptive scenario]",
            "skill_target": "Primary Excel skill",
            "difficulty": "Easy/Medium/Hard based on candidate ability",
            "adaptive_reasoning": "Why this question fits the candidate's current level",
            "scenario_context": "Business scenario description",
            "requires_dataset": true/false,
            "dataset_requirements": {{
                "data_context": "type of data needed",
                "required_columns": ["col1", "col2"],
                "data_challenges": ["challenge1", "challenge2"],
                "sample_size": 30-100
            }},
            "expected_approach": "Key Excel methodology elements",
            "evaluation_criteria": ["criterion1", "criterion2"],
            "builds_on_previous": "How this connects to previous questions"
        }}
    ],
    "next_focus_areas": ["areas to explore in future questions"]
}}

ADAPTIVE STRATEGY:
- If candidate is performing well: Increase complexity, introduce advanced concepts
- If candidate is struggling: Reinforce fundamentals, provide supportive scenarios
- If candidate shows specific weaknesses: Target those areas with focused questions
- If candidate shows expertise in an area: Move to different skill domains

Generate questions that will help determine the candidate's true Excel capability level."""

        return prompt
    
    def _enhance_question_with_data(self, question: Dict) -> Dict:
        """Enhance a single question with contextual dataset if needed"""
        if not question.get("requires_dataset"):
            return question
        
        try:
            dataset_result = self._enhanced_data_generator.generate_contextual_dataset(
                question_context=question.get("question", ""),
                size=question.get("dataset_requirements", {}).get("sample_size", 40),
                specific_requirements=question.get("dataset_requirements", {})
            )
            
            if dataset_result.get("success"):
                question["dataset_info"] = {
                    "html_table": dataset_result["dataset_html"],
                    "csv_data": dataset_result["dataset_csv"],
                    "metadata": dataset_result["dataset_info"],
                    "context_analysis": dataset_result.get("context_analysis", {}),
                    "generated_successfully": True
                }
            else:
                question["dataset_info"] = {
                    "error": dataset_result.get("error", "Unknown error"),
                    "generated_successfully": False
                }
                
        except Exception as e:
            logger.error(f"Error enhancing question with data: {str(e)}")
            question["dataset_info"] = {
                "error": str(e),
                "generated_successfully": False
            }
        
        return question
    
    def process_response(self, candidate_answer: str) -> Dict[str, Any]:
        """
        Process candidate response and adaptively generate next question
        """
        try:
            if self.interview_state != "in_progress":
                return {"success": False, "error": "Interview not in progress"}
            
            if self.current_question_index >= len(self.current_questions):
                return {"success": False, "error": "No current question available"}
            
            current_question = self.current_questions[self.current_question_index]
            
            logger.info(f"Processing adaptive response for question {self.current_question_index + 1}")
            
            # Evaluate current response
            evaluation_context = {
                "timestamp": datetime.now().isoformat(),
                "assessment_type": "adaptive_excel_methodology",
                "response_type": "verbal_explanation",
                "dataset_available": current_question.get("dataset_info", {}).get("generated_successfully", False),
                "adaptive_context": True
            }
            
            # Log response
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "adaptive_response",
                "question_id": current_question["question_id"],
                "content": candidate_answer,
                "skill_target": current_question.get("skill_target"),
                "had_dataset": current_question.get("requires_dataset", False)
            })
            
            # Evaluate response
            evaluation_result = self.reviewer_agent.evaluate_response(
                current_question,
                candidate_answer,
                evaluation_context
            )
            
            if not evaluation_result["success"]:
                return {"success": False, "error": f"Failed to evaluate response: {evaluation_result.get('error')}"}
            
            evaluation_data = evaluation_result["evaluation"]
            
            # Update candidate profile based on response
            self._update_candidate_profile(current_question, evaluation_data, candidate_answer)
            
            # Create assessment record
            assessment_record = {
                "question_index": len(self.assessment_results),
                "question": current_question,
                "candidate_answer": candidate_answer,
                "evaluation": evaluation_data,
                "timestamp": datetime.now().isoformat(),
                "excel_skill": current_question.get("skill_target"),
                "adaptive_generation": True
            }
            
            self.assessment_results.append(assessment_record)
            
            # Handle follow-ups
            if evaluation_data.get("follow_up_needed"):
                follow_up_suggestion = evaluation_data.get("follow_up_suggestion", "Can you elaborate?")
                follow_up_result = self.interviewer_agent.ask_clarification(
                    clarification_type="adaptive_probe", 
                    specific_area=follow_up_suggestion
                )
                
                return {
                    "success": True,
                    "acknowledgment": evaluation_data.get("justification"),
                    "next_question": {"question": follow_up_result["clarification_question"], "is_follow_up": True},
                    "interview_complete": False,
                    "adaptive_mode": True
                }
            
            # Get acknowledgment
            acknowledgment_result = self.interviewer_agent.acknowledge_answer(
                candidate_answer,
                evaluation_data.get("grade")
            )
            acknowledgment = acknowledgment_result.get("acknowledgment", "Thank you for your response.")
            
            # Adaptive decision: should we continue?
            continue_decision = self._should_continue_adaptive_assessment()
            
            if not continue_decision["continue"]:
                return self._complete_adaptive_assessment(acknowledgment, continue_decision.get("reason"))
            
            # Move to next question or generate new ones
            self.current_question_index += 1
            
            # Check if we need to generate more questions
            if self.current_question_index >= len(self.current_questions):
                # Analyze performance and generate next batch
                response_analysis = {
                    "latest_evaluation": evaluation_data,
                    "performance_trend": self._analyze_performance_trend(),
                    "skill_gaps": self._identify_skill_gaps()
                }
                
                next_questions = self._generate_next_questions(
                    context="adaptive_continuation",
                    count=2,
                    response_analysis=response_analysis
                )
                
                if next_questions["success"]:
                    self.current_questions.extend(next_questions["questions"])
                    
                    # Log trajectory decision
                    self.trajectory_decisions.append({
                        "timestamp": datetime.now().isoformat(),
                        "reasoning": next_questions.get("generation_reasoning"),
                        "trajectory": next_questions.get("trajectory_decision"),
                        "questions_generated": len(next_questions["questions"])
                    })
                else:
                    return self._complete_adaptive_assessment(acknowledgment, "Failed to generate adaptive questions")
            
            # Present next question
            next_question = self.current_questions[self.current_question_index]
            next_question_result = self.interviewer_agent.present_question(
                next_question,
                len(self.assessment_results) + 1,
                "Adaptive"
            )
            
            if not next_question_result["success"]:
                return {"success": False, "error": f"Failed to present next question: {next_question_result.get('error')}"}
            
            # Track new skill
            next_skill = next_question.get("skill_target", "Unknown")
            self.excel_skills_tested.add(next_skill)
            
            # Chat log for next question
            next_question_chat = {
                "timestamp": datetime.now().isoformat(),
                "type": "adaptive_question",
                "question_id": next_question["question_id"],
                "content": next_question_result["question_presentation"],
                "question_data": next_question,
                "adaptive_reasoning": next_question.get("adaptive_reasoning", "")
            }
            
            if next_question.get("dataset_info", {}).get("generated_successfully"):
                next_question_chat["dataset_available"] = True
            
            self.chat_history.append(next_question_chat)
            
            response_data = {
                "success": True,
                "acknowledgment": acknowledgment,
                "next_question": next_question,
                "question_presentation": next_question_result["question_presentation"],
                "evaluation": evaluation_data,
                "interview_complete": False,
                "adaptive_mode": True,
                "candidate_profile_updated": True
            }
            
            # Include dataset info if available
            if next_question.get("dataset_info", {}).get("generated_successfully"):
                response_data["next_question_has_dataset"] = True
                response_data["dataset_info"] = {
                    "html_table": next_question["dataset_info"].get("html_table", ""),
                    "metadata": next_question["dataset_info"].get("metadata", {})
                }
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing adaptive response: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _update_candidate_profile(self, question: Dict, evaluation: Dict, answer: str):
        """Update candidate profile based on latest response"""
        skill = question.get("skill_target", "Unknown")
        score = evaluation.get("score", 0)
        grade = evaluation.get("grade", "")
        
        # Update skill performance tracking
        if skill not in self.excel_performance_by_skill:
            self.excel_performance_by_skill[skill] = []
        
        self.excel_performance_by_skill[skill].append({
            "score": score,
            "grade": grade,
            "question_difficulty": question.get("difficulty", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        # Update candidate profile
        self.candidate_profile["skill_trajectory"].append({
            "skill": skill,
            "score": score,
            "difficulty": question.get("difficulty", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        # Update strengths and weaknesses
        if score >= 80:
            if skill not in self.candidate_profile["strengths"]:
                self.candidate_profile["strengths"].append(skill)
        elif score < 60:
            if skill not in self.candidate_profile["weaknesses"]:
                self.candidate_profile["weaknesses"].append(skill)
                
            if skill not in self.candidate_profile["areas_needing_focus"]:
                self.candidate_profile["areas_needing_focus"].append(skill)
        
        # Adjust preferred difficulty
        recent_scores = [item["score"] for item in self.candidate_profile["skill_trajectory"][-3:]]
        if recent_scores:
            avg_recent = sum(recent_scores) / len(recent_scores)
            if avg_recent >= 85:
                self.candidate_profile["preferred_difficulty"] = "Hard"
            elif avg_recent >= 70:
                self.candidate_profile["preferred_difficulty"] = "Medium"
            else:
                self.candidate_profile["preferred_difficulty"] = "Easy"
    
    def _analyze_performance_trend(self) -> Dict[str, Any]:
        """Analyze candidate's performance trend"""
        if len(self.candidate_profile["skill_trajectory"]) < 2:
            return {"trend": "insufficient_data"}
        
        recent_scores = [item["score"] for item in self.candidate_profile["skill_trajectory"][-3:]]
        
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0] + 10:
                trend = "improving"
            elif recent_scores[-1] < recent_scores[0] - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "recent_average": sum(recent_scores) / len(recent_scores),
            "score_range": [min(recent_scores), max(recent_scores)]
        }
    
    def _identify_skill_gaps(self) -> List[str]:
        """Identify skills that need more attention"""
        all_excel_skills = [
            "Basic Formulas and Functions",
            "Data Manipulation and Cleaning", 
            "Lookup Functions (VLOOKUP, INDEX/MATCH)",
            "Pivot Tables and Data Analysis",
            "Data Visualization and Charts",
            "Conditional Logic and IF Statements",
            "Advanced Functions and Array Formulas"
        ]
        
        tested_skills = list(self.excel_skills_tested)
        weak_skills = self.candidate_profile["areas_needing_focus"]
        untested_skills = [skill for skill in all_excel_skills if skill not in tested_skills]
        
        # Priority: weak skills first, then untested skills
        return weak_skills + untested_skills[:2]  # Limit to avoid too many
    
    def _should_continue_adaptive_assessment(self) -> Dict[str, Any]:
        """Determine if adaptive assessment should continue"""
        
        # Minimum questions check
        if len(self.assessment_results) < 4:
            return {"continue": True, "reason": "Need minimum assessment coverage"}
        
        # Maximum questions check
        if len(self.assessment_results) >= self.candidate_data.get("max_questions", 10):
            return {"continue": False, "reason": "Reached maximum question limit"}
        
        # Performance stability check
        if len(self.assessment_results) >= 6:
            recent_scores = [r["evaluation"]["score"] for r in self.assessment_results[-4:]]
            score_variance = max(recent_scores) - min(recent_scores)
            
            if score_variance < 15:  # Scores are stable
                return {"continue": False, "reason": "Performance level established"}
        
        # Skill coverage check
        target_skills = 5  # Target number of different skills to assess
        if len(self.excel_skills_tested) >= target_skills:
            return {"continue": False, "reason": "Adequate skill coverage achieved"}
        
        return {"continue": True, "reason": "Continue adaptive assessment"}
    
    def _complete_adaptive_assessment(self, acknowledgment: str, reason: str) -> Dict[str, Any]:
        """Complete the adaptive assessment"""
        try:
            logger.info(f"Completing adaptive assessment: {reason}")
            
            self.interview_state = "completed"
            self.end_time = datetime.now()
            
            # Enhanced context for final decision
            adaptive_context = {
                "assessment_type": "adaptive_excel_methodology",
                "trajectory_decisions": self.trajectory_decisions,
                "candidate_profile": self.candidate_profile,
                "adaptive_features_used": True
            }
            
            final_decision_result = self.recruiter_agent.make_final_decision(
                self.interview_metadata,
                self.assessment_results,
                adaptive_context
            )
            
            if not final_decision_result["success"]:
                final_decision = {
                    "decision": "Requires Manual Review",
                    "overall_score": 0,
                    "recommendation_summary": "Unable to generate adaptive assessment decision."
                }
            else:
                final_decision = final_decision_result["final_decision"]
            
            # Get conclusion
            conclusion_result = self.interviewer_agent.conclude_interview(
                final_decision.get("decision", "Complete"),
                "Thank you for participating in this adaptive Excel skills assessment."
            )
            
            conclusion_message = conclusion_result.get("conclusion_message", 
                "Thank you for completing the adaptive Excel assessment!")
            
            # Update metadata
            self.interview_metadata.update({
                "end_time": datetime.now().isoformat(),
                "duration": str(self.end_time - self.start_time),
                "questions_completed": len(self.assessment_results),
                "final_decision": final_decision,
                "adaptive_trajectory_decisions": len(self.trajectory_decisions),
                "candidate_profile_final": self.candidate_profile
            })
            
            return {
                "success": True,
                "acknowledgment": acknowledgment,
                "conclusion_message": conclusion_message,
                "interview_complete": True,
                "final_decision": final_decision,
                "adaptive_summary": {
                    "trajectory_decisions": len(self.trajectory_decisions),
                    "skills_discovered": list(self.excel_skills_tested),
                    "performance_trend": self._analyze_performance_trend(),
                    "adaptive_personalization": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error completing adaptive assessment: {str(e)}")
            return {"success": False, "error": str(e), "interview_complete": True}
    
    def get_current_question_dataset(self) -> Dict[str, Any]:
        """Get dataset for current question"""
        try:
            if (self.interview_state != "in_progress" or 
                self.current_question_index >= len(self.current_questions)):
                return {"success": False, "error": "No current question available"}
            
            current_question = self.current_questions[self.current_question_index]
            dataset_info = current_question.get("dataset_info", {})
            
            if not dataset_info.get("generated_successfully"):
                return {"success": False, "error": "No dataset available for current question"}
            
            return {
                "success": True,
                "dataset_html": dataset_info.get("html_table", ""),
                "dataset_metadata": dataset_info.get("metadata", {}),
                "context_analysis": dataset_info.get("context_analysis", {}),
                "question_id": current_question.get("question_id"),
                "skill_target": current_question.get("skill_target")
            }
            
        except Exception as e:
            logger.error(f"Error getting current question dataset: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_progress(self) -> Dict[str, Any]:
        """Get adaptive assessment progress"""
        return {
            "questions_completed": len(self.assessment_results),
            "current_question_number": len(self.assessment_results) + 1,
            "interview_state": self.interview_state,
            "skills_tested": list(self.excel_skills_tested),
            "adaptive_mode": True,
            "trajectory_decisions": len(self.trajectory_decisions),
            "candidate_profile": {
                "strengths": self.candidate_profile["strengths"],
                "areas_needing_focus": self.candidate_profile["areas_needing_focus"],
                "preferred_difficulty": self.candidate_profile["preferred_difficulty"]
            },
            "performance_trend": self._analyze_performance_trend().get("trend", "unknown")
        }
    
    def get_final_results(self) -> Dict[str, Any]:
        """Get comprehensive adaptive assessment results"""
        try:
            if self.interview_state != "completed":
                return {"success": False, "error": "Adaptive assessment not completed"}
            
            performance_metrics = self._calculate_adaptive_performance_metrics()
            
            return {
                "success": True,
                "final_decision": self.interview_metadata.get("final_decision", {}),
                "performance_metrics": performance_metrics,
                "interview_metadata": self.interview_metadata,
                "assessment_results": self.assessment_results,
                "excel_skills_performance": self.excel_performance_by_skill,
                "candidate_profile": self.candidate_profile,
                "adaptive_features": {
                    "trajectory_decisions": self.trajectory_decisions,
                    "adaptive_personalization": True,
                    "dynamic_question_generation": True,
                    "questions_adapted": len(self.trajectory_decisions),
                    "skills_discovered": len(self.excel_skills_tested),
                    "final_difficulty_level": self.candidate_profile.get("preferred_difficulty", "Medium"),
                    "performance_trend": self._analyze_performance_trend().get("trend", "stable")
                }
            }
        except Exception as e:
            logger.error(f"Error getting adaptive assessment results: {str(e)}")
            return {"success": False, "error": str(e)}