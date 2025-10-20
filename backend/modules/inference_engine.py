# Tugas Riyan: Mesin Inferensi (Forward Chaining)
from collections import defaultdict
from .certainty_factor import calculate_rule_cf, combine_cf
from .knowledge_base import KnowledgeBase

class InferenceEngine:
    """
    Mesin Inferensi untuk menjalankan proses penalaran berdasarkan CF.
    """
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.working_memory = {} # Fakta yang dikonfirmasi CF 1.0 (input user)
        self.hypothesis_cf = defaultdict(float) # CF untuk setiap kesimpulan/hipotesis
        self.hypothesis_paths = defaultdict(list) # Rules yang digunakan untuk setiap hipotesis

    def _reset_session(self):
        """Reset state untuk sesi konsultasi baru."""
        self.working_memory = {}
        self.hypothesis_cf = defaultdict(float)
        self.hypothesis_paths = defaultdict(list)

    def forward_chaining(self, symptoms_input: list, fase: str):
        """
        Menjalankan inferensi maju (data-driven) dengan Certainty Factor.
        """
        self._reset_session()
        
        # 1. Inisialisasi Working Memory: Gejala yang dipilih user (CF = 1.0)
        
        # Tambahkan fase sebagai fakta
        self.working_memory[fase] = 1.0
        
        # Tambahkan gejala visual sebagai fakta
        for symptom in symptoms_input:
            self.working_memory[symptom] = 1.0 # CF dari user
        
        rules_used_all = set()

        # 2. Iterasi melalui rules
        for rule_id, rule in self.kb.get_all_rules().items():
            conditions = rule.get('IF', [])
            conclusion = rule.get('THEN')
            rule_cf_pakar = rule.get('CF', 0.0)

            # Cek apakah SEMUA kondisi IF ada di Working Memory
            is_matched = all(cond in self.working_memory for cond in conditions)
            
            if is_matched:
                rules_used_all.add(rule_id)
                
                # CF Evidence (CF[E]): Ambil CF paling rendah dari semua kondisi yang matched (Conservative conjunction)
                # Karena user input CF=1.0, maka min CF evidence adalah 1.0 jika semua ada.
                cf_evidence = min(self.working_memory[cond] for cond in conditions)
                
                # Hitung CF rule (CF[H, E]) = CF[E] * CF[H, e]
                cf_result = calculate_rule_cf(cf_evidence, rule_cf_pakar)
                
                # Gabungkan CF jika hipotesis sudah ada (Menggunakan combine_cf dari Abdul)
                current_cf = self.hypothesis_cf[conclusion]
                new_cf = combine_cf(current_cf, cf_result)
                
                self.hypothesis_cf[conclusion] = new_cf
                self.hypothesis_paths[conclusion].append(rule_id)

        # 3. Ambil hasil terbaik (diagnosis dengan CF tertinggi)
        if not self.hypothesis_cf:
            return {
                "diagnosis": "Tidak_Ditemukan_Diagnosis_Signifikan", 
                "certainty_factor": 0.0, 
                "recommendation": "Tidak ditemukan kecocokan diagnosis yang signifikan berdasarkan gejala. Harap periksa gejala atau tambahkan rule baru.",
                "reasoning_path": list(rules_used_all),
                "symptoms_input": symptoms_input
            }
        
        best_conclusion = max(self.hypothesis_cf, key=self.hypothesis_cf.get)
        final_cf = self.hypothesis_cf[best_conclusion]

        # 4. Tentukan Rekomendasi
        reco = self._generate_recommendation(best_conclusion, fase)
        
        return {
            "diagnosis": best_conclusion,
            "certainty_factor": round(final_cf, 3),
            "recommendation": reco,
            "reasoning_path": self.hypothesis_paths[best_conclusion],
            "symptoms_input": [fase] + symptoms_input
        }

    def _generate_recommendation(self, conclusion: str, fase: str) -> str:
        """Menghasilkan rekomendasi pemupukan yang lebih detail."""
        element = conclusion.split('_')[-1] # Ambil unsur hara (N, K, Ca, dll)
        
        recommendations = {
            "N_Nitrogen": f"Diagnosis: Kekurangan Nitrogen (N). Rekomendasi: Aplikasikan pupuk yang kaya Nitrogen seperti Urea, ZA, atau Amonium Sulfat. Perhatikan dosis pada fase {fase} untuk menghindari pertumbuhan vegetatif berlebihan.",
            "P_Fosfor": f"Diagnosis: Kekurangan Fosfor (P). Rekomendasi: Gunakan pupuk TSP atau SP-36. P sangat penting untuk perkembangan akar di fase vegetatif dan pembungaan di fase generatif.",
            "K_Kalium": f"Diagnosis: Kekurangan Kalium (K). Rekomendasi: Aplikasikan pupuk Kalium seperti KNO3 atau KCl. Kalium penting untuk kualitas buah dan ketahanan terhadap penyakit.",
            "Ca_Kalsium": f"Diagnosis: Kekurangan Kalsium (Ca). Rekomendasi: Lakukan pengapuran tanah atau berikan pupuk Kalsium Nitrat (KNO3) terutama saat fase generatif untuk mencegah busuk ujung buah (Blossom End Rot).",
            "Mg_Magnesium": f"Diagnosis: Kekurangan Magnesium (Mg). Rekomendasi: Semprotkan atau aplikasikan Dolomit atau Kieserite (MgSO4). Magnesium adalah inti dari klorofil, penting untuk fotosintesis.",
            "B_Boron": f"Diagnosis: Kekurangan Boron (B). Rekomendasi: Aplikasikan pupuk Borax atau Solubor. Boron vital untuk pembentukan bunga dan buah, serta perkembangan titik tumbuh.",
        }
        
        return recommendations.get(conclusion, f"Rekomendasi umum untuk {conclusion}: Lakukan pemupukan seimbang sesuai standar budidaya cabai.")
