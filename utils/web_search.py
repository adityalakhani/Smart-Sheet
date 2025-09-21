"""
Web Search Tool for agents to research Excel best practices and current information
"""

import requests
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WebSearchTool:
    """
    Web search tool using DuckDuckGo API for researching Excel information
    """
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.headers = {
            'User-Agent': 'ExcelInterviewer/1.0 (Educational Tool)'
        }
    
    def search_excel_topic(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Search for Excel-related information
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            dict: Search results and metadata
        """
        try:
            # Enhance query with Excel context if not present
            if "excel" not in query.lower():
                enhanced_query = f"Microsoft Excel {query}"
            else:
                enhanced_query = query
            
            # Simple web search implementation
            # In a real implementation, you'd use a proper search API
            results = self._perform_search(enhanced_query, max_results)
            
            return {
                "success": True,
                "query": enhanced_query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def _perform_search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Perform the actual web search
        
        Args:
            query (str): Search query
            max_results (int): Maximum results
            
        Returns:
            list: Search results
        """
        # Mock search results for Excel topics
        # In production, integrate with a real search API
        mock_results = [
            {
                "title": f"Excel Guide: {query}",
                "url": "https://support.microsoft.com/excel",
                "snippet": f"Comprehensive guide covering {query} with step-by-step instructions and examples.",
                "source": "Microsoft Support"
            },
            {
                "title": f"Best Practices for {query}",
                "url": "https://excel-university.com",
                "snippet": f"Professional tips and best practices for implementing {query} in Excel workbooks.",
                "source": "Excel University"
            },
            {
                "title": f"Advanced {query} Techniques",
                "url": "https://chandoo.org",
                "snippet": f"Advanced techniques and formulas for mastering {query} in Excel.",
                "source": "Chandoo.org"
            }
        ]
        
        return mock_results[:max_results]
    
    def search_excel_function(self, function_name: str) -> Dict[str, Any]:
        """
        Search for specific Excel function information
        
        Args:
            function_name (str): Excel function name
            
        Returns:
            dict: Function information
        """
        query = f"Excel {function_name} function syntax examples"
        return self.search_excel_topic(query, max_results=2)
    
    def search_excel_best_practices(self, topic: str) -> Dict[str, Any]:
        """
        Search for Excel best practices on a specific topic
        
        Args:
            topic (str): Topic for best practices
            
        Returns:
            dict: Best practices information
        """
        query = f"Excel best practices {topic}"
        return self.search_excel_topic(query, max_results=3)
    
    def search_troubleshooting(self, issue: str) -> Dict[str, Any]:
        """
        Search for troubleshooting information
        
        Args:
            issue (str): Excel issue to troubleshoot
            
        Returns:
            dict: Troubleshooting information
        """
        query = f"Excel troubleshoot fix {issue}"
        return self.search_excel_topic(query, max_results=2)