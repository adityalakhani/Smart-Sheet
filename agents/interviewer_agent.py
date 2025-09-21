"""
Interviewer Agent - Handles conversational interface with candidates (uses lighter model)
"""

from .base_agent import BaseAgent
from utils.prompts import INTERVIEWER_SYSTEM_PROMPT

class InterviewerAgent(BaseAgent):
    """
    Interviewer Agent manages the conversational flow with candidates
    Uses the lighter Gemini model for better performance
    """
    
    def __init__(self, llm_client_lite, tools=None):
        # Note: This agent uses the lite client for faster responses
        super().__init__("Interviewer", llm_client_lite, tools)
        self.interview_state = "not_started"
        self.current_question = None
        self.candidate_responses = []
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Interviewer agent"""
        return INTERVIEWER_SYSTEM_PROMPT
    
    def generate_response(self, user_input: str, context=None) -> dict:
        """
        Override to use the lite model (gemini-2.5-flash)
        """
        try:
            system_prompt = self.get_system_prompt()
            
            if context:
                context_str = f"\nContext: {context}"
            else:
                context_str = ""
            
            full_prompt = f"{system_prompt}{context_str}\n\nUser Input: {user_input}"
            
            # Use the lighter model for interviewer responses
            response = self.llm_client.generate_content(
                contents=full_prompt,
            )
            
            self.conversation_history.append({
                "input": user_input,
                "output": response.text,
                "context": context
            })
            
            return {
                "success": True,
                "response": response.text,
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def start_interview(self, candidate_name: str = "Candidate") -> dict:
        """
        Start the interview with a welcome message
        
        Args:
            candidate_name (str): Name of the candidate
            
        Returns:
            dict: Welcome message and instructions
        """
        self.interview_state = "started"
        
        context = {
            "candidate_name": candidate_name,
            "interview_stage": "welcome",
            "action": "start_interview"
        }
        
        user_input = f"Start interview for {candidate_name}. Provide welcome message and instructions."
        
        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "welcome_message": response["response"],
                "interview_state": self.interview_state
            }
        else:
            return response
    
    def present_question(self, question: dict, question_number: int, total_questions: int) -> dict:
        """
        Present a question to the candidate in a conversational manner
        
        Args:
            question (dict): Question details from interview plan
            question_number (int): Current question number
            total_questions (int): Total number of questions
            
        Returns:
            dict: Formatted question presentation
        """
        self.current_question = question
        
        context = {
            "question": question,
            "question_number": question_number,
            "total_questions": total_questions,
            "interview_stage": "presenting_question",
            "action": "present_question"
        }
        
        user_input = f"""Present question {question_number} of {total_questions} to the candidate:

Question Details:
- Question: {question.get('question', '')}
- Skill Target: {question.get('skill_target', '')}
- Difficulty: {question.get('difficulty', '')}

Make it conversational and encouraging. If the question requires a dataset, mention that clearly."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "question_presentation": response["response"],
                "current_question": question,
                "progress": f"{question_number}/{total_questions}"
            }
        else:
            return response
    
    def acknowledge_answer(self, candidate_answer: str, evaluation_grade: str = None) -> dict:
        """
        Acknowledge candidate's answer and provide transition
        
        Args:
            candidate_answer (str): The candidate's response
            evaluation_grade (str, optional): Grade from reviewer (for internal use)
            
        Returns:
            dict: Acknowledgment message
        """
        self.candidate_responses.append({
            "question": self.current_question,
            "answer": candidate_answer,
            "grade": evaluation_grade
        })
        
        context = {
            "candidate_answer": candidate_answer,
            "evaluation_grade": evaluation_grade,
            "interview_stage": "acknowledging_answer",
            "action": "acknowledge_answer"
        }
        
        user_input = f"""Acknowledge the candidate's answer and provide a smooth transition:

Candidate's Answer: {candidate_answer}

Be encouraging and professional. Don't reveal the evaluation grade. Prepare for the next question or conclusion."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "acknowledgment": response["response"],
                "recorded_response": True
            }
        else:
            return response
    
    def ask_clarification(self, clarification_type: str, specific_area: str) -> dict:
        """
        Ask for clarification on a candidate's response
        
        Args:
            clarification_type (str): Type of clarification needed
            specific_area (str): Specific area that needs clarification
            
        Returns:
            dict: Clarification question
        """
        context = {
            "clarification_type": clarification_type,
            "specific_area": specific_area,
            "current_question": self.current_question,
            "interview_stage": "seeking_clarification",
            "action": "ask_clarification"
        }
        
        user_input = f"""Ask for clarification about {specific_area}. 

Clarification type: {clarification_type}
Current question context: {self.current_question.get('question', '') if self.current_question else 'N/A'}

Be polite and specific in asking for clarification. Don't make the candidate feel bad about their initial response."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "clarification_question": response["response"],
                "awaiting_clarification": True
            }
        else:
            return response
    
    def provide_encouragement(self, performance_context: str = "general") -> dict:
        """
        Provide encouragement to the candidate during the interview
        
        Args:
            performance_context (str): Context for encouragement
            
        Returns:
            dict: Encouraging message
        """
        context = {
            "performance_context": performance_context,
            "interview_stage": "encouragement",
            "action": "provide_encouragement"
        }
        
        user_input = f"""Provide encouragement to the candidate. Context: {performance_context}

Be genuine, supportive, and maintain professional interview atmosphere."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "encouragement_message": response["response"]
            }
        else:
            return response
    
    def conclude_interview(self, interview_outcome: str, next_steps: str = "") -> dict:
        """
        Conclude the interview with appropriate closing remarks
        
        Args:
            interview_outcome (str): Overall interview outcome context
            next_steps (str): Information about next steps
            
        Returns:
            dict: Concluding message
        """
        self.interview_state = "concluded"
        
        context = {
            "interview_outcome": interview_outcome,
            "next_steps": next_steps,
            "total_responses": len(self.candidate_responses),
            "interview_stage": "conclusion",
            "action": "conclude_interview"
        }
        
        user_input = f"""Conclude the interview professionally:

Interview outcome context: {interview_outcome}
Next steps: {next_steps}
Total questions answered: {len(self.candidate_responses)}

Thank the candidate, mention next steps if provided, and maintain positive tone regardless of performance."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "conclusion_message": response["response"],
                "interview_state": self.interview_state,
                "total_responses_recorded": len(self.candidate_responses)
            }
        else:
            return response
    
    def handle_off_topic_response(self, candidate_input: str) -> dict:
        """
        Handle when candidate gives off-topic or unclear responses
        
        Args:
            candidate_input (str): The candidate's off-topic response
            
        Returns:
            dict: Redirect message
        """
        context = {
            "candidate_input": candidate_input,
            "current_question": self.current_question,
            "interview_stage": "redirecting",
            "action": "handle_off_topic"
        }
        
        user_input = f"""The candidate gave an off-topic response: {candidate_input}

Current question: {self.current_question.get('question', '') if self.current_question else 'N/A'}

Politely redirect them back to the current Excel question. Be helpful and understanding."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "redirect_message": response["response"],
                "needs_refocus": True
            }
        else:
            return response
    
    def get_interview_summary(self) -> dict:
        """
        Get summary of the interview conversation
        
        Returns:
            dict: Interview summary
        """
        return {
            "interview_state": self.interview_state,
            "total_questions_answered": len(self.candidate_responses),
            "conversation_length": len(self.conversation_history),
            "candidate_responses": self.candidate_responses,
            "current_question": self.current_question
        }
    
    def reset_interview(self):
        """Reset the interview state for a new candidate"""
        self.interview_state = "not_started"
        self.current_question = None
        self.candidate_responses = []
        self.reset_conversation()
    
    def provide_hint(self, hint_level: str = "gentle") -> dict:
        """
        Provide a hint for the current question
        
        Args:
            hint_level (str): Level of hint (gentle/moderate/direct)
            
        Returns:
            dict: Hint message
        """
        if not self.current_question:
            return {
                "success": False,
                "error": "No current question to provide hint for"
            }
        
        context = {
            "current_question": self.current_question,
            "hint_level": hint_level,
            "interview_stage": "providing_hint",
            "action": "provide_hint"
        }
        
        user_input = f"""Provide a {hint_level} hint for the current question:

Question: {self.current_question.get('question', '')}
Skill Target: {self.current_question.get('skill_target', '')}
Expected Approach: {self.current_question.get('expected_approach', '')}

Give a helpful hint without giving away the complete answer. Match the hint level requested."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "hint_message": response["response"],
                "hint_provided": True,
                "hint_level": hint_level
            }
        else:
            return response
    
    def check_understanding(self, concept: str) -> dict:
        """
        Check candidate's understanding of a specific Excel concept
        
        Args:
            concept (str): Excel concept to check understanding of
            
        Returns:
            dict: Understanding check question
        """
        context = {
            "concept": concept,
            "interview_stage": "checking_understanding",
            "action": "check_understanding"
        }
        
        user_input = f"""Ask a quick understanding check question about: {concept}

Make it conversational and not intimidating. This is to gauge their conceptual understanding."""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return {
                "success": True,
                "understanding_check": response["response"],
                "concept_being_checked": concept
            }
        else:
            return response