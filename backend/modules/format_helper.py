"""
Format Helper Module
Utility functions untuk formatting data
"""

from datetime import datetime
from typing import Dict, List, Any


class FormatHelper:
    """Helper class untuk formatting data diagnosis dan lainnya"""
    
    def __init__(self):
        pass
    
    def format_diagnosis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format hasil diagnosis agar lebih konsisten dan user-friendly
        
        Args:
            result: Raw result dari inference engine
            
        Returns:
            Formatted result
        """
        formatted = {
            "consultation_id": result.get("consultation_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "symptoms": result.get("symptoms", []),
            "fase": result.get("fase", ""),
            "conclusions": []
        }
        
        # Format each conclusion
        for conclusion in result.get("conclusions", []):
            formatted_conclusion = {
                "rule_id": conclusion.get("rule_id", ""),
                "diagnosis": self.format_diagnosis_name(conclusion.get("diagnosis", "")),
                "cf": round(conclusion.get("cf", 0.0), 3),
                "cf_percentage": f"{conclusion.get('cf', 0.0) * 100:.1f}%",
                "cf_interpretation": conclusion.get("cf_interpretation", ""),
                "recommendation": self.format_recommendation(conclusion.get("recommendation", {})),
                "explanation": conclusion.get("explanation", ""),
                "conditions": conclusion.get("conditions", [])
            }
            formatted["conclusions"].append(formatted_conclusion)
        
        # Add metadata
        formatted["metadata"] = {
            "total_conclusions": len(formatted["conclusions"]),
            "highest_cf": max([c["cf"] for c in formatted["conclusions"]]) if formatted["conclusions"] else 0.0,
            "used_rules": result.get("used_rules", []),
            "total_iterations": result.get("total_iterations", 0)
        }
        
        return formatted
    
    def format_diagnosis_name(self, diagnosis: str) -> str:
        """Format nama diagnosis agar lebih readable"""
        # Capitalize first letter of each word
        return diagnosis.replace("_", " ").title()
    
    def format_recommendation(self, recommendation: Dict) -> Dict:
        """Format rekomendasi"""
        return {
            "pupuk": recommendation.get("pupuk", "N/A"),
            "dosis": recommendation.get("dosis", "N/A"),
            "metode": recommendation.get("metode", "N/A"),
            "timing": recommendation.get("timing", "Sesuai fase pertumbuhan"),
            "catatan": recommendation.get("catatan", "")
        }
    
    def format_symptom_name(self, symptom: str) -> str:
        """Format nama gejala untuk display"""
        return symptom.replace("_", " ").capitalize()
    
    def format_rule_for_display(self, rule: Dict) -> Dict:
        """Format rule untuk ditampilkan di UI"""
        return {
            "id": rule.get("id", ""),
            "name": rule.get("name", ""),
            "conditions": [self.format_symptom_name(c) for c in rule.get("IF", [])],
            "conclusion": self.format_diagnosis_name(rule.get("THEN", {}).get("diagnosis", "")),
            "cf": rule.get("CF", 0.0),
            "status": rule.get("status", "active"),
            "created_at": rule.get("created_at", ""),
            "updated_at": rule.get("updated_at", "")
        }
    
    def format_history_item(self, item: Dict) -> Dict:
        """Format history item untuk display"""
        return {
            "consultation_id": item.get("consultation_id", "unknown"),
            "timestamp": item.get("timestamp", ""),
            "timestamp_formatted": self.format_timestamp(item.get("timestamp", "")),
            "diagnosis": self.format_diagnosis_name(item.get("diagnosis", "")),
            "cf": round(float(item.get("cf", 0.0)), 3),
            "cf_percentage": f"{float(item.get('cf', 0.0)) * 100:.1f}%",
            "fase": item.get("fase", ""),
            "symptoms_count": len(item.get("symptoms", []))
        }
    
    def format_timestamp(self, timestamp: str) -> str:
        """Format timestamp ke format yang lebih readable"""
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%d %B %Y, %H:%M")
        except:
            return timestamp
