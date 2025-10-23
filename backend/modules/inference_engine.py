"""
Inference Engine Module
Implementasi Forward Chaining dan Backward Chaining
untuk reasoning pada sistem pakar
"""

from typing import Dict, List, Any, Tuple
from modules.certainty_factor import CertaintyFactor


class InferenceEngine:
    """
    Mesin inferensi untuk sistem pakar
    Mengimplementasikan Forward Chaining dan Backward Chaining
    """
    
    def __init__(self, knowledge_base):
        """
        Inisialisasi Inference Engine
        
        Args:
            knowledge_base: Instance dari KnowledgeBase class
        """
        self.kb = knowledge_base
        self.cf_calculator = CertaintyFactor()
        self.working_memory = []
        self.used_rules = []
        self.reasoning_path = []
    
    def reset_memory(self):
        """Reset working memory dan reasoning path"""
        self.working_memory = []
        self.used_rules = []
        self.reasoning_path = []
    
    def forward_chaining(self, facts: List[str], user_cfs: Dict[str, float]) -> Dict[str, Any]:
        """
        Forward Chaining: Data-Driven Reasoning
        Dimulai dari fakta yang diketahui, mencari kesimpulan
        
        Args:
            facts: List fakta yang diketahui dari user
            user_cfs: Dictionary CF untuk setiap fakta dari user
            
        Returns:
            Dictionary berisi conclusions, used_rules, reasoning_path
        """
        self.reset_memory()
        self.working_memory = facts.copy()
        conclusions = []
        
        print("\n=== FORWARD CHAINING STARTED ===")
        print(f"Initial Facts: {facts}")
        
        iteration = 0
        max_iterations = 50  # Prevent infinite loop
        
        while iteration < max_iterations:
            iteration += 1
            fired_rule = False
            
            # Iterasi melalui semua rules
            for rule_id, rule in self.kb.get_all_rules().items():
                # Skip jika rule sudah digunakan
                if rule_id in self.used_rules:
                    continue
                
                # Check apakah semua kondisi IF terpenuhi
                conditions_met = all(cond in self.working_memory for cond in rule['IF'])
                
                if conditions_met:
                    # Rule dapat di-fire
                    fired_rule = True
                    
                    # Hitung CF kombinasi
                    matched_cfs = [user_cfs.get(cond, 0.8) for cond in rule['IF']]
                    final_cf = self.cf_calculator.calculate_rule_cf(rule['CF'], matched_cfs)
                    
                    # Tambahkan ke conclusions
                    conclusion = {
                        'rule_id': rule_id,
                        'diagnosis': rule['THEN']['diagnosis'],
                        'recommendation': rule['THEN'],
                        'cf': final_cf,
                        'cf_interpretation': self.cf_calculator.interpret_cf(final_cf),
                        'explanation': rule['explanation'],
                        'conditions': rule['IF']
                    }
                    conclusions.append(conclusion)
                    
                    # Update working memory
                    new_fact = rule['THEN']['diagnosis']
                    if new_fact not in self.working_memory:
                        self.working_memory.append(new_fact)
                    
                    # Tandai rule sebagai used
                    self.used_rules.append(rule_id)
                    
                    # Tambahkan ke reasoning path
                    self.reasoning_path.append({
                        'step': len(self.reasoning_path) + 1,
                        'rule': rule_id,
                        'conditions': rule['IF'],
                        'conclusion': rule['THEN']['diagnosis'],
                        'cf': final_cf,
                        'reasoning': f"IF {' AND '.join(rule['IF'])} THEN {rule['THEN']['diagnosis']}"
                    })
                    
                    print(f"Step {len(self.reasoning_path)}: Rule {rule_id} fired")
                    print(f"  Conclusion: {rule['THEN']['diagnosis']} (CF: {final_cf:.3f})")
            
            # Jika tidak ada rule yang fire, hentikan
            if not fired_rule:
                break
        
        # Sort conclusions berdasarkan CF tertinggi
        conclusions.sort(key=lambda x: x['cf'], reverse=True)
        
        print(f"\n=== FORWARD CHAINING COMPLETED ===")
        print(f"Total iterations: {iteration}")
        print(f"Rules fired: {len(self.used_rules)}")
        print(f"Conclusions found: {len(conclusions)}")
        
        return {
            'conclusions': conclusions[:5],  # Top 5 diagnosa
            'all_conclusions': conclusions,
            'used_rules': self.used_rules,
            'reasoning_path': self.reasoning_path,
            'working_memory': self.working_memory,
            'total_iterations': iteration
        }
    
    def backward_chaining(self, goal: str, known_facts: List[str]) -> Dict[str, Any]:
        """
        Backward Chaining: Goal-Driven Reasoning
        Dimulai dari hipotesis/goal, bekerja mundur untuk membuktikan fakta
        
        Args:
            goal: Diagnosis yang ingin dibuktikan
            known_facts: Fakta yang sudah diketahui
            
        Returns:
            Dictionary berisi status pembuktian dan fakta yang dibutuhkan
        """
        print(f"\n=== BACKWARD CHAINING STARTED ===")
        print(f"Goal: {goal}")
        print(f"Known Facts: {known_facts}")
        
        # Cari rules yang menghasilkan goal
        relevant_rules = []
        for rule_id, rule in self.kb.get_all_rules().items():
            if goal.lower() in rule['THEN']['diagnosis'].lower():
                relevant_rules.append((rule_id, rule))
        
        if not relevant_rules:
            return {
                'goal': goal,
                'proven': False,
                'message': f'Tidak ada rule yang menghasilkan diagnosis: {goal}',
                'relevant_rules': []
            }
        
        results = []
        
        for rule_id, rule in relevant_rules:
            required_facts = rule['IF']
            satisfied_facts = [f for f in required_facts if f in known_facts]
            missing_facts = [f for f in required_facts if f not in known_facts]
            
            can_prove = len(missing_facts) == 0
            
            result = {
                'rule_id': rule_id,
                'goal': goal,
                'required_facts': required_facts,
                'satisfied_facts': satisfied_facts,
                'missing_facts': missing_facts,
                'can_prove': can_prove,
                'cf': rule['CF'],
                'recommendation': rule['THEN']
            }
            
            results.append(result)
            
            if can_prove:
                print(f"✓ Goal dapat dibuktikan dengan Rule {rule_id}")
            else:
                print(f"✗ Goal tidak dapat dibuktikan dengan Rule {rule_id}")
                print(f"  Missing facts: {missing_facts}")
        
        # Check apakah ada rule yang bisa membuktikan goal
        proven = any(r['can_prove'] for r in results)
        
        return {
            'goal': goal,
            'proven': proven,
            'relevant_rules': results,
            'message': 'Goal terbukti' if proven else 'Goal tidak dapat dibuktikan dengan fakta yang ada'
        }
    
    def hybrid_reasoning(self, facts: List[str], user_cfs: Dict[str, float], 
                        verify_goal: str = None) -> Dict[str, Any]:
        """
        Hybrid Reasoning: Kombinasi Forward dan Backward Chaining
        
        Args:
            facts: Fakta yang diketahui
            user_cfs: CF untuk setiap fakta
            verify_goal: Optional goal untuk diverifikasi dengan backward chaining
            
        Returns:
            Dictionary hasil reasoning hybrid
        """
        print("\n=== HYBRID REASONING ===")
        
        # Jalankan Forward Chaining dulu
        forward_result = self.forward_chaining(facts, user_cfs)
        
        result = {
            'forward_chaining': forward_result,
            'backward_chaining': None
        }
        
        # Jika ada goal yang ingin diverifikasi
        if verify_goal:
            backward_result = self.backward_chaining(verify_goal, facts)
            result['backward_chaining'] = backward_result
            
            # Cross-validate hasil
            forward_diagnoses = [c['diagnosis'] for c in forward_result['conclusions']]
            if verify_goal in forward_diagnoses and backward_result['proven']:
                result['validation'] = {
                    'status': 'CONFIRMED',
                    'message': f'Diagnosis {verify_goal} dikonfirmasi oleh forward dan backward chaining'
                }
            elif verify_goal in forward_diagnoses and not backward_result['proven']:
                result['validation'] = {
                    'status': 'PARTIAL',
                    'message': f'Forward chaining menemukan {verify_goal}, tetapi backward chaining membutuhkan fakta tambahan'
                }
            else:
                result['validation'] = {
                    'status': 'NOT_CONFIRMED',
                    'message': f'Diagnosis {verify_goal} tidak dikonfirmasi'
                }
        
        return result
    
    def explain_reasoning(self, rule_id: str) -> Dict[str, Any]:
        """
        Menjelaskan mengapa suatu rule digunakan dalam reasoning
        
        Args:
            rule_id: ID rule yang ingin dijelaskan
            
        Returns:
            Dictionary penjelasan reasoning
        """
        rule = self.kb.get_rule(rule_id)
        if not rule:
            return {'error': f'Rule {rule_id} tidak ditemukan'}
        
        # Cari di reasoning path
        path_entry = next((p for p in self.reasoning_path if p['rule'] == rule_id), None)
        
        explanation = {
            'rule_id': rule_id,
            'conditions': rule['IF'],
            'conclusion': rule['THEN']['diagnosis'],
            'cf': rule['CF'],
            'explanation': rule['explanation'],
            'used_in_reasoning': path_entry is not None
        }
        
        if path_entry:
            explanation['step'] = path_entry['step']
            explanation['reasoning_cf'] = path_entry['cf']
        
        return explanation
    
    def get_next_question(self, current_facts: List[str]) -> Dict[str, Any]:
        """
        Menentukan pertanyaan selanjutnya yang harus ditanyakan
        Berguna untuk interactive consultation
        
        Args:
            current_facts: Fakta yang sudah diketahui
            
        Returns:
            Dictionary berisi pertanyaan yang disarankan
        """
        # Hitung frekuensi kondisi dalam rules yang belum terpenuhi
        condition_frequency = {}
        
        for rule_id, rule in self.kb.get_all_rules().items():
            # Skip jika rule sudah digunakan
            if rule_id in self.used_rules:
                continue
            
            # Cek kondisi yang belum terpenuhi
            missing_conditions = [c for c in rule['IF'] if c not in current_facts]
            
            for condition in missing_conditions:
                if condition not in condition_frequency:
                    condition_frequency[condition] = {
                        'count': 0,
                        'rules': [],
                        'potential_diagnoses': []
                    }
                condition_frequency[condition]['count'] += 1
                condition_frequency[condition]['rules'].append(rule_id)
                condition_frequency[condition]['potential_diagnoses'].append(
                    rule['THEN']['diagnosis']
                )
        
        if not condition_frequency:
            return {
                'has_question': False,
                'message': 'Tidak ada pertanyaan tambahan yang diperlukan'
            }
        
        # Pilih kondisi dengan frekuensi tertinggi
        best_condition = max(condition_frequency.items(), 
                           key=lambda x: x[1]['count'])
        
        return {
            'has_question': True,
            'recommended_question': best_condition[0],
            'frequency': best_condition[1]['count'],
            'affected_rules': best_condition[1]['rules'],
            'potential_diagnoses': list(set(best_condition[1]['potential_diagnoses'])),
            'reason': f'Pertanyaan ini dapat mengaktifkan {best_condition[1]["count"]} rules'
        }
    
    def confidence_analysis(self, conclusions: List[Dict]) -> Dict[str, Any]:
        """
        Analisis tingkat kepercayaan hasil diagnosis
        
        Args:
            conclusions: List hasil diagnosis dari forward chaining
            
        Returns:
            Dictionary analisis confidence
        """
        if not conclusions:
            return {'error': 'Tidak ada conclusions untuk dianalisis'}
        
        cfs = [c['cf'] for c in conclusions]
        
        analysis = {
            'total_conclusions': len(conclusions),
            'highest_cf': max(cfs),
            'lowest_cf': min(cfs),
            'average_cf': sum(cfs) / len(cfs),
            'median_cf': sorted(cfs)[len(cfs) // 2],
            'confidence_distribution': {
                'sangat_yakin': len([cf for cf in cfs if cf >= 0.8]),
                'yakin': len([cf for cf in cfs if 0.6 <= cf < 0.8]),
                'cukup_yakin': len([cf for cf in cfs if 0.4 <= cf < 0.6]),
                'kurang_yakin': len([cf for cf in cfs if cf < 0.4])
            },
            'top_diagnosis': conclusions[0]['diagnosis'] if conclusions else None,
            'top_cf': conclusions[0]['cf'] if conclusions else None
        }
        
        # Rekomendasi berdasarkan confidence
        if analysis['highest_cf'] >= 0.8:
            analysis['recommendation'] = 'Diagnosis sangat kuat, dapat diaplikasikan'
        elif analysis['highest_cf'] >= 0.6:
            analysis['recommendation'] = 'Diagnosis cukup kuat, disarankan konfirmasi tambahan'
        elif analysis['highest_cf'] >= 0.4:
            analysis['recommendation'] = 'Diagnosis lemah, butuh informasi tambahan'
        else:
            analysis['recommendation'] = 'Diagnosis sangat lemah, perlu pengamatan lebih lanjut'
        
        return analysis
    
    def trace_reasoning(self, diagnosis: str) -> List[Dict[str, Any]]:
        """
        Trace alur reasoning untuk suatu diagnosis tertentu
        
        Args:
            diagnosis: Diagnosis yang ingin di-trace
            
        Returns:
            List langkah-langkah reasoning yang menghasilkan diagnosis
        """
        trace = []
        
        for step in self.reasoning_path:
            if diagnosis.lower() in step['conclusion'].lower():
                trace.append({
                    'step': step['step'],
                    'rule': step['rule'],
                    'conditions': step['conditions'],
                    'conclusion': step['conclusion'],
                    'cf': step['cf'],
                    'reasoning': step['reasoning']
                })
        
        return trace
    
    def get_conflicting_rules(self) -> List[Dict[str, Any]]:
        """
        Identifikasi rules yang mungkin menghasilkan kesimpulan bertentangan
        
        Returns:
            List rules yang berpotensi konflik
        """
        conflicts = []
        
        rules_list = list(self.kb.get_all_rules().items())
        
        for i, (rule_id1, rule1) in enumerate(rules_list):
            for rule_id2, rule2 in rules_list[i+1:]:
                # Check apakah kondisi sama tapi kesimpulan berbeda
                if set(rule1['IF']) == set(rule2['IF']):
                    if rule1['THEN']['diagnosis'] != rule2['THEN']['diagnosis']:
                        conflicts.append({
                            'rule1': rule_id1,
                            'rule2': rule_id2,
                            'conditions': rule1['IF'],
                            'diagnosis1': rule1['THEN']['diagnosis'],
                            'diagnosis2': rule2['THEN']['diagnosis'],
                            'type': 'SAME_CONDITIONS_DIFFERENT_CONCLUSIONS'
                        })
        
        return conflicts
    
    def get_inference_statistics(self) -> Dict[str, Any]:
        """
        Dapatkan statistik proses inferensi
        
        Returns:
            Dictionary statistik inferensi
        """
        return {
            'total_rules_in_kb': len(self.kb.get_all_rules()),
            'rules_used': len(self.used_rules),
            'rules_unused': len(self.kb.get_all_rules()) - len(self.used_rules),
            'reasoning_steps': len(self.reasoning_path),
            'working_memory_size': len(self.working_memory),
            'usage_percentage': (len(self.used_rules) / len(self.kb.get_all_rules()) * 100) 
                              if len(self.kb.get_all_rules()) > 0 else 0
        }


# Example usage dan testing
if __name__ == "__main__":
    from modules.knowledge_base import KnowledgeBase
    
    # Initialize
    kb = KnowledgeBase('rules.json')
    engine = InferenceEngine(kb)
    
    print("="*60)
    print("TESTING INFERENCE ENGINE")
    print("="*60)
    
    # Test Case 1: Forward Chaining
    print("\n### TEST CASE 1: Forward Chaining ###")
    facts = ['fase_vegetatif', 'daun_kuning_merata', 'pertumbuhan_lambat']
    user_cfs = {
        'fase_vegetatif': 1.0,
        'daun_kuning_merata': 0.9,
        'pertumbuhan_lambat': 0.8
    }
    
    result = engine.forward_chaining(facts, user_cfs)
    print(f"\nTop Diagnosis: {result['conclusions'][0]['diagnosis']}")
    print(f"CF: {result['conclusions'][0]['cf']:.3f}")
    print(f"Interpretation: {result['conclusions'][0]['cf_interpretation']}")
    
    # Test Case 2: Backward Chaining
    print("\n### TEST CASE 2: Backward Chaining ###")
    goal = "Kekurangan Nitrogen (N)"
    backward_result = engine.backward_chaining(goal, facts)
    print(f"Goal: {backward_result['goal']}")
    print(f"Proven: {backward_result['proven']}")
    print(f"Message: {backward_result['message']}")
    
    # Test Case 3: Next Question
    print("\n### TEST CASE 3: Next Question Recommendation ###")
    partial_facts = ['fase_generatif', 'bunga_rontok']
    next_q = engine.get_next_question(partial_facts)
    if next_q['has_question']:
        print(f"Recommended Question: {next_q['recommended_question']}")
        print(f"Reason: {next_q['reason']}")
    
    # Test Case 4: Confidence Analysis
    print("\n### TEST CASE 4: Confidence Analysis ###")
    analysis = engine.confidence_analysis(result['conclusions'])
    print(f"Highest CF: {analysis['highest_cf']:.3f}")
    print(f"Average CF: {analysis['average_cf']:.3f}")
    print(f"Recommendation: {analysis['recommendation']}")
    
    # Test Case 5: Statistics
    print("\n### TEST CASE 5: Inference Statistics ###")
    stats = engine.get_inference_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")