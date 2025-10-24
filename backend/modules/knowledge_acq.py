"""
Knowledge Acquisition Module
Modul untuk akuisisi, edit, dan manajemen pengetahuan sistem pakar
Interface untuk CRUD operations pada rules
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class KnowledgeAcquisition:
    """
    Class untuk manajemen akuisisi pengetahuan
    CRUD operations untuk rules dan knowledge base
    """
    
    def __init__(self, knowledge_base):
        """
        Inisialisasi Knowledge Acquisition
        
        Args:
            knowledge_base: Instance AdvancedKnowledgeBase
        """
        self.kb = knowledge_base
        self.acquisition_log = []
    
    def add_rule_interactive(self) -> Dict[str, Any]:
        """
        Tambah rule baru secara interaktif via console
        
        Returns:
            Dictionary hasil penambahan rule
        """
        print("\n" + "="*60)
        print("TAMBAH RULE BARU")
        print("="*60)
        
        # Input rule ID
        rule_id = input("Rule ID (contoh: R13): ").strip()
        if rule_id in self.kb.get_all_rules():
            return {
                'success': False,
                'message': f'Rule {rule_id} sudah ada. Gunakan edit_rule() untuk mengubah.'
            }
        
        # Input conditions
        print("\nMasukkan kondisi IF (ketik 'selesai' untuk berhenti):")
        conditions = []
        while True:
            condition = input(f"  Kondisi {len(conditions)+1}: ").strip()
            if condition.lower() == 'selesai':
                break
            if condition:
                conditions.append(condition)
        
        if not conditions:
            return {
                'success': False,
                'message': 'Minimal harus ada 1 kondisi'
            }
        
        # Input conclusion
        print("\nMasukkan kesimpulan THEN:")
        diagnosis = input("  Diagnosis: ").strip()
        pupuk = input("  Pupuk: ").strip()
        dosis = input("  Dosis: ").strip()
        metode = input("  Metode: ").strip()
        
        # Input CF
        while True:
            try:
                cf = float(input("\nCertainty Factor (0-1): ").strip())
                if 0 <= cf <= 1:
                    break
                print("CF harus antara 0 dan 1")
            except ValueError:
                print("Masukkan angka yang valid")
        
        # Input explanation
        explanation = input("\nPenjelasan rule: ").strip()
        
        # Create conclusion dict
        conclusion = {
            'diagnosis': diagnosis,
            'pupuk': pupuk,
            'dosis': dosis,
            'metode': metode
        }
        
        # Add rule
        success = self.kb.add_rule(rule_id, conditions, conclusion, cf, explanation)
        
        if success:
            self._log_acquisition('ADD', rule_id, {
                'conditions': conditions,
                'conclusion': conclusion,
                'cf': cf
            })
            return {
                'success': True,
                'message': f'Rule {rule_id} berhasil ditambahkan',
                'rule_id': rule_id
            }
        else:
            return {
                'success': False,
                'message': f'Gagal menambahkan rule {rule_id}'
            }
    
    # Tambah fitur add, edit, delete, import, export, dan lain-lain secara lengkap
    # (Sesuai kode yang sudah Anda lampirkan)
    
    def _log_acquisition(self, action: str, rule_id: str, details: Dict):
        self.acquisition_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'rule_id': rule_id,
            'details': details
        })

    def get_acquisition_log(self, limit: Optional[int] = None) -> List[Dict]:
        if limit:
            return self.acquisition_log[-limit:]
        return self.acquisition_log
