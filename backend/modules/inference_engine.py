"""
Inference Engine Module
Implementasi Forward Chaining dan Backward Chaining
untuk reasoning pada sistem pakar
"""

from typing import Dict, List, Any
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
            knowledge_base: Instance dari AdvancedKnowledgeBase
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
        """
        self.reset_memory()

        # Pastikan working_memory dalam format dict
        if isinstance(facts, dict):
            self.working_memory = dict(facts)
        else:
            self.working_memory = {fact: 1.0 for fact in facts}

        # --- Normalisasi fase agar cocok dengan rule.json ---
        if "fase_vegetatif" in self.working_memory:
            self.working_memory["fase_vegetatif_lanjut"] = 1.0
        if "fase_generatif" in self.working_memory:
            self.working_memory["fase_generatif_lanjut"] = 1.0

        print("[DEBUG] Working memory setelah normalisasi:", list(self.working_memory.keys()))

        conclusions = []
        iteration = 0
        max_iterations = 50

        while iteration < max_iterations:
            iteration += 1
            fired_rule = False

            for rule_id, rule in self.kb.get_active_rules().items():
                if rule_id in self.used_rules:
                    continue

                # Cek apakah semua kondisi rule terpenuhi
                conditions_met = all(cond in self.working_memory.keys() for cond in rule["IF"])

                if not conditions_met:
                    missing = [cond for cond in rule["IF"] if cond not in self.working_memory.keys()]
                    print(f"[DEBUG] ❌ Rule {rule_id} tidak terpenuhi. Kondisi yang belum ada: {missing}")
                    continue

                # Jika terpenuhi
                fired_rule = True
                matched_cfs = [user_cfs.get(cond, 0.8) for cond in rule["IF"]]
                final_cf = self.cf_calculator.calculate_rule_cf(rule["CF"], matched_cfs)

                conclusion = {
                    "rule_id": rule_id,
                    "diagnosis": rule["THEN"]["diagnosis"],
                    "recommendation": rule["THEN"],
                    "cf": final_cf,
                    "cf_interpretation": self.cf_calculator.interpret_cf(final_cf),
                    "explanation": rule.get("explanation", ""),
                    "conditions": rule["IF"],
                }
                conclusions.append(conclusion)

                # Tambahkan diagnosis ke working memory
                self.working_memory[rule["THEN"]["diagnosis"]] = final_cf
                self.used_rules.append(rule_id)

                self.reasoning_path.append({
                    "step": len(self.reasoning_path) + 1,
                    "rule": rule_id,
                    "conditions": rule["IF"],
                    "conclusion": rule["THEN"]["diagnosis"],
                    "cf": final_cf,
                    "reasoning": f"IF {' AND '.join(rule['IF'])} THEN {rule['THEN']['diagnosis']}"
                })

            if not fired_rule:
                break

        conclusions.sort(key=lambda x: x["cf"], reverse=True)

        return {
            "conclusions": conclusions[:5],
            "all_conclusions": conclusions,
            "used_rules": self.used_rules,
            "reasoning_path": self.reasoning_path,
            "working_memory": self.working_memory,
            "total_iterations": iteration,
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
        
        proven = any(r['can_prove'] for r in results)
        
        return {
            'goal': goal,
            'proven': proven,
            'relevant_rules': results,
            'message': 'Goal terbukti' if proven else 'Goal tidak dapat dibuktikan dengan fakta yang ada'
        }
