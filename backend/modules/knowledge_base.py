"""
Knowledge Base Module
Modul untuk mengelola basis pengetahuan sistem pakar
Menggunakan representasi IF-THEN Rules
"""

import json
from typing import Dict, List, Any

class KnowledgeBase:
    """
    Class untuk mengelola Knowledge Base sistem pakar
    Menyimpan rules, facts, dan nutrient information
    """
    
    def __init__(self, rules_file: str = 'rules.json'):
        """
        Inisialisasi Knowledge Base
        
        Args:
            rules_file: Path ke file JSON yang berisi rules
        """
        self.rules_file = rules_file
        self.rules = {}
        self.nutrients = {}
        self.growth_phases = {}
        self.metadata = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        """Load knowledge dari file JSON"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rules = data.get('rules', {})
                self.nutrients = data.get('nutrient_database', {})
                self.growth_phases = data.get('growth_phases', {})
                self.metadata = data.get('metadata', {})
            print(f"✓ Knowledge base loaded: {len(self.rules)} rules")
        except FileNotFoundError:
            print(f"⚠ File {self.rules_file} tidak ditemukan. Membuat knowledge base baru.")
            self.initialize_default_knowledge()
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON: {e}")
            raise
    
    def save_knowledge(self):
        """Simpan knowledge ke file JSON"""
        data = {
            'metadata': self.metadata,
            'rules': self.rules,
            'nutrient_database': self.nutrients,
            'growth_phases': self.growth_phases
        }
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Knowledge base saved to {self.rules_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving knowledge base: {e}")
            return False
    
    def initialize_default_knowledge(self):
        """Inisialisasi knowledge base dengan data default"""
        self.metadata = {
            'version': '1.0',
            'domain': 'Pemupukan Tanaman Cabai',
            'expert_source': 'Balai Penelitian Tanaman Sayuran'
        }
        
        self.rules = {
            'R1': {
                'IF': ['fase_vegetatif', 'daun_kuning_merata', 'pertumbuhan_lambat'],
                'THEN': {
                    'diagnosis': 'Kekurangan Nitrogen (N)',
                    'pupuk': 'Urea atau ZA',
                    'dosis': '150-200 kg/ha',
                    'metode': 'Aplikasi bertahap setiap 2 minggu'
                },
                'CF': 0.9,
                'explanation': 'Nitrogen penting untuk pertumbuhan vegetatif'
            }
        }
        
        self.save_knowledge()
    
    def add_rule(self, rule_id: str, conditions: List[str], 
                 conclusion: Dict[str, str], cf: float, explanation: str):
        """
        Tambah rule baru ke knowledge base
        
        Args:
            rule_id: ID unik untuk rule
            conditions: List kondisi IF
            conclusion: Dictionary berisi diagnosis dan rekomendasi
            cf: Certainty Factor (0-1)
            explanation: Penjelasan rule
        """
        if rule_id in self.rules:
            print(f"⚠ Rule {rule_id} sudah ada. Gunakan update_rule() untuk mengubah.")
            return False
        
        self.rules[rule_id] = {
            'IF': conditions,
            'THEN': conclusion,
            'CF': cf,
            'explanation': explanation
        }
        
        self.save_knowledge()
        print(f"✓ Rule {rule_id} berhasil ditambahkan")
        return True
    
    def update_rule(self, rule_id: str, **kwargs):
        """
        Update rule yang sudah ada
        
        Args:
            rule_id: ID rule yang akan diupdate
            **kwargs: Field yang akan diupdate (IF, THEN, CF, explanation)
        """
        if rule_id not in self.rules:
            print(f"✗ Rule {rule_id} tidak ditemukan")
            return False
        
        for key, value in kwargs.items():
            if key in ['IF', 'THEN', 'CF', 'explanation']:
                self.rules[rule_id][key] = value
        
        self.save_knowledge()
        print(f"✓ Rule {rule_id} berhasil diupdate")
        return True
    
    def delete_rule(self, rule_id: str):
        """
        Hapus rule dari knowledge base
        
        Args:
            rule_id: ID rule yang akan dihapus
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.save_knowledge()
            print(f"✓ Rule {rule_id} berhasil dihapus")
            return True
        else:
            print(f"✗ Rule {rule_id} tidak ditemukan")
            return False
    
    def get_rule(self, rule_id: str) -> Dict[str, Any]:
        """Dapatkan detail rule berdasarkan ID"""
        return self.rules.get(rule_id, None)
    
    def get_all_rules(self) -> Dict[str, Any]:
        """Dapatkan semua rules"""
        return self.rules
    
    def search_rules_by_condition(self, condition: str) -> List[str]:
        """
        Cari rules yang memiliki kondisi tertentu
        
        Args:
            condition: Kondisi yang dicari
            
        Returns:
            List rule_id yang memenuhi
        """
        matching_rules = []
        for rule_id, rule in self.rules.items():
            if condition in rule['IF']:
                matching_rules.append(rule_id)
        return matching_rules
    
    def search_rules_by_diagnosis(self, diagnosis: str) -> List[str]:
        """
        Cari rules berdasarkan diagnosis
        
        Args:
            diagnosis: Diagnosis yang dicari
            
        Returns:
            List rule_id yang memenuhi
        """
        matching_rules = []
        for rule_id, rule in self.rules.items():
            if diagnosis.lower() in rule['THEN']['diagnosis'].lower():
                matching_rules.append(rule_id)
        return matching_rules
    
    def get_nutrient_info(self, symbol: str) -> Dict[str, Any]:
        """Dapatkan informasi nutrisi berdasarkan simbol"""
        return self.nutrients.get(symbol, None)
    
    def get_all_nutrients(self) -> Dict[str, Any]:
        """Dapatkan semua informasi nutrisi"""
        return self.nutrients
    
    def get_phase_info(self, phase: str) -> Dict[str, Any]:
        """Dapatkan informasi fase pertumbuhan"""
        return self.growth_phases.get(phase, None)
    
    def validate_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Validasi struktur rule
        
        Returns:
            Dict dengan status validasi dan pesan error jika ada
        """
        if rule_id not in self.rules:
            return {'valid': False, 'error': 'Rule tidak ditemukan'}
        
        rule = self.rules[rule_id]
        
        # Check required fields
        required_fields = ['IF', 'THEN', 'CF', 'explanation']
        for field in required_fields:
            if field not in rule:
                return {'valid': False, 'error': f'Field {field} tidak ada'}
        
        # Check IF conditions
        if not isinstance(rule['IF'], list) or len(rule['IF']) == 0:
            return {'valid': False, 'error': 'IF harus berupa list dengan minimal 1 kondisi'}
        
        # Check THEN structure
        if not isinstance(rule['THEN'], dict):
            return {'valid': False, 'error': 'THEN harus berupa dictionary'}
        
        required_then_fields = ['diagnosis', 'pupuk', 'dosis', 'metode']
        for field in required_then_fields:
            if field not in rule['THEN']:
                return {'valid': False, 'error': f'THEN harus memiliki field {field}'}
        
        # Check CF range
        if not (0 <= rule['CF'] <= 1):
            return {'valid': False, 'error': 'CF harus antara 0 dan 1'}
        
        return {'valid': True, 'message': 'Rule valid'}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Dapatkan statistik knowledge base"""
        total_rules = len(self.rules)
        
        # Hitung rules per fase
        vegetatif_rules = sum(1 for r in self.rules.values() 
                             if 'fase_vegetatif' in r['IF'])
        generatif_rules = sum(1 for r in self.rules.values() 
                             if 'fase_generatif' in r['IF'])
        
        # Hitung diagnosis unik
        diagnoses = set(r['THEN']['diagnosis'] for r in self.rules.values())
        
        # Average CF
        avg_cf = sum(r['CF'] for r in self.rules.values()) / total_rules if total_rules > 0 else 0
        
        return {
            'total_rules': total_rules,
            'vegetatif_rules': vegetatif_rules,
            'generatif_rules': generatif_rules,
            'unique_diagnoses': len(diagnoses),
            'average_cf': round(avg_cf, 3),
            'total_nutrients': len(self.nutrients)
        }
    
    def export_to_csv(self, output_file: str = 'rules_export.csv'):
        """Export rules ke format CSV"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Rule_ID', 'Conditions', 'Diagnosis', 'Pupuk', 
                         'Dosis', 'Metode', 'CF', 'Explanation']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for rule_id, rule in self.rules.items():
                writer.writerow({
                    'Rule_ID': rule_id,
                    'Conditions': ' AND '.join(rule['IF']),
                    'Diagnosis': rule['THEN']['diagnosis'],
                    'Pupuk': rule['THEN']['pupuk'],
                    'Dosis': rule['THEN']['dosis'],
                    'Metode': rule['THEN']['metode'],
                    'CF': rule['CF'],
                    'Explanation': rule['explanation']
                })
        
        print(f"✓ Rules exported to {output_file}")


# Example usage
if __name__ == "__main__":
    kb = KnowledgeBase()
    
    print("\n=== Knowledge Base Statistics ===")
    stats = kb.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Testing Rule Retrieval ===")
    rule = kb.get_rule('R1')
    if rule:
        print(f"Rule R1: {rule['THEN']['diagnosis']}")
        print(f"CF: {rule['CF']}")
    
    print("\n=== Testing Search ===")
    results = kb.search_rules_by_condition('daun_kuning_merata')
    print(f"Rules with 'daun_kuning_merata': {results}")