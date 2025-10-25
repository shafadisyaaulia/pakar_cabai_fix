"""
Explanation Facility Module
Modul untuk menjelaskan proses reasoning sistem pakar
Menjawab pertanyaan WHY dan HOW
"""

from typing import Dict, List, Any, Optional

class ExplanationFacility:
    """
    Class untuk explanation facility sistem pakar
    Menyediakan kemampuan WHY dan HOW explanation
    """
    
    def __init__(self, knowledge_base, inference_engine):
        """
        Inisialisasi Explanation Facility
        
        Args:
            knowledge_base: Instance AdvancedKnowledgeBase
            inference_engine: Instance InferenceEngine
        """
        self.kb = knowledge_base
        self.engine = inference_engine
        self.explanation_history = []
    
    def explain_why(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Menjelaskan MENGAPA sistem menanyakan pertanyaan tertentu
        
        Args:
            question: Pertanyaan/kondisi yang ditanyakan
            context: Konteks current reasoning (current_facts, potential_goals)
            
        Returns:
            Dictionary penjelasan WHY
        """
        current_facts = context.get('current_facts', [])
        
        relevant_rules = []
        for rule_id, rule in self.kb.get_all_rules().items():
            if question in rule['IF']:
                satisfied = [cond for cond in rule['IF'] if cond in current_facts]
                missing = [cond for cond in rule['IF'] if cond not in current_facts]
                
                if question in missing:
                    relevant_rules.append({
                        'rule_id': rule_id,
                        'diagnosis': rule['THEN']['diagnosis'],
                        'satisfied_conditions': satisfied,
                        'missing_conditions': missing,
                        'cf': rule['CF'],
                        'explanation': rule['explanation']
                    })
        
        if not relevant_rules:
            return {
                'question': question,
                'answer': f'Pertanyaan "{question}" tidak relevan dengan rules yang ada.',
                'relevant_rules': []
            }
        
        relevant_rules.sort(key=lambda x: len(x['satisfied_conditions']), reverse=True)
        
        explanation = {
            'question': question,
            'answer': self._generate_why_explanation(question, relevant_rules),
            'relevant_rules': relevant_rules,
            'potential_diagnoses': [r['diagnosis'] for r in relevant_rules],
            'total_rules_affected': len(relevant_rules)
        }
        
        self._add_to_history('WHY', explanation)
        return explanation
    
    def _generate_why_explanation(self, question: str, relevant_rules: List[Dict]) -> str:
        if len(relevant_rules) == 0:
            return f"Sistem tidak memerlukan informasi tentang '{question}' untuk diagnosis saat ini."
        
        top_rule = relevant_rules[0]
        
        explanation = f"Sistem menanyakan '{question}' karena:\n\n"
        explanation += f"1. Informasi ini diperlukan untuk mendiagnosis '{top_rule['diagnosis']}'\n"
        explanation += f"2. Sudah ada {len(top_rule['satisfied_conditions'])} kondisi yang terpenuhi: "
        explanation += ", ".join(top_rule['satisfied_conditions'][:3])
        if len(top_rule['satisfied_conditions']) > 3:
            explanation += f", dan {len(top_rule['satisfied_conditions']) - 3} lainnya"
        explanation += f"\n3. Tingkat kepercayaan rule ini: {top_rule['cf']*100:.0f}%\n"
        
        if len(relevant_rules) > 1:
            explanation += f"\nInformasi ini juga mempengaruhi {len(relevant_rules)-1} diagnosis lainnya: "
            other_diagnoses = [r['diagnosis'] for r in relevant_rules[1:4]]
            explanation += ", ".join(other_diagnoses)
            if len(relevant_rules) > 4:
                explanation += f", dan {len(relevant_rules)-4} lainnya"
        
        return explanation
    
    def explain_how(self, conclusion: str, reasoning_path: List[Dict]) -> Dict[str, Any]:
        relevant_steps = [
            step for step in reasoning_path 
            if conclusion.lower() in step['conclusion'].lower()
        ]
        
        if not relevant_steps:
            return {
                'conclusion': conclusion,
                'answer': f'Sistem tidak menemukan kesimpulan "{conclusion}" dalam reasoning.',
                'steps': []
            }
        
        explanation = {
            'conclusion': conclusion,
            'answer': self._generate_how_explanation(conclusion, relevant_steps),
            'steps': self._format_reasoning_steps(relevant_steps),
            'rules_used': [step['rule'] for step in relevant_steps],
            'total_steps': len(relevant_steps)
        }
        
        self._add_to_history('HOW', explanation)
        return explanation
    
    def _generate_how_explanation(self, conclusion: str, steps: List[Dict]) -> str:
        if len(steps) == 0:
            return f"Sistem tidak dapat menemukan kesimpulan '{conclusion}'."
        
        explanation = f"Sistem sampai pada kesimpulan '{conclusion}' melalui langkah berikut:\n\n"
        
        for step in steps:
            explanation += f"Langkah {step['step']}:\n"
            explanation += f"  - Menggunakan Rule {step['rule']}\n"
            explanation += f"  - Kondisi yang terpenuhi: {', '.join(step['conditions'])}\n"
            explanation += f"  - Kesimpulan: {step['conclusion']}\n"
            explanation += f"  - Tingkat kepercayaan: {step['cf']*100:.1f}%\n\n"
        
        final_cf = steps[-1]['cf']
        explanation += f"Kesimpulan akhir memiliki tingkat kepercayaan {final_cf*100:.1f}%, "
        
        if final_cf >= 0.8:
            explanation += "yang menunjukkan diagnosis sangat kuat."
        elif final_cf >= 0.6:
            explanation += "yang menunjukkan diagnosis cukup kuat."
        elif final_cf >= 0.4:
            explanation += "yang menunjukkan diagnosis moderat."
        else:
            explanation += "yang menunjukkan diagnosis lemah dan memerlukan konfirmasi tambahan."
        
        return explanation
    
    def _format_reasoning_steps(self, steps: List[Dict]) -> List[Dict]:
        formatted = []
        
        for step in steps:
            rule = self.kb.get_rule(step['rule'])
            
            formatted_step = {
                'step_number': step['step'],
                'rule_id': step['rule'],
                'if_conditions': step['conditions'],
                'then_conclusion': step['conclusion'],
                'certainty_factor': step['cf'],
                'cf_percentage': f"{step['cf']*100:.1f}%",
                'rule_explanation': rule['explanation'] if rule else 'N/A',
                'recommendation': rule['THEN'] if rule else None
            }
            
            formatted.append(formatted_step)
        
        return formatted
    
    def explain_rule(self, rule_id: str) -> Dict[str, Any]:
        rule = self.kb.get_rule(rule_id)
        
        if not rule:
            return {
                'error': f'Rule {rule_id} tidak ditemukan',
                'rule_id': rule_id
            }
        
        explanation = {
            'rule_id': rule_id,
            'structure': {
                'IF': rule['IF'],
                'THEN': rule['THEN'],
                'CF': rule['CF']
            },
            'natural_language': self._rule_to_natural_language(rule_id, rule),
            'expert_explanation': rule['explanation'],
            'certainty_factor': {
                'value': rule['CF'],
                'percentage': f"{rule['CF']*100:.0f}%",
                'interpretation': self._interpret_rule_cf(rule['CF'])
            },
            'recommendation_details': rule['THEN']
        }
    
        try:
            if hasattr(self.kb, 'validate_rule'):
                validation = self.kb.validate_rule(rule_id)
                explanation['validation'] = validation
            else:
                explanation['validation'] = {'status': 'ok', 'message': 'Validation not available'}
        except Exception as e:
            explanation['validation'] = {'status': 'error', 'message': str(e)}
        
        self._add_to_history('RULE', explanation)
        return explanation

    
    def _rule_to_natural_language(self, rule_id: str, rule: Dict) -> str:
        nl = f"Rule {rule_id} menyatakan bahwa:\n\n"
        nl += "JIKA:\n"
        for i, condition in enumerate(rule['IF'], 1):
            nl += f"  {i}. {condition}\n"
        nl += "\nMAKA:\n"
        nl += f"  - Diagnosis: {rule['THEN']['diagnosis']}\n"
        nl += f"  - Pupuk yang direkomendasikan: {rule['THEN']['pupuk']}\n"
        nl += f"  - Dosis: {rule['THEN']['dosis']}\n"
        nl += f"  - Metode aplikasi: {rule['THEN']['metode']}\n"
        nl += f"\nDengan tingkat kepercayaan: {rule['CF']*100:.0f}%"
        
        return nl
    
    def _interpret_rule_cf(self, cf: float) -> str:
        if cf >= 0.9:
            return "Sangat tinggi - Rule ini memiliki dasar yang sangat kuat"
        elif cf >= 0.8:
            return "Tinggi - Rule ini dapat diandalkan"
        elif cf >= 0.7:
            return "Cukup tinggi - Rule ini cukup dapat dipercaya"
        elif cf >= 0.6:
            return "Moderat - Rule ini memerlukan evidence pendukung"
        else:
            return "Rendah - Rule ini memerlukan validasi tambahan"
    
    def explain_comparison(self, diagnoses: List[Dict]) -> Dict[str, Any]:
        if len(diagnoses) < 2:
            return {
                'message': 'Memerlukan minimal 2 diagnosis untuk perbandingan',
                'diagnoses_count': len(diagnoses)
            }
        
        sorted_diagnoses = sorted(diagnoses, key=lambda x: x['cf'], reverse=True)
        
        comparison = {
            'total_diagnoses': len(diagnoses),
            'top_diagnosis': sorted_diagnoses[0]['diagnosis'],
            'top_cf': sorted_diagnoses[0]['cf'],
            'differences': [],
            'summary': self._generate_comparison_summary(sorted_diagnoses)
        }
        
        top = sorted_diagnoses[0]
        for other in sorted_diagnoses[1:]:
            diff = {
                'diagnosis': other['diagnosis'],
                'cf': other['cf'],
                'cf_difference': top['cf'] - other['cf'],
                'rules_comparison': self._compare_rules(top['rule_id'], other['rule_id'])
            }
            comparison['differences'].append(diff)
        
        self._add_to_history('COMPARISON', comparison)
        return comparison
    
    def _generate_comparison_summary(self, diagnoses: List[Dict]) -> str:
        if not diagnoses:
            return "Tidak ada diagnosis untuk dibandingkan."
        
        top = diagnoses[0]
        summary = f"Diagnosis paling mungkin adalah '{top['diagnosis']}' "
        summary += f"dengan tingkat kepercayaan {top['cf']*100:.1f}%.\n\n"
        
        if len(diagnoses) > 1:
            second = diagnoses[1]
            diff = (top['cf'] - second['cf']) * 100
            
            if diff < 10:
                summary += f"Diagnosis ini sangat dekat dengan '{second['diagnosis']}' "
                summary += f"(selisih hanya {diff:.1f}%). Disarankan untuk melakukan konfirmasi tambahan."
            elif diff < 20:
                summary += f"Diagnosis ini cukup lebih kuat dari '{second['diagnosis']}' "
                summary += f"(selisih {diff:.1f}%)."
            else:
                summary += f"Diagnosis ini jauh lebih kuat dari alternatif lainnya "
                summary += f"(selisih minimal {diff:.1f}%)."
        
        return summary
    
    def _compare_rules(self, rule_id1: str, rule_id2: str) -> Dict[str, Any]:
        rule1 = self.kb.get_rule(rule_id1)
        rule2 = self.kb.get_rule(rule_id2)
        
        if not (rule1 and rule2):
            return {'error': 'One or both rules not found'}
        
        return {
            'rule1_conditions': len(rule1['IF']),
            'rule2_conditions': len(rule2['IF']),
            'rule1_cf': rule1['CF'],
            'rule2_cf': rule2['CF'],
            'common_conditions': list(set(rule1['IF']) & set(rule2['IF'])),
            'unique_to_rule1': list(set(rule1['IF']) - set(rule2['IF'])),
            'unique_to_rule2': list(set(rule2['IF']) - set(rule1['IF']))
        }
    
    def _add_to_history(self, explanation_type: str, explanation: Dict):
        self.explanation_history.append({
            'type': explanation_type,
            'timestamp': self._get_timestamp(),
            'explanation': explanation
        })
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_explanation_history(self) -> List[Dict]:
        return self.explanation_history
    
    def clear_history(self):
        self.explanation_history = []
    
    def generate_full_report(self, consultation_result: Dict) -> str:
        report = "="*70 + "\n"
        report += "LAPORAN PENJELASAN SISTEM PAKAR PUPUK CABAI\n"
        report += "="*70 + "\n\n"
        
        report += "1. FAKTA INPUT\n"
        report += "-"*70 + "\n"
        facts = consultation_result.get('facts', [])
        for i, fact in enumerate(facts, 1):
            report += f"   {i}. {fact}\n"
        report += "\n"
        
        report += "2. HASIL DIAGNOSIS\n"
        report += "-"*70 + "\n"
        conclusions = consultation_result.get('conclusions', [])
        for i, conclusion in enumerate(conclusions, 1):
            report += f"   {i}. {conclusion['diagnosis']}\n"
            report += f"      Certainty Factor: {conclusion['cf']*100:.1f}%\n"
            report += f"      Pupuk: {conclusion['recommendation']['pupuk']}\n"
            report += f"      Dosis: {conclusion['recommendation']['dosis']}\n"
            report += f"      Metode: {conclusion['recommendation']['metode']}\n\n"
        
        report += "3. ALUR PENALARAN\n"
        report += "-"*70 + "\n"
        reasoning_path = consultation_result.get('reasoning_path', [])
        for step in reasoning_path:
            report += f"   Step {step['step']}: Rule {step['rule']}\n"
            report += f"   IF: {' AND '.join(step['conditions'])}\n"
            report += f"   THEN: {step['conclusion']}\n"
            report += f"   CF: {step['cf']*100:.1f}%\n\n"
        
        report += "4. RULES YANG DIGUNAKAN\n"
        report += "-"*70 + "\n"
        used_rules = consultation_result.get('used_rules', [])
        report += f"   Total: {len(used_rules)} rules\n"
        report += f"   Rules: {', '.join(used_rules)}\n\n"
        
        report += "="*70 + "\n"
        report += f"Generated at: {self._get_timestamp()}\n"
        report += "="*70 + "\n"
        
        return report
