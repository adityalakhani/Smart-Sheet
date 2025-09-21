"""
Report Generator for creating comprehensive interview reports and feedback
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json

class ReportGenerator:
    """
    Generates various types of reports for the Excel interview system
    """
    
    def __init__(self):
        self.report_templates = {
            "candidate_feedback": self._candidate_feedback_template,
            "hiring_manager": self._hiring_manager_template,
            "interview_summary": self._interview_summary_template,
            "performance_analysis": self._performance_analysis_template
        }
    
    def generate_candidate_feedback_report(self, 
                                          candidate_name: str,
                                          final_decision: Dict[str, Any],
                                          interview_data: Dict[str, Any],
                                          evaluations: List[Dict[str, Any]]) -> str:
        """
        Generate comprehensive feedback report for candidate
        
        Args:
            candidate_name (str): Name of the candidate
            final_decision (dict): Final hiring decision data
            interview_data (dict): Complete interview session data
            evaluations (list): List of question evaluations
            
        Returns:
            str: Formatted feedback report
        """
        
        report = f"""
# Excel Proficiency Assessment - Candidate Feedback Report

**Candidate:** {candidate_name}
**Assessment Date:** {datetime.now().strftime('%B %d, %Y')}
**Interview Duration:** {interview_data.get('duration', 'N/A')}
**Questions Completed:** {len(evaluations)}

## Overall Performance Summary

**Final Result:** {final_decision.get('decision', 'N/A')}
**Overall Score:** {final_decision.get('overall_score', 'N/A')}/100
**Assessment Confidence:** {final_decision.get('confidence_level', 'N/A')}

{final_decision.get('recommendation_summary', '')}

## Skill Area Assessment

"""
        
        # Add skill breakdown
        skill_assessment = final_decision.get('skill_assessment', {})
        for skill, rating in skill_assessment.items():
            skill_display = skill.replace('_', ' ').title()
            report += f"**{skill_display}:** {rating}\n"
        
        report += "\n## Detailed Performance Analysis\n\n"
        
        # Add question-by-question feedback
        for i, evaluation in enumerate(evaluations, 1):
            if evaluation.get('success') and evaluation.get('evaluation'):
                eval_data = evaluation['evaluation']
                report += f"### Question {i}: {eval_data.get('skill_target', 'Unknown Skill')}\n\n"
                report += f"**Grade:** {eval_data.get('grade', 'N/A')}\n"
                report += f"**Score:** {eval_data.get('score', 'N/A')}/100\n\n"
                report += f"**Feedback:** {eval_data.get('justification', 'No feedback available')}\n\n"
                
                if eval_data.get('strengths'):
                    report += "**Strengths Demonstrated:**\n"
                    for strength in eval_data['strengths']:
                        report += f"• {strength}\n"
                    report += "\n"
                
                if eval_data.get('weaknesses'):
                    report += "**Areas for Improvement:**\n"
                    for weakness in eval_data['weaknesses']:
                        report += f"• {weakness}\n"
                    report += "\n"
        
        # Add recommendations
        report += "## Development Recommendations\n\n"
        if final_decision.get('improvement_areas'):
            for area in final_decision['improvement_areas']:
                report += f"• {area}\n"
        
        if final_decision.get('follow_up_recommendations'):
            report += "\n## Next Steps\n\n"
            for rec in final_decision['follow_up_recommendations']:
                report += f"• {rec}\n"
        
        report += f"\n\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*"
        
        return report
    
    def generate_hiring_manager_report(self,
                                      candidate_name: str,
                                      role_title: str,
                                      final_decision: Dict[str, Any],
                                      performance_metrics: Dict[str, Any],
                                      interview_data: Dict[str, Any]) -> str:
        """
        Generate executive summary report for hiring managers
        
        Args:
            candidate_name (str): Name of the candidate
            role_title (str): Position being interviewed for
            final_decision (dict): Final hiring decision
            performance_metrics (dict): Performance analysis
            interview_data (dict): Interview session data
            
        Returns:
            str: Executive summary report
        """
        
        report = f"""
# Hiring Manager Report - Excel Proficiency Assessment

## Candidate Summary
- **Candidate:** {candidate_name}
- **Position:** {role_title}
- **Assessment Date:** {datetime.now().strftime('%B %d, %Y')}
- **Interview Duration:** {interview_data.get('duration', 'N/A')}

## Executive Summary

**RECOMMENDATION: {final_decision.get('decision', 'N/A').upper()}**
**Confidence Level:** {final_decision.get('confidence_level', 'N/A')}
**Overall Score:** {final_decision.get('overall_score', 'N/A')}/100

{final_decision.get('recommendation_summary', '')}

## Performance Metrics

- **Questions Answered:** {performance_metrics.get('total_questions', 0)}
- **Average Score:** {performance_metrics.get('average_score', 0)}/100
- **Pass Rate:** {performance_metrics.get('pass_rate', 0):.1f}%
- **Performance Trend:** {performance_metrics.get('performance_trend', 'N/A').title()}

### Grade Distribution
"""
        
        # Add grade distribution
        grade_dist = performance_metrics.get('grade_distribution', {})
        for grade, count in grade_dist.items():
            report += f"- **{grade}:** {count} question(s)\n"
        
        report += "\n## Key Strengths\n\n"
        if final_decision.get('strengths'):
            for strength in final_decision['strengths']:
                report += f"• {strength}\n"
        
        report += "\n## Areas of Concern\n\n"
        if final_decision.get('weaknesses'):
            for weakness in final_decision['weaknesses']:
                report += f"• {weakness}\n"
        
        # Add next steps
        report += f"\n## Recommended Next Steps\n\n{final_decision.get('next_steps', 'No specific next steps provided.')}"
        
        report += f"\n\n---\n*Executive Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*"
        
        return report
    
    def generate_interview_summary(self, interview_data: Dict[str, Any]) -> str:
        """
        Generate technical interview summary
        
        Args:
            interview_data (dict): Complete interview session data
            
        Returns:
            str: Technical summary report
        """
        
        report = f"""
# Interview Session Summary

**Session ID:** {interview_data.get('session_id', 'N/A')}
**Start Time:** {interview_data.get('start_time', 'N/A')}
**End Time:** {interview_data.get('end_time', 'N/A')}
**Total Duration:** {interview_data.get('duration', 'N/A')}

## Session Statistics

- **Questions Asked:** {len(interview_data.get('questions', []))}
- **Responses Recorded:** {len(interview_data.get('responses', []))}
- **Average Response Time:** {interview_data.get('avg_response_time', 'N/A')}
- **Session Completion:** {'Complete' if interview_data.get('completed') else 'Incomplete'}

## Question Sequence

"""
        
        questions = interview_data.get('questions', [])
        for i, question in enumerate(questions, 1):
            report += f"{i}. **{question.get('skill_target', 'Unknown')}** ({question.get('difficulty', 'Unknown')})\n"
            report += f"   {question.get('question', 'No question text')[:100]}...\n\n"
        
        return report
    
    def generate_performance_analysis(self, 
                                    evaluations: List[Dict[str, Any]],
                                    skills_tested: List[str]) -> str:
        """
        Generate detailed performance analysis
        
        Args:
            evaluations (list): Question evaluations
            skills_tested (list): List of skills that were tested
            
        Returns:
            str: Performance analysis report
        """
        
        report = """
# Detailed Performance Analysis

## Skills Assessment Matrix

"""
        
        # Analyze performance by skill
        skill_performance = {}
        for evaluation in evaluations:
            if evaluation.get('success') and evaluation.get('evaluation'):
                skill = evaluation['evaluation'].get('skill_target', 'Unknown')
                score = evaluation['evaluation'].get('score', 0)
                grade = evaluation['evaluation'].get('grade', 'N/A')
                
                if skill not in skill_performance:
                    skill_performance[skill] = []
                skill_performance[skill].append({'score': score, 'grade': grade})
        
        for skill, performances in skill_performance.items():
            avg_score = sum(p['score'] for p in performances) / len(performances)
            grades = [p['grade'] for p in performances]
            
            report += f"### {skill}\n"
            report += f"- **Questions Asked:** {len(performances)}\n"
            report += f"- **Average Score:** {avg_score:.1f}/100\n"
            report += f"- **Grades:** {', '.join(grades)}\n\n"
        
        return report
    
    def export_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Export report data to JSON format
        
        Args:
            data (dict): Report data
            filename (str, optional): Output filename
            
        Returns:
            str: JSON formatted data
        """
        json_data = {
            "report_generated": datetime.now().isoformat(),
            "data": data
        }
        
        json_output = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(json_output)
            except Exception as e:
                print(f"Error saving JSON file: {e}")
        
        return json_output
    
    def _candidate_feedback_template(self) -> str:
        """Template for candidate feedback reports"""
        return """
        # Candidate Feedback Template
        - Overall performance summary
        - Skill-by-skill breakdown
        - Specific strengths and improvements
        - Development recommendations
        - Next steps
        """
    
    def _hiring_manager_template(self) -> str:
        """Template for hiring manager reports"""
        return """
        # Hiring Manager Template
        - Executive summary
        - Recommendation with confidence level
        - Key performance metrics
        - Risk assessment
        - Next steps in hiring process
        """
    
    def _interview_summary_template(self) -> str:
        """Template for interview summary reports"""
        return """
        # Interview Summary Template
        - Session metadata
        - Question sequence and responses
        - Technical metrics
        - Completion status
        """
    
    def _performance_analysis_template(self) -> str:
        """Template for performance analysis reports"""
        return """
        # Performance Analysis Template
        - Skills matrix
        - Score distributions
        - Trend analysis
        - Comparative metrics
        """
    
    def generate_custom_report(self, 
                              template_name: str,
                              data: Dict[str, Any],
                              **kwargs) -> str:
        """
        Generate custom report using specified template
        
        Args:
            template_name (str): Name of template to use
            data (dict): Data for report generation
            **kwargs: Additional parameters
            
        Returns:
            str: Generated report
        """
        if template_name not in self.report_templates:
            return f"Template '{template_name}' not found"
        
        template_func = self.report_templates[template_name]
        return template_func()
    
    def create_summary_statistics(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create summary statistics from evaluations
        
        Args:
            evaluations (list): List of evaluation results
            
        Returns:
            dict: Summary statistics
        """
        if not evaluations:
            return {"error": "No evaluations provided"}
        
        successful_evals = [e for e in evaluations if e.get('success')]
        
        if not successful_evals:
            return {"error": "No successful evaluations"}
        
        scores = []
        grades = []
        skills = []
        
        for evaluation in successful_evals:
            eval_data = evaluation.get('evaluation', {})
            if 'score' in eval_data:
                scores.append(eval_data['score'])
            if 'grade' in eval_data:
                grades.append(eval_data['grade'])
            if 'skill_target' in eval_data:
                skills.append(eval_data['skill_target'])
        
        # Calculate statistics
        stats = {
            "total_questions": len(successful_evals),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "skills_tested": len(set(skills)),
            "unique_skills": list(set(skills))
        }
        
        # Grade distribution
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        stats["grade_distribution"] = grade_counts
        
        # Performance level
        if stats["average_score"] >= 80:
            stats["performance_level"] = "Excellent"
        elif stats["average_score"] >= 70:
            stats["performance_level"] = "Good"
        elif stats["average_score"] >= 60:
            stats["performance_level"] = "Fair"
        else:
            stats["performance_level"] = "Needs Improvement"
        
        return stats