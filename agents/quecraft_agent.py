"""
Enhanced QueCraft Agent with integrated contextual data generation
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from utils.prompts import QUERAFT_SYSTEM_PROMPT
from utils.tool_logger import tool_logger_instance, log_tool_call

logger = logging.getLogger(__name__)

class QueCraftAgent(BaseAgent):
    """
    Enhanced QueCraft Agent for creating case-based Excel interview questions
    with contextually relevant data generation
    """
    
    def __init__(self, llm_client, enhanced_data_generator, web_search_tool=None):
        super().__init__("QueCraft", llm_client)
        self.enhanced_data_generator = enhanced_data_generator
        self.web_search_tool = web_search_tool
        
        # Add tools with logging
        self.add_tool("generate_contextual_data", self._logged_generate_contextual_data)
        self.add_tool("search_excel_practices", self._logged_web_search)
        
        logger.info("Enhanced QueCraft Agent initialized with contextual data generation")
    
    def get_system_prompt(self) -> str:
        """Get the enhanced system prompt for case-based Excel assessment"""
        return QUERAFT_SYSTEM_PROMPT
    
    @log_tool_call("generate_contextual_data", "QueCraft")
    def _logged_generate_contextual_data(self, **kwargs) -> Dict[str, Any]:
        """Generate contextual data with comprehensive logging"""
        try:
            result = self.enhanced_data_generator.generate_contextual_dataset(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in contextual data generation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @log_tool_call("search_excel_practices", "QueCraft")  
    def _logged_web_search(self, **kwargs) -> Dict[str, Any]:
        """Perform web search with logging"""
        if self.web_search_tool:
            return self.web_search_tool.search_excel_topic(**kwargs)
        else:
            return {"success": False, "error": "Web search tool not available"}
    
    def generate_case_based_interview_plan(self, 
                                         role_context: str = "Business Analyst",
                                         difficulty_level: str = "Mixed",
                                         focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive case-based interview plan with contextual data
        """
        
        logger.info(f"Generating case-based interview plan - Role: {role_context}, Difficulty: {difficulty_level}")
        
        context = {
            "role_context": role_context,
            "difficulty_level": difficulty_level, 
            "focus_areas": focus_areas or [],
            "request_type": "case_based_interview_plan"
        }
        
        user_input = f"""Generate a comprehensive case-based Excel interview plan for a {role_context} role with {difficulty_level} difficulty level.

CRITICAL REQUIREMENTS:
1. Create 8-10 CASE-BASED questions that test Excel THINKING, not software execution
2. Each question should present a realistic business scenario
3. Questions must be INTERROGATIVE ("How would you...") not directive ("Please do...")
4. Focus on methodology, approach, and Excel tool selection reasoning
5. For questions requiring datasets, specify EXACT data requirements

RESPONSE FORMAT:
{{
    "interview_plan": [
        {{
            "question_id": 1,
            "question": "Given [specific scenario], how would you [specific challenge]? Explain your approach step-by-step.",
            "skill_target": "Primary Excel skill being assessed", 
            "difficulty": "Easy/Medium/Hard",
            "scenario_context": "Detailed business situation",
            "requires_dataset": true/false,
            "dataset_requirements": {{
                "data_context": "marketing campaigns/sales data/employee records/etc",
                "required_columns": ["Column1", "Column2", "Column3"],
                "data_challenges": ["zero values", "missing data", "inconsistent formats"],
                "sample_size": 30-100
            }},
            "expected_approach": "Key Excel methodology elements",
            "evaluation_criteria": ["methodology clarity", "function appropriateness"],
            "excel_functions_tested": ["primary functions candidate should mention"]
        }}
    ],
    "total_questions": 8-10,
    "estimated_duration": "45-60 minutes", 
    "skills_covered": ["skill1", "skill2", ...],
    "assessment_focus": "Excel methodology and analytical thinking"
}}

SAMPLE QUESTION FOR ROAS CALCULATION:
"A marketing manager needs to calculate Return on Ad Spend (ROAS) for different campaigns. You have campaign data with 'Spend' and 'Revenue' columns, but some campaigns have zero spend values. How would you create a ROAS calculation (Revenue/Spend) that handles division by zero errors gracefully? Walk me through your Excel approach step-by-step, including the functions you'd use and your error-handling strategy."

Generate similar case-based questions that require realistic business data to make the Excel challenge meaningful."""

        try:
            start_time = time.time()
            response = self.generate_response(user_input, context)
            execution_time = time.time() - start_time
            
            if response["success"]:
                json_result = self.parse_json_response(response["response"])
                if json_result["success"]:
                    # Enhance the interview plan with contextual datasets
                    enhanced_plan = self._enhance_interview_plan_with_data(json_result["data"])
                    return {
                        "success": True,
                        "interview_plan": enhanced_plan,
                        "raw_response": response["response"]
                    }
                else:
                    logger.error(f"Failed to parse interview plan JSON: {json_result.get('error')}")
                    return {
                        "success": False,
                        "error": "Failed to parse interview plan JSON",
                        "raw_response": response["response"]
                    }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error generating case-based interview plan: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _enhance_interview_plan_with_data(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance interview plan by generating contextual datasets for questions that need them
        """
        enhanced_plan = plan_data.copy()
        
        for question in enhanced_plan.get("interview_plan", []):
            if question.get("requires_dataset", False):
                try:
                    # Generate contextual dataset for this specific question
                    dataset_result = self._logged_generate_contextual_data(
                        question_context=question.get("question", ""),
                        size=question.get("dataset_requirements", {}).get("sample_size", 50),
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
                        logger.info(f"Generated contextual dataset for question {question.get('question_id')}")
                    else:
                        # Fallback to specific question type data
                        fallback_result = self.enhanced_data_generator.generate_for_specific_question_types(
                            question.get("skill_target", "general"),
                            size=30
                        )
                        
                        question["dataset_info"] = {
                            "html_table": fallback_result["dataset_html"],
                            "csv_data": fallback_result["dataset_csv"],
                            "metadata": fallback_result["dataset_info"],
                            "fallback_used": True,
                            "generated_successfully": True
                        }
                        logger.warning(f"Used fallback data for question {question.get('question_id')}")
                
                except Exception as e:
                    logger.error(f"Error generating dataset for question {question.get('question_id')}: {str(e)}")
                    question["dataset_info"] = {
                        "error": str(e),
                        "generated_successfully": False
                    }
        
        # Add assessment metadata
        enhanced_plan["assessment_metadata"] = {
            "focus_type": "case_based_methodology",
            "evaluation_approach": "verbal_explanation",
            "excel_access_required": False,
            "created_timestamp": time.time(),
            "agent_version": "Enhanced QueCraft v3.0",
            "data_generation_enabled": True
        }
        
        logger.info(f"Enhanced interview plan with {len(enhanced_plan['interview_plan'])} questions and contextual datasets")
        
        return enhanced_plan
    
    def create_single_question_with_data(self, 
                                       question_context: str,
                                       skill_target: str,
                                       difficulty: str = "Medium") -> Dict[str, Any]:
        """
        Create a single question with perfectly matched dataset
        
        Args:
            question_context (str): The specific question or scenario
            skill_target (str): Excel skill being tested
            difficulty (str): Question difficulty level
            
        Returns:
            dict: Complete question with contextual dataset
        """
        try:
            # Generate contextual dataset
            dataset_result = self._logged_generate_contextual_data(
                question_context=question_context,
                size=40,
                specific_requirements={
                    "skill_target": skill_target,
                    "difficulty": difficulty
                }
            )
            
            question_data = {
                "question_id": 1,
                "question": question_context,
                "skill_target": skill_target,
                "difficulty": difficulty,
                "requires_dataset": True,
                "dataset_info": dataset_result if dataset_result.get("success") else {"error": "Failed to generate data"}
            }
            
            return {
                "success": True,
                "question": question_data,
                "dataset_generated": dataset_result.get("success", False)
            }
            
        except Exception as e:
            logger.error(f"Error creating single question with data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def refine_question_data_match(self, 
                                  question: Dict[str, Any],
                                  data_feedback: str) -> Dict[str, Any]:
        """
        Refine the data generation to better match the question requirements
        
        Args:
            question (dict): Original question data
            data_feedback (str): Feedback on how to improve data matching
            
        Returns:
            dict: Refined question with better matched dataset
        """
        try:
            # Regenerate data with specific feedback
            improved_dataset = self._logged_generate_contextual_data(
                question_context=question.get("question", ""),
                size=50,
                specific_requirements={
                    "improvement_feedback": data_feedback,
                    "original_question": question,
                    "skill_target": question.get("skill_target", "")
                }
            )
            
            # Update question with improved dataset
            refined_question = question.copy()
            refined_question["dataset_info"] = improved_dataset
            refined_question["data_refinement_applied"] = data_feedback
            
            return {
                "success": True,
                "refined_question": refined_question,
                "improvement_applied": True
            }
            
        except Exception as e:
            logger.error(f"Error refining question data match: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_question_data_alignment(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the generated data properly supports the question
        
        Args:
            question (dict): Question with dataset
            
        Returns:
            dict: Validation results
        """
        try:
            dataset_info = question.get("dataset_info", {})
            if not dataset_info.get("generated_successfully"):
                return {
                    "aligned": False,
                    "issues": ["Dataset generation failed"],
                    "recommendation": "Retry data generation with specific requirements"
                }
            
            question_text = question.get("question", "").lower()
            dataset_columns = dataset_info.get("metadata", {}).get("column_names", [])
            
            # Check if question mentions specific columns/concepts that should be in data
            alignment_issues = []
            
            # Check for common Excel scenarios
            if "roas" in question_text and not any("spend" in col.lower() and "revenue" in col.lower() for col in dataset_columns):
                alignment_issues.append("ROAS question requires 'Spend' and 'Revenue' columns")
            
            if "vlookup" in question_text or "lookup" in question_text:
                if len(dataset_columns) < 4:
                    alignment_issues.append("Lookup questions typically need multiple tables/columns")
            
            if "pivot" in question_text:
                categorical_cols = [col for col in dataset_columns if "name" in col.lower() or "type" in col.lower()]
                if len(categorical_cols) < 2:
                    alignment_issues.append("Pivot questions need categorical columns for grouping")
            
            return {
                "aligned": len(alignment_issues) == 0,
                "issues": alignment_issues,
                "dataset_columns": dataset_columns,
                "validation_score": max(0, 100 - len(alignment_issues) * 25)
            }
            
        except Exception as e:
            logger.error(f"Error validating question-data alignment: {str(e)}")
            return {
                "aligned": False,
                "error": str(e)
            }