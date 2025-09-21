"""
Configuration for AI-Powered Excel Mock Interviewer
Focused specifically on Microsoft Excel skills assessment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for Excel Mock Interviewer"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration - Focused on Excel assessment
    GEMINI_PRO_MODEL = "gemini-2.0-flash-exp"  # For complex reasoning (QueCraft, Reviewer, Recruiter)
    GEMINI_LITE_MODEL = "gemini-2.0-flash-exp"  # For conversational tasks (Interviewer)
    
    # Rate Limiting
    PRO_MODEL_RATE_LIMIT = 15  # Requests per minute
    LITE_MODEL_RATE_LIMIT = 60  # Requests per minute
    
    # Interview Configuration - Excel Focused
    MIN_QUESTIONS_THRESHOLD = 5
    MAX_QUESTIONS_PER_INTERVIEW = 10
    
    # Excel Skill Categories - Core Focus Areas
    EXCEL_SKILL_CATEGORIES = [
        "Basic Formulas and Functions",
        "Data Manipulation and Cleaning", 
        "Lookup Functions (VLOOKUP, INDEX/MATCH)",
        "Pivot Tables and Data Analysis",
        "Data Visualization and Charts",
        "Conditional Logic and IF Statements",
        "Text Functions and String Manipulation",
        "Advanced Functions and Array Formulas",
        "Data Validation and Error Handling",
        "Macro Basics and Automation"
    ]
    
    # Difficulty Levels
    DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard", "Mixed"]
    
    # Assessment Focus - Excel Only
    ASSESSMENT_FOCUS = "microsoft_excel_proficiency"
    
    # Data Generation Configuration
    DATA_GENERATION_METHOD = "faker_synthetic"  # Use Faker library
    DEFAULT_DATASET_SIZE = 50  # Default number of records
    MAX_DATASET_SIZE = 200     # Maximum records for performance
    
    # Supported Data Types for Excel Questions
    EXCEL_DATA_TYPES = [
        "sales_transactions",
        "employee_records", 
        "financial_expenses",
        "inventory_stock",
        "customer_database",
        "survey_responses",
        "project_timeline",
        "budget_allocation",
        "performance_metrics",
        "contact_information"
    ]
    
    # Question Types - Case-Based Approach
    QUESTION_FORMATS = [
        "case_study",      # Scenario-based questions
        "problem_solving", # How would you approach...
        "best_practice",   # What's the best way to...
        "troubleshooting", # How would you fix...
        "optimization"     # How would you improve...
    ]
    
    # Logging Configuration
    ENABLE_TOOL_LOGGING = True
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Report Configuration
    GENERATE_DETAILED_REPORTS = True
    INCLUDE_SKILL_BREAKDOWN = True
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        return True