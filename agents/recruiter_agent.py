"""
Recruiter Agent - Responsible for final hiring decisions and comprehensive assessment
"""

from .base_agent import BaseAgent
from utils.prompts import RECRUITER_SYSTEM_PROMPT
import json

class RecruiterAgent(BaseAgent):
    """
    Recruiter Agent makes final hiring decisions based on interview performance
    """
    
    def __init__(self, llm_client, tools=None):
        super().__init__("Recruiter", llm_client, tools)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Recruiter agent"""
        return RECRUITER_SYSTEM_PROMPT
    
    def make_final_decision(self, interview_summary: dict, evaluation_history: list, role_requirements: dict = None) -> dict:
        """
        Make final hiring decision based on complete interview performance
        
        Args:
            interview_summary (dict): Summary of the interview session
            evaluation_history (list): List of all question evaluations
            role_requirements (dict, optional): Specific requirements for the role
            
        Returns:
            dict: Final decision and comprehensive assessment
        """
        context = {
            "interview_summary": interview_summary,
            "evaluation_history": evaluation_history,
            "role_requirements": role_requirements or {},
            "request_type": "final_decision"
        }
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(evaluation_history)
        
        user_input = f"""Based on the complete interview performance, make a final hiring decision:

INTERVIEW SUMMARY:
{json.dumps(interview_summary, indent=2)}

PERFORMANCE METRICS:
{json.dumps(performance_metrics, indent=2)}

EVALUATION HISTORY:
{json.dumps(evaluation_history, indent=2)}

ROLE REQUIREMENTS:
{json.dumps(role_requirements, indent=2)}

Please provide a comprehensive final assessment in JSON format:
{{
    "decision": "Pass/Fail/Continue Interview",
    "confidence_level": "High/Medium/Low",
    "overall_score": 0-100,
    "recommendation_summary": "2-3 paragraph summary for hiring managers",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "skill_assessment": {{
        "basic_formulas": "Excellent/Good/Fair/Poor",
        "data_analysis": "Excellent/Good/Fair/Poor",
        "pivot_tables": "Excellent/Good/Fair/Poor",
        "data_visualization": "Excellent/Good/Fair/Poor",
        "advanced_functions": "Excellent/Good/Fair/Poor"
    }},
    "improvement_areas": ["area1", "area2", ...],
    "follow_up_recommendations": ["recommendation1", "recommendation2", ...],
    "next_steps": "Recommended next steps in hiring process"
}}

Consider the candidate's:
1. Technical proficiency across Excel skills
2. Problem-solving approach and methodology
3. Communication clarity and explanation quality
4. Consistency in performance across different question types
5. Ability to handle increasing complexity"""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            json_result = self.parse_json_response(response["response"])
            if json_result["success"]:
                decision_data = json_result["data"]
                decision_data["performance_metrics"] = performance_metrics
                
                return {
                    "success": True,
                    "final_decision": decision_data,
                    "raw_response": response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to parse decision JSON",
                    "raw_response": response["response"]
                }
        else:
            return response
    
    def should_continue_interview(self, current_evaluations: list, question_count: int) -> dict:
        """
        Determine if interview should continue based on current performance
        
        Args:
            current_evaluations (list): Evaluations so far
            question_count (int): Number of questions asked
            
        Returns:
            dict: Decision on whether to continue
        """
        context = {
            "current_evaluations": current_evaluations,
            "question_count": question_count,
            "request_type": "continue_decision"
        }
        
        # Quick performance analysis
        performance_summary = self._analyze_current_performance(current_evaluations)
        
        user_input = f"""Based on the current interview progress, decide whether to continue:

QUESTIONS ASKED: {question_count}
CURRENT PERFORMANCE SUMMARY:
{json.dumps(performance_summary, indent=2)}

RECENT EVALUATIONS:
{json.dumps(current_evaluations[-3:], indent=2)}  # Last 3 evaluations

Please provide a decision in JSON format:
{{
    "continue_interview": true/false,
    "reason": "Explanation for the decision",
    "suggested_focus_area": "Area to focus on if continuing",
    "early_termination_reason": "Reason if stopping early",
    "confidence_in_decision": "High/Medium/Low"
}}

Continue if:
- Performance is improving or consistently good
- Still need to assess key skills
- Haven't reached minimum question threshold (5 questions)

Stop early if:
- Consistently poor performance (3+ unsatisfactory grades)
- Candidate clearly unprepared
- Major knowledge gaps evident"""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return self.parse_json_response(response["response"])
        else:
            return response
    
    def generate_feedback_report(self, final_decision: dict, interview_data: dict) -> dict:
        """
        Generate comprehensive feedback report for candidate
        
        Args:
            final_decision (dict): The final hiring decision
            interview_data (dict): Complete interview session data
            
        Returns:
            dict: Formatted feedback report
        """
        context = {
            "final_decision": final_decision,
            "interview_data": interview_data,
            "request_type": "feedback_report"
        }
        
        user_input = f"""Generate a constructive feedback report for the candidate:

FINAL DECISION:
{json.dumps(final_decision, indent=2)}

INTERVIEW DATA:
{json.dumps(interview_data, indent=2)}

Create a professional feedback report in JSON format:
{{
    "report_summary": "Overall performance summary",
    "detailed_feedback": {{
        "technical_skills": "Assessment of Excel technical skills",
        "problem_solving": "Problem-solving approach evaluation",
        "communication": "Communication and explanation quality",
        "areas_of_strength": ["strength1", "strength2", ...],
        "areas_for_improvement": ["improvement1", "improvement2", ...],
        "specific_recommendations": ["recommendation1", "recommendation2", ...]
    }},
    "skill_breakdown": {{
        "formulas_and_functions": {{"score": 0-100, "feedback": "specific feedback"}},
        "data_analysis": {{"score": 0-100, "feedback": "specific feedback"}},
        "pivot_tables": {{"score": 0-100, "feedback": "specific feedback"}},
        "data_visualization": {{"score": 0-100, "feedback": "specific feedback"}}
    }},
    "next_steps": "Recommended next steps for skill development",
    "interview_experience_rating": "Rate the interview experience for improvements"
}}"""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return self.parse_json_response(response["response"])
        else:
            return response
    
    def _calculate_performance_metrics(self, evaluation_history: list) -> dict:
        """
        Calculate performance metrics from evaluation history
        
        Args:
            evaluation_history (list): List of evaluations
            
        Returns:
            dict: Performance metrics
        """
        if not evaluation_history:
            return {"error": "No evaluations to analyze"}
        
        successful_evaluations = [e for e in evaluation_history if e.get("success", False)]
        
        if not successful_evaluations:
            return {"error": "No successful evaluations"}
        
        grades = []
        scores = []
        skills_tested = []
        
        for eval_item in successful_evaluations:
            evaluation = eval_item.get("evaluation", {})
            if evaluation:
                grades.append(evaluation.get("grade", ""))
                if "score" in evaluation:
                    scores.append(evaluation["score"])
                if "skill_target" in evaluation:
                    skills_tested.append(evaluation["skill_target"])
        
        # Calculate grade distribution
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # Calculate average score
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine trend (improving/declining/stable)
        trend = "stable"
        if len(scores) > 2:
            first_half_avg = sum(scores[:len(scores)//2]) / len(scores[:len(scores)//2])
            second_half_avg = sum(scores[len(scores)//2:]) / len(scores[len(scores)//2:])
            if second_half_avg > first_half_avg + 10:
                trend = "improving"
            elif second_half_avg < first_half_avg - 10:
                trend = "declining"
        
        return {
            "total_questions": len(successful_evaluations),
            "average_score": round(avg_score, 2),
            "grade_distribution": grade_counts,
            "skills_tested": list(set(skills_tested)),
            "performance_trend": trend,
            "pass_rate": (grade_counts.get("Satisfactory", 0) + grade_counts.get("Partly Acceptable", 0)) / len(grades) * 100 if grades else 0
        }
    
    def _analyze_current_performance(self, current_evaluations: list) -> dict:
        """
        Analyze current performance for continue/stop decision
        
        Args:
            current_evaluations (list): Current evaluations
            
        Returns:
            dict: Performance analysis
        """
        if not current_evaluations:
            return {"status": "no_data"}
        
        recent_grades = []
        for eval_item in current_evaluations[-3:]:  # Last 3 evaluations
            if eval_item.get("success") and eval_item.get("evaluation"):
                recent_grades.append(eval_item["evaluation"].get("grade", ""))
        
        unsatisfactory_count = recent_grades.count("Unsatisfactory")
        satisfactory_count = recent_grades.count("Satisfactory")
        
        return {
            "recent_grades": recent_grades,
            "unsatisfactory_streak": unsatisfactory_count,
            "satisfactory_count": satisfactory_count,
            "total_evaluated": len(current_evaluations),
            "recommendation": "stop" if unsatisfactory_count >= 2 else "continue"
        }