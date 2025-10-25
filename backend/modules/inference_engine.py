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

         # Set CF default jika user_cfs tidak ada
        if user_cfs is None:
            user_cfs = {}
    
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

        print("\n[DEBUG] ============================================")
        print("[DEBUG] CF User Input:")
        for fact, cf in self.working_memory.items():
            if not fact.startswith("fase_"):
                print(f"  - {fact}: {cf:.2f} ({cf*100:.0f}%)")
        print("[DEBUG] Working memory setelah normalisasi:", list(self.working_memory.keys()))
        print("[DEBUG] ============================================\n")

        conclusions = []
        iteration = 0
        max_iterations = 50

        while iteration < max_iterations:
            iteration += 1
            fired_rule = False

            for rule_id, rule in self.kb.get_active_rules().items():
                if rule_id in self.used_rules:
                    continue

                # Jadi minimum match (contoh: minimal 2 dari 3 IF harus ada)
                required_minimum = max(1, len(rule["IF"]) - 1)  # misal, at least 2 dari 3
                matched_conditions = [
                    cond for cond in rule["IF"] 
                    if cond in self.working_memory.keys()
                ]
                num_matched = len(matched_conditions)
                conditions_met = num_matched >= required_minimum

                if not conditions_met:
                    missing = [cond for cond in rule["IF"] if cond not in self.working_memory.keys()]
                    print(f"[DEBUG] ❌ Rule {rule_id} tidak terpenuhi.")
                    print(f"         Kondisi matched: {num_matched}/{len(rule['IF'])}")
                    print(f"         Kondisi missing: {missing}")
                    continue

                # Jika terpenuhi
                fired_rule = True
                # Ambil CF dari working_memory untuk kondisi yang matched
                matched_cfs = [
                    self.working_memory.get(cond, 0.8) 
                    for cond in matched_conditions
                ]
                # Hitung CF final dengan memperhitungkan CF rule dan CF user
                final_cf = self.cf_calculator.calculate_rule_cf(rule["CF"], matched_cfs)
                
                print(f"\n[DEBUG] ✅ Rule {rule_id} FIRED!")
                print(f"         Kondisi matched: {matched_conditions}")
                print(f"         CF User: {[f'{cf:.2f}' for cf in matched_cfs]}")
                print(f"         CF Rule: {rule['CF']:.2f}")
                print(f"         CF Final: {final_cf:.3f} ({final_cf*100:.1f}%)")
            
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
                        "conditions": matched_conditions,
                        "conditions_cf": dict(zip(matched_conditions, matched_cfs)),
                        "conclusion": rule["THEN"]["diagnosis"],
                        "cf": final_cf,
                        "reasoning": f"IF {' AND '.join(matched_conditions)} THEN {rule['THEN']['diagnosis']}"
                    })
            if not fired_rule:
                print("\n[DEBUG] Tidak ada rule yang fired lagi. Stopping.")
                break
        # Sort conclusions berdasarkan CF tertinggi
        conclusions.sort(key=lambda x: x["cf"], reverse=True)

        print(f"\n[DEBUG] Total conclusions: {len(conclusions)}")
        print(f"[DEBUG] Total iterations: {iteration}")

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
