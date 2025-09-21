"""
Reviewer Agent - Responsible for evaluating candidate responses
"""

from .base_agent import BaseAgent
from utils.prompts import REVIEWER_SYSTEM_PROMPT

class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent evaluates candidate answers against Excel proficiency standards
    """
    
    def __init__(self, llm_client, tools=None):
        super().__init__("Reviewer", llm_client, tools)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Reviewer agent"""
        return REVIEWER_SYSTEM_PROMPT
    
    def evaluate_response(self, question: dict, candidate_answer: str, context: dict = None) -> dict:
        """
        Evaluate a candidate's response to an Excel interview question
        
        Args:
            question (dict): The interview question details
            candidate_answer (str): The candidate's response
            context (dict, optional): Additional context for evaluation
            
        Returns:
            dict: Evaluation results with grade and justification
        """
        evaluation_context = {
            "question": question,
            "candidate_answer": candidate_answer,
            "additional_context": context or {},
            "request_type": "evaluate_response"
        }
        
        user_input = f"""Evaluate the following candidate response:

QUESTION:
- Question: {question.get('question', 'N/A')}
- Skill Target: {question.get('skill_target', 'N/A')}
- Difficulty: {question.get('difficulty', 'N/A')}
- Expected Approach: {question.get('expected_approach', 'N/A')}

CANDIDATE ANSWER:
{candidate_answer}

Please evaluate this response and return a JSON object with the following structure:
{{
    "grade": "Satisfactory/Partly Acceptable/Unsatisfactory/Requires More Assessment",
    "score": 0-100,
    "justification": "Detailed explanation of the grade",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "alternative_solutions": ["Better approach 1", "Better approach 2", ...],
    "follow_up_needed": true/false,
    "follow_up_suggestion": "Suggested follow-up question if needed"
}}

Consider:
1. Correctness of the solution
2. Efficiency of the approach
3. Understanding of Excel concepts
4. Clarity of explanation
5. Practical applicability"""

        response = self.generate_response(user_input, evaluation_context)
        
        if response["success"]:
            json_result = self.parse_json_response(response["response"])
            if json_result["success"]:
                evaluation = json_result["data"]
                # Add metadata
                evaluation["question_id"] = question.get("question_id")
                evaluation["skill_target"] = question.get("skill_target")
                evaluation["timestamp"] = evaluation_context.get("timestamp")
                
                return {
                    "success": True,
                    "evaluation": evaluation,
                    "raw_response": response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to parse evaluation JSON",
                    "raw_response": response["response"]
                }
        else:
            return response
    
    def verify_excel_concept(self, concept: str, candidate_explanation: str) -> dict:
        """
        Verify candidate's understanding of a specific Excel concept
        
        Args:
            concept (str): The Excel concept to verify
            candidate_explanation (str): Candidate's explanation of the concept
            
        Returns:
            dict: Verification results
        """
        # Use web search tool if available to verify concept
        search_result = self.execute_tool("web_search", query=f"Excel {concept} syntax examples")
        
        context = {
            "concept": concept,
            "candidate_explanation": candidate_explanation,
            "search_result": search_result,
            "request_type": "verify_concept"
        }
        
        user_input = f"""Verify the candidate's understanding of the Excel concept: {concept}

Candidate's Explanation:
{candidate_explanation}

Please return a JSON object:
{{
    "concept_understood": true/false,
    "accuracy_score": 0-100,
    "explanation_quality": "Poor/Fair/Good/Excellent",
    "corrections_needed": ["correction1", "correction2", ...],
    "concept_verification": "Detailed verification notes"
}}"""

        response = self.generate_response(user_input, context)
        
        if response["success"]:
            return self.parse_json_response(response["response"])
        else:
            return response
    
    def batch_evaluate(self, question_answer_pairs: list) -> dict:
        """
        Evaluate multiple question-answer pairs in batch
        
        Args:
            question_answer_pairs (list): List of tuples (question, answer)
            
        Returns:
            dict: Batch evaluation results
        """
        evaluations = []
        
        for i, (question, answer) in enumerate(question_answer_pairs):
            evaluation = self.evaluate_response(question, answer)
            evaluation["pair_index"] = i
            evaluations.append(evaluation)
        
        # Calculate overall statistics
        successful_evaluations = [e for e in evaluations if e.get("success", False)]
        
        if successful_evaluations:
            grades = [e["evaluation"]["grade"] for e in successful_evaluations]
            scores = [e["evaluation"]["score"] for e in successful_evaluations if "score" in e["evaluation"]]
            
            grade_distribution = {}
            for grade in grades:
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
            
            return {
                "success": True,
                "evaluations": evaluations,
                "summary": {
                    "total_evaluated": len(successful_evaluations),
                    "average_score": sum(scores) / len(scores) if scores else 0,
                    "grade_distribution": grade_distribution
                }
            }
        else:
            return {
                "success": False,
                "error": "No successful evaluations",
                "evaluations": evaluations
            }