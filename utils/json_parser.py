"""
JSON Parser utility for handling LLM responses and ensuring proper JSON formatting
"""

import json
import re
import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

class JSONParser:
    """
    Utility class for parsing and validating JSON responses from LLM agents
    """
    
    @staticmethod
    def parse_json_response(response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response text, handling common formatting issues
        
        Args:
            response_text (str): Raw response text from LLM
            
        Returns:
            dict: Parsed JSON data or error information
        """
        if not response_text or not isinstance(response_text, str):
            return {
                "success": False,
                "error": "Empty or invalid response text",
                "data": None
            }
        
        # Try direct JSON parsing first
        try:
            data = json.loads(response_text)
            return {
                "success": True,
                "data": data,
                "error": None
            }
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return {
                    "success": True,
                    "data": data,
                    "error": None
                }
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object in text
        json_pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
        json_matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        for match in json_matches:
            try:
                data = json.loads(match)
                return {
                    "success": True,
                    "data": data,
                    "error": None
                }
            except json.JSONDecodeError:
                continue
        
        # If all parsing attempts fail
        logger.error(f"Failed to parse JSON from response: {response_text[:200]}...")
        return {
            "success": False,
            "error": "Could not parse valid JSON from response",
            "data": None,
            "raw_response": response_text
        }
    
    @staticmethod
    def validate_interview_plan(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate interview plan JSON structure
        
        Args:
            data (dict): Parsed JSON data
            
        Returns:
            dict: Validation results
        """
        required_fields = ["interview_plan", "total_questions", "estimated_duration", "skills_covered"]
        required_question_fields = ["question_id", "question", "skill_target", "difficulty"]
        
        validation_errors = []
        
        # Check required top-level fields
        for field in required_fields:
            if field not in data:
                validation_errors.append(f"Missing required field: {field}")
        
        # Validate interview_plan structure
        if "interview_plan" in data:
            if not isinstance(data["interview_plan"], list):
                validation_errors.append("interview_plan must be a list")
            else:
                for i, question in enumerate(data["interview_plan"]):
                    if not isinstance(question, dict):
                        validation_errors.append(f"Question {i+1} must be a dictionary")
                        continue
                    
                    for field in required_question_fields:
                        if field not in question:
                            validation_errors.append(f"Question {i+1} missing field: {field}")
                    
                    # Validate difficulty levels
                    if "difficulty" in question:
                        if question["difficulty"] not in ["Easy", "Medium", "Hard"]:
                            validation_errors.append(f"Question {i+1} has invalid difficulty level")
        
        return {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "data": data
        }
    
    @staticmethod
    def validate_evaluation(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate evaluation JSON structure
        
        Args:
            data (dict): Parsed JSON data
            
        Returns:
            dict: Validation results
        """
        required_fields = ["grade", "score", "justification", "strengths", "weaknesses"]
        valid_grades = ["Satisfactory", "Partly Acceptable", "Unsatisfactory", "Requires More Assessment"]
        
        validation_errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                validation_errors.append(f"Missing required field: {field}")
        
        # Validate grade
        if "grade" in data:
            if data["grade"] not in valid_grades:
                validation_errors.append(f"Invalid grade: {data['grade']}")
        
        # Validate score
        if "score" in data:
            try:
                score = float(data["score"])
                if not 0 <= score <= 100:
                    validation_errors.append("Score must be between 0 and 100")
            except (TypeError, ValueError):
                validation_errors.append("Score must be a number")
        
        # Validate lists
        for list_field in ["strengths", "weaknesses"]:
            if list_field in data:
                if not isinstance(data[list_field], list):
                    validation_errors.append(f"{list_field} must be a list")
        
        return {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "data": data
        }
    
    @staticmethod
    def validate_final_decision(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate final decision JSON structure
        
        Args:
            data (dict): Parsed JSON data
            
        Returns:
            dict: Validation results
        """
        required_fields = ["decision", "confidence_level", "overall_score", "recommendation_summary"]
        valid_decisions = ["Pass", "Fail", "Continue Interview"]
        valid_confidence = ["High", "Medium", "Low"]
        
        validation_errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                validation_errors.append(f"Missing required field: {field}")
        
        # Validate decision
        if "decision" in data:
            if data["decision"] not in valid_decisions:
                validation_errors.append(f"Invalid decision: {data['decision']}")
        
        # Validate confidence level
        if "confidence_level" in data:
            if data["confidence_level"] not in valid_confidence:
                validation_errors.append(f"Invalid confidence level: {data['confidence_level']}")
        
        # Validate overall score
        if "overall_score" in data:
            try:
                score = float(data["overall_score"])
                if not 0 <= score <= 100:
                    validation_errors.append("Overall score must be between 0 and 100")
            except (TypeError, ValueError):
                validation_errors.append("Overall score must be a number")
        
        return {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "data": data
        }
    
    @staticmethod
    def clean_response_text(text: str) -> str:
        """
        Clean response text for better JSON parsing
        
        Args:
            text (str): Raw response text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove common prefixes and suffixes
        text = re.sub(r'^Here\'s.*?:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*```$', '', text)
        
        # Remove extra whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def format_json_for_display(data: Union[Dict, str], indent: int = 2) -> str:
        """
        Format JSON data for display
        
        Args:
            data: JSON data or string
            indent: Indentation level
            
        Returns:
            str: Formatted JSON string
        """
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            return str(data)