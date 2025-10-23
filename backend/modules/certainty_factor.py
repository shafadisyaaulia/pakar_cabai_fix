"""
Certainty Factor Module
Implementasi perhitungan Certainty Factor untuk menangani ketidakpastian
dalam sistem pakar

Formula:
CF(H,E) = MB(H,E) - MD(H,E)
CF(H,E1 ∧ E2) = CF(H,E1) + CF(H,E2) × [1 - CF(H,E1)]

Range: -1.0 (pasti salah) hingga +1.0 (pasti benar)
"""

from typing import List, Dict, Any


class CertaintyFactor:
    """
    Class untuk perhitungan dan manajemen Certainty Factor
    """
    
    def __init__(self):
        """Inisialisasi CertaintyFactor calculator"""
        self.cf_range = (-1.0, 1.0)
    
    def validate_cf(self, cf: float) -> bool:
        """
        Validasi nilai CF berada dalam range yang valid
        
        Args:
            cf: Nilai certainty factor
            
        Returns:
            True jika valid, False jika tidak
        """
        return self.cf_range[0] <= cf <= self.cf_range[1]
    
    def calculate_combined_cf(self, cf1: float, cf2: float) -> float:
        """
        Menggabungkan dua CF untuk evidence yang berbeda
        
        Formula:
        - Jika CF1 dan CF2 positif: CF(CF1, CF2) = CF1 + CF2(1 - CF1)
        - Jika CF1 dan CF2 negatif: CF(CF1, CF2) = CF1 + CF2(1 + CF1)
        - Jika berbeda tanda: CF(CF1, CF2) = (CF1 + CF2) / (1 - min(|CF1|, |CF2|))
        
        Args:
            cf1: Certainty Factor pertama
            cf2: Certainty Factor kedua
            
        Returns:
            Combined Certainty Factor
        """
        if not (self.validate_cf(cf1) and self.validate_cf(cf2)):
            raise ValueError(f"CF values must be between {self.cf_range[0]} and {self.cf_range[1]}")
        
        # Kedua CF positif
        if cf1 >= 0 and cf2 >= 0:
            return cf1 + cf2 * (1 - cf1)
        
        # Kedua CF negatif
        elif cf1 < 0 and cf2 < 0:
            return cf1 + cf2 * (1 + cf1)
        
        # CF berbeda tanda
        else:
            return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))
    
    def calculate_multiple_cf(self, cf_list: List[float]) -> float:
        """
        Menggabungkan multiple CF secara berurutan
        
        Args:
            cf_list: List CF values
            
        Returns:
            Combined CF dari semua evidence
        """
        if not cf_list:
            return 0.0
        
        if len(cf_list) == 1:
            return cf_list[0]
        
        # Gabungkan secara iteratif
        result = cf_list[0]
        for cf in cf_list[1:]:
            result = self.calculate_combined_cf(result, cf)
        
        return result
    
    def calculate_rule_cf(self, rule_cf: float, evidence_cfs: List[float]) -> float:
        """
        Menghitung CF untuk suatu rule berdasarkan CF evidence dan CF rule
        
        CF(Rule, Evidence) = CF(Rule) × CF(Evidence)
        
        Args:
            rule_cf: CF dari rule (dari knowledge base)
            evidence_cfs: List CF dari evidence/kondisi
            
        Returns:
            Final CF untuk rule
        """
        if not evidence_cfs:
            return 0.0
        
        # Gabungkan semua CF evidence
        combined_evidence_cf = self.calculate_multiple_cf(evidence_cfs)
        
        # Kalikan dengan CF rule
        final_cf = rule_cf * combined_evidence_cf
        
        return max(self.cf_range[0], min(self.cf_range[1], final_cf))
    
    def calculate_cf_with_user_certainty(self, rule_cf: float, 
                                        condition_cfs: Dict[str, float]) -> float:
        """
        Menghitung CF dengan mempertimbangkan user certainty untuk setiap kondisi
        
        Args:
            rule_cf: CF dari rule
            condition_cfs: Dictionary {condition: user_cf}
            
        Returns:
            Final CF
        """
        if not condition_cfs:
            return 0.0
        
        evidence_cfs = list(condition_cfs.values())
        return self.calculate_rule_cf(rule_cf, evidence_cfs)
    
    def interpret_cf(self, cf: float) -> str:
        """
        Interpretasi nilai CF dalam bahasa natural
        
        Args:
            cf: Nilai certainty factor
            
        Returns:
            String interpretasi
        """
        if not self.validate_cf(cf):
            return "Invalid CF"
        
        if cf >= 0.8:
            return "Sangat Yakin"
        elif cf >= 0.6:
            return "Yakin"
        elif cf >= 0.4:
            return "Cukup Yakin"
        elif cf >= 0.2:
            return "Kurang Yakin"
        elif cf > 0:
            return "Sedikit Yakin"
        elif cf == 0:
            return "Tidak Tahu"
        elif cf > -0.2:
            return "Sedikit Tidak Yakin"
        elif cf > -0.4:
            return "Kurang Tidak Yakin"
        elif cf > -0.6:
            return "Cukup Tidak Yakin"
        elif cf > -0.8:
            return "Tidak Yakin"
        else:
            return "Sangat Tidak Yakin"
    
    def get_cf_category(self, cf: float) -> str:
        """
        Kategorisasi CF untuk klasifikasi
        
        Args:
            cf: Nilai certainty factor
            
        Returns:
            Kategori (STRONG, MODERATE, WEAK, VERY_WEAK, UNKNOWN)
        """
        abs_cf = abs(cf)
        
        if abs_cf >= 0.8:
            return "STRONG"
        elif abs_cf >= 0.6:
            return "MODERATE"
        elif abs_cf >= 0.4:
            return "WEAK"
        elif abs_cf > 0:
            return "VERY_WEAK"
        else:
            return "UNKNOWN"
    
    def calculate_mb_md(self, cf: float) -> Dict[str, float]:
        """
        Menghitung Measure of Belief (MB) dan Measure of Disbelief (MD)
        dari CF
        
        CF = MB - MD
        
        Args:
            cf: Certainty Factor
            
        Returns:
            Dictionary dengan MB dan MD
        """
        if cf > 0:
            return {'MB': cf, 'MD': 0.0}
        elif cf < 0:
            return {'MB': 0.0, 'MD': abs(cf)}
        else:
            return {'MB': 0.0, 'MD': 0.0}
    
    def calculate_cf_from_mb_md(self, mb: float, md: float) -> float:
        """
        Menghitung CF dari MB dan MD
        
        Args:
            mb: Measure of Belief
            md: Measure of Disbelief
            
        Returns:
            Certainty Factor
        """
        return mb - md
    
    def normalize_cf(self, cf: float) -> float:
        """
        Normalisasi CF ke range [0, 1] untuk keperluan tertentu
        
        Args:
            cf: Certainty Factor (-1 to 1)
            
        Returns:
            Normalized CF (0 to 1)
        """
        return (cf + 1) / 2
    
    def denormalize_cf(self, normalized_cf: float) -> float:
        """
        Denormalisasi CF dari range [0, 1] ke [-1, 1]
        
        Args:
            normalized_cf: Normalized CF (0 to 1)
            
        Returns:
            CF (-1 to 1)
        """
        return normalized_cf * 2 - 1
    
    def calculate_cf_parallel_evidence(self, evidence_dict: Dict[str, float]) -> float:
        """
        Menghitung CF untuk parallel evidence (multiple evidence untuk satu hipotesis)
        
        Args:
            evidence_dict: Dictionary {evidence_id: cf_value}
            
        Returns:
            Combined CF
        """
        if not evidence_dict:
            return 0.0
        
        cf_values = list(evidence_dict.values())
        return self.calculate_multiple_cf(cf_values)
    
    def calculate_cf_sequential_rules(self, rule_chain: List[Dict[str, Any]]) -> float:
        """
        Menghitung CF untuk rantai rules yang berurutan
        
        Args:
            rule_chain: List of dictionaries dengan format:
                       [{'rule_cf': float, 'evidence_cfs': [float, ...]}]
            
        Returns:
            Final combined CF
        """
        if not rule_chain:
            return 0.0
        
        # Hitung CF untuk setiap rule
        rule_cfs = []
        for rule_info in rule_chain:
            rule_cf = self.calculate_rule_cf(
                rule_info['rule_cf'],
                rule_info.get('evidence_cfs', [1.0])
            )
            rule_cfs.append(rule_cf)
        
        # Gabungkan semua CF dari rules
        return self.calculate_multiple_cf(rule_cfs)
    
    def get_cf_confidence_interval(self, cf: float, confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Estimasi confidence interval untuk CF (simplified)
        
        Args:
            cf: Certainty Factor
            confidence_level: Level kepercayaan (default 0.95)
            
        Returns:
            Dictionary dengan lower dan upper bound
        """
        # Simplified confidence interval
        margin = (1 - confidence_level) * abs(cf)
        
        lower = max(self.cf_range[0], cf - margin)
        upper = min(self.cf_range[1], cf + margin)
        
        return {
            'cf': cf,
            'lower_bound': lower,
            'upper_bound': upper,
            'confidence_level': confidence_level
        }
    
    def compare_cfs(self, cf1: float, cf2: float, threshold: float = 0.1) -> str:
        """
        Membandingkan dua CF
        
        Args:
            cf1: CF pertama
            cf2: CF kedua
            threshold: Threshold untuk menentukan "similar"
            
        Returns:
            String hasil komparasi
        """
        diff = abs(cf1 - cf2)
        
        if diff < threshold:
            return "SIMILAR"
        elif cf1 > cf2:
            return "CF1_HIGHER"
        else:
            return "CF2_HIGHER"
    
    def aggregate_expert_cfs(self, expert_cfs: List[float], 
                           method: str = 'average') -> float:
        """
        Agregasi CF dari multiple experts
        
        Args:
            expert_cfs: List CF dari berbagai pakar
            method: Metode agregasi ('average', 'max', 'min', 'combined')
            
        Returns:
            Aggregated CF
        """
        if not expert_cfs:
            return 0.0
        
        if method == 'average':
            return sum(expert_cfs) / len(expert_cfs)
        elif method == 'max':
            return max(expert_cfs)
        elif method == 'min':
            return min(expert_cfs)
        elif method == 'combined':
            return self.calculate_multiple_cf(expert_cfs)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")


# Example usage dan testing
if __name__ == "__main__":
    cf_calc = CertaintyFactor()
    
    print("="*60)
    print("TESTING CERTAINTY FACTOR MODULE")
    print("="*60)
    
    # Test 1: Combine two CFs
    print("\n### TEST 1: Combining Two CFs ###")
    cf1 = 0.8
    cf2 = 0.6
    combined = cf_calc.calculate_combined_cf(cf1, cf2)
    print(f"CF1: {cf1}, CF2: {cf2}")
    print(f"Combined CF: {combined:.3f}")
    print(f"Interpretation: {cf_calc.interpret_cf(combined)}")
    
    # Test 2: Multiple CFs
    print("\n### TEST 2: Multiple CFs ###")
    cf_list = [0.9, 0.8, 0.7]
    result = cf_calc.calculate_multiple_cf(cf_list)
    print(f"CF List: {cf_list}")
    print(f"Combined: {result:.3f}")
    
    # Test 3: Rule CF with evidence
    print("\n### TEST 3: Rule CF Calculation ###")
    rule_cf = 0.9
    evidence_cfs = [0.8, 0.85, 0.9]
    final_cf = cf_calc.calculate_rule_cf(rule_cf, evidence_cfs)
    print(f"Rule CF: {rule_cf}")
    print(f"Evidence CFs: {evidence_cfs}")
    print(f"Final CF: {final_cf:.3f}")
    print(f"Category: {cf_calc.get_cf_category(final_cf)}")
    
    # Test 4: CF Interpretation
    print("\n### TEST 4: CF Interpretations ###")
    test_cfs = [0.95, 0.75, 0.55, 0.35, 0.15, 0.0, -0.3, -0.7, -0.95]
    for cf in test_cfs:
        print(f"CF {cf:5.2f}: {cf_calc.interpret_cf(cf)}")
    
    # Test 5: MB and MD
    print("\n### TEST 5: MB and MD Calculation ###")
    cf = 0.8
    mb_md = cf_calc.calculate_mb_md(cf)
    print(f"CF: {cf}")
    print(f"MB: {mb_md['MB']}, MD: {mb_md['MD']}")
    
    reconstructed_cf = cf_calc.calculate_cf_from_mb_md(mb_md['MB'], mb_md['MD'])
    print(f"Reconstructed CF: {reconstructed_cf}")
    
    # Test 6: Normalization
    print("\n### TEST 6: CF Normalization ###")
    cf = 0.6
    normalized = cf_calc.normalize_cf(cf)
    denormalized = cf_calc.denormalize_cf(normalized)
    print(f"Original CF: {cf}")
    print(f"Normalized (0-1): {normalized}")
    print(f"Denormalized: {denormalized}")
    
    # Test 7: Confidence Interval
    print("\n### TEST 7: Confidence Interval ###")
    cf = 0.75
    interval = cf_calc.get_cf_confidence_interval(cf, 0.95)
    print(f"CF: {interval['cf']}")
    print(f"95% CI: [{interval['lower_bound']:.3f}, {interval['upper_bound']:.3f}]")
    
    # Test 8: Expert Aggregation
    print("\n### TEST 8: Expert CF Aggregation ###")
    expert_cfs = [0.8, 0.75, 0.85, 0.9]
    methods = ['average', 'max', 'min', 'combined']
    print(f"Expert CFs: {expert_cfs}")
    for method in methods:
        result = cf_calc.aggregate_expert_cfs(expert_cfs, method)
        print(f"  {method}: {result:.3f}")
    
    # Test 9: Sequential Rules
    print("\n### TEST 9: Sequential Rules Chain ###")
    rule_chain = [
        {'rule_cf': 0.9, 'evidence_cfs': [0.8, 0.85]},
        {'rule_cf': 0.85, 'evidence_cfs': [0.9]},
        {'rule_cf': 0.8, 'evidence_cfs': [0.75, 0.8, 0.85]}
    ]
    chain_cf = cf_calc.calculate_cf_sequential_rules(rule_chain)
    print(f"Rule Chain CF: {chain_cf:.3f}")
    print(f"Interpretation: {cf_calc.interpret_cf(chain_cf)}")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)