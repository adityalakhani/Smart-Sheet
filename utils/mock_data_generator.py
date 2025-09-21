"""
Enhanced Mock Data Generator with LLM integration for contextually relevant data
"""

import pandas as pd
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from faker import Faker
import io
import json

logger = logging.getLogger(__name__)

class MockDataGenerator:
    """
    Enhanced data generator that uses LLM to create contextually relevant datasets
    specifically designed for Excel interview questions
    """
    
    def __init__(self, llm_client=None):
        self.fake = Faker()
        self.llm_client = llm_client
        Faker.seed(42)
        
        logger.info("Enhanced Mock Data Generator initialized with LLM integration")
    
    def generate_contextual_dataset(self, 
                                  question_context: str,
                                  size: int = 50,
                                  specific_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate dataset that matches the specific question context using LLM
        
        Args:
            question_context (str): The interview question requiring data
            size (int): Number of records
            specific_requirements (dict): Specific data requirements
            
        Returns:
            dict: Generated dataset with HTML table format
        """
        logger.info(f"Generating contextual dataset for question: {question_context[:100]}...")
        
        try:
            # Use LLM to understand context and generate appropriate data structure
            data_structure = self._analyze_question_and_design_data(question_context, specific_requirements)
            
            if not data_structure.get("success"):
                logger.warning("Failed to analyze question context, falling back to sales data")
                return self._generate_fallback_data(size)
            
            # Generate the actual data based on LLM analysis
            dataset = self._generate_data_from_structure(data_structure["structure"], size)
            
            # Convert to HTML table format
            html_table = self._convert_to_html_table(dataset)
            
            return {
                "success": True,
                "dataset_html": html_table,
                "dataset_csv": dataset.to_csv(index=False),
                "dataset_info": self._get_dataset_metadata(dataset),
                "context_analysis": data_structure.get("analysis", {}),
                "columns": dataset.columns.tolist(),
                "rows": len(dataset)
            }
            
        except Exception as e:
            logger.error(f"Error generating contextual dataset: {str(e)}")
            fallback_data = self._generate_fallback_data(size)
            return {
                "success": False,
                "error": str(e),
                "dataset_html": self._convert_to_html_table(fallback_data["dataset"]),
                "dataset_csv": fallback_data["dataset"].to_csv(index=False),
                "fallback_used": True
            }
    
    def _analyze_question_and_design_data(self, question_context: str, requirements: Dict = None) -> Dict[str, Any]:
        """
        Use LLM to analyze question and design appropriate data structure
        """
        if not self.llm_client:
            return {"success": False, "error": "No LLM client available"}
        
        prompt = f"""
Analyze this Excel interview question and design a dataset structure that would be perfect for testing the skills mentioned:

QUESTION: {question_context}

ADDITIONAL REQUIREMENTS: {json.dumps(requirements or {}, indent=2)}

Design a dataset structure that:
1. Directly supports the Excel challenge described in the question
2. Contains the exact columns mentioned or implied in the question
3. Includes realistic business data relevant to the scenario
4. Has some data quality issues that make the Excel challenge meaningful
5. Is sized appropriately for the skill being tested
6. Has only 10-20 rows

Respond in JSON format:
{{
    "analysis": {{
        "question_type": "data_analysis/formula_creation/pivot_tables/data_cleaning/etc",
        "key_skills_tested": ["skill1", "skill2", "skill3"],
        "data_context": "marketing/sales/hr/finance/etc",
        "specific_challenges": ["challenge1", "challenge2"]
    }},
    "structure": {{
        "columns": [
            {{
                "name": "Column_Name",
                "type": "string/number/date/boolean",
                "description": "what this column represents",
                "data_pattern": "how to generate realistic data",
                "include_issues": true/false,
                "issue_type": "missing_values/inconsistent_format/duplicates/etc"
            }}
        ],
        "business_context": "realistic business scenario description",
        "sample_size_recommendation": 10-20,
        "key_data_relationships": "how columns relate to each other"
    }}
}}

Make sure the dataset directly enables the candidate to practice the Excel skills mentioned in the question.
"""
        
        try:
            response = self.llm_client.generate_content(contents=prompt)
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data_structure = json.loads(json_match.group(0))
                return {
                    "success": True,
                    "structure": data_structure,
                    "analysis": data_structure.get("analysis", {}),
                    "raw_response": response.text
                }
            else:
                logger.error("Could not extract JSON from LLM response")
                return {"success": False, "error": "Invalid LLM response format"}
                
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_data_from_structure(self, structure: Dict, size: int) -> pd.DataFrame:
        """
        Generate pandas DataFrame based on LLM-designed structure
        """
        data = []
        columns_info = structure["structure"]["columns"]
        
        for i in range(size):
            row = {}
            
            for col_info in columns_info:
                col_name = col_info["name"]
                col_type = col_info["type"]
                data_pattern = col_info.get("data_pattern", "")
                include_issues = col_info.get("include_issues", False)
                issue_type = col_info.get("issue_type", "")
                
                # Generate data based on column type and pattern
                value = self._generate_column_value(col_type, data_pattern, include_issues, issue_type, i)
                row[col_name] = value
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _generate_column_value(self, col_type: str, pattern: str, include_issues: bool, issue_type: str, row_index: int):
        """
        Generate individual column values based on specifications
        """
        # Base value generation
        if col_type == "string" and col_type != None:
            if "campaign" in pattern.lower():
                base_value = f"{random.choice(['Email', 'Social', 'PPC', 'Display'])} Campaign {row_index + 1}"
            elif "name" in pattern.lower():
                base_value = self.fake.name()
            elif "company" in pattern.lower():
                base_value = self.fake.company()
            else:
                base_value = self.fake.word().title()
                
        elif col_type == "number" and col_type != None:
            if "spend" in pattern.lower():
                base_value = round(random.uniform(100, 10000), 2)
            elif "revenue" in pattern.lower():
                base_value = round(random.uniform(500, 50000), 2)
            elif "quantity" in pattern.lower():
                base_value = random.randint(1, 100)
            else:
                base_value = round(random.uniform(1, 1000), 2)
                
        elif col_type == "date" and col_type != None:
            base_value = self.fake.date_between(start_date="-1y", end_date="today").strftime("%Y-%m-%d")
            
        elif col_type == "boolean" and col_type != None:
            base_value = random.choice([True, False])
            
        else:
            base_value = str(self.fake.word())
        
        # Apply data quality issues
        if include_issues and random.random() < 0.15:  # 15% chance of issues
            if issue_type == "missing_values":
                return ""
            elif issue_type == "inconsistent_format" and col_type == "string":
                if random.random() < 0.5:
                    return str(base_value).upper()
                else:
                    return str(base_value).lower()
            elif issue_type == "zero_values" and col_type == "number":
                return 0
        
        return base_value
    
    def _convert_to_html_table(self, df: pd.DataFrame) -> str:
        """
        Convert DataFrame to HTML table with Bootstrap styling
        """
        html = df.to_html(
            index=False,
            classes='table table-striped table-bordered',
            escape=False
        )
        
        # Wrap in a container for better styling
        wrapped_html = f"""
        <div class="table-responsive">
            {html}
        </div>
        """
        
        return wrapped_html
    
    def _get_dataset_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate metadata about the dataset
        """
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_preview": df.head(3).to_dict('records'),
            "has_missing_values": df.isnull().sum().sum() > 0,
            "memory_usage": f"{df.memory_usage().sum()} bytes"
        }
    
    def _generate_fallback_data(self, size: int) -> Dict[str, Any]:
        """
        Generate fallback data when LLM analysis fails
        """
        # Simple marketing campaign data as fallback
        data = []
        for i in range(size):
            spend = round(random.uniform(100, 10000), 2)
            # Some campaigns with zero spend for division by zero practice
            if random.random() < 0.1:  # 10% zero spend
                spend = 0
            
            revenue = round(random.uniform(500, 50000), 2) if spend > 0 else 0
            
            data.append({
                "Campaign_ID": f"CAM{str(i+1001).zfill(4)}",
                "Campaign_Name": f"{random.choice(['Email', 'Social', 'PPC', 'Display'])} Campaign {i+1}",
                "Spend": spend,
                "Revenue": revenue,
                "Impressions": random.randint(1000, 100000),
                "Clicks": random.randint(50, 5000),
                "Date": self.fake.date_between(start_date="-6m", end_date="today").strftime("%Y-%m-%d")
            })
        
        df = pd.DataFrame(data)
        return {
            "success": True,
            "dataset": df,
            "fallback_used": True
        }
    
    def generate_for_specific_question_types(self, question_type: str, size: int = 50) -> Dict[str, Any]:
        """
        Generate data for specific question types without LLM
        """
        if question_type.lower() in ["roas", "marketing", "campaign"]:
            return self._generate_marketing_roas_data(size)
        elif question_type.lower() in ["vlookup", "lookup", "index_match"]:
            return self._generate_lookup_data(size)
        elif question_type.lower() in ["pivot", "summary", "analysis"]:
            return self._generate_pivot_data(size)
        else:
            return self._generate_fallback_data(size)
    
    def _generate_marketing_roas_data(self, size: int) -> Dict[str, Any]:
        """
        Generate marketing ROAS data specifically for ROAS calculation questions
        """
        data = []
        campaigns = ["Email Marketing", "Social Media", "Google Ads", "Facebook Ads", "Display Banner", "YouTube"]
        
        for i in range(size):
            spend = round(random.uniform(0, 10000), 2)
            
            # Ensure some zero spend values for division by zero practice
            if random.random() < 0.15:  # 15% chance of zero spend
                spend = 0
            
            # Generate revenue based on spend (with some randomness)
            if spend > 0:
                roas_multiplier = random.uniform(0.5, 8.0)  # ROAS between 0.5 and 8
                revenue = round(spend * roas_multiplier, 2)
            else:
                revenue = round(random.uniform(0, 1000), 2)  # Some revenue even with zero spend
            
            data.append({
                "Campaign_ID": f"CAM{str(i+1001).zfill(4)}",
                "Campaign_Name": f"{random.choice(campaigns)} - Q{random.randint(1,4)} 2024",
                "Spend": spend,
                "Revenue": revenue,
                "Campaign_Type": random.choice(campaigns),
                "Start_Date": self.fake.date_between(start_date="-1y", end_date="-30d").strftime("%Y-%m-%d"),
                "End_Date": self.fake.date_between(start_date="-30d", end_date="today").strftime("%Y-%m-%d"),
                "Target_Audience": random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]),
                "Platform": random.choice(["Google", "Facebook", "LinkedIn", "Twitter", "YouTube"])
            })
        
        df = pd.DataFrame(data)
        html_table = self._convert_to_html_table(df)
        
        return {
            "success": True,
            "dataset_html": html_table,
            "dataset_csv": df.to_csv(index=False),
            "dataset_info": self._get_dataset_metadata(df),
            "context_analysis": {
                "question_type": "ROAS Calculation",
                "key_challenges": ["Division by zero handling", "Formula creation", "Error checking"],
                "excel_functions_needed": ["IF", "ISERROR", "DIVIDE", "ROUND"]
            }
        }
    
    def _generate_lookup_data(self, size: int) -> Dict[str, Any]:
        """
        Generate data suitable for VLOOKUP/INDEX-MATCH exercises
        """
        # Generate main data table
        main_data = []
        product_codes = [f"PRD{str(i+1001).zfill(3)}" for i in range(20)]
        
        for i in range(size):
            main_data.append({
                "Order_ID": f"ORD{str(i+2001).zfill(4)}",
                "Product_Code": random.choice(product_codes),
                "Quantity": random.randint(1, 50),
                "Order_Date": self.fake.date_between(start_date="-6m", end_date="today").strftime("%Y-%m-%d"),
                "Customer_ID": f"CUST{random.randint(1001, 1100)}"
            })
        
        # Generate lookup table
        lookup_data = []
        for code in product_codes:
            lookup_data.append({
                "Product_Code": code,
                "Product_Name": self.fake.catch_phrase(),
                "Unit_Price": round(random.uniform(10, 500), 2),
                "Category": random.choice(["Electronics", "Clothing", "Home", "Sports", "Books"])
            })
        
        main_df = pd.DataFrame(main_data)
        lookup_df = pd.DataFrame(lookup_data)
        
        # Combine both tables with a separator
        combined_html = f"""
        <h4>Main Orders Data</h4>
        {self._convert_to_html_table(main_df)}
        
        <h4>Product Lookup Table</h4>
        {self._convert_to_html_table(lookup_df)}
        """
        
        return {
            "success": True,
            "dataset_html": combined_html,
            "dataset_csv": main_df.to_csv(index=False) + "\n\nLookup Table:\n" + lookup_df.to_csv(index=False),
            "dataset_info": {
                "main_table": self._get_dataset_metadata(main_df),
                "lookup_table": self._get_dataset_metadata(lookup_df)
            }
        }