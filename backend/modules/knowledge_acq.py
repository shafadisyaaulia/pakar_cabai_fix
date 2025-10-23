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
            knowledge_base: Instance KnowledgeBase
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
    
    def add_rule_from_dict(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tambah rule dari dictionary
        
        Args:
            rule_data: Dictionary berisi rule data
                Format: {
                    'rule_id': str,
                    'conditions': List[str],
                    'diagnosis': str,
                    'pupuk': str,
                    'dosis': str,
                    'metode': str,
                    'cf': float,
                    'explanation': str
                }
        
        Returns:
            Dictionary hasil operasi
        """
        try:
            rule_id = rule_data['rule_id']
            conditions = rule_data['conditions']
            
            conclusion = {
                'diagnosis': rule_data['diagnosis'],
                'pupuk': rule_data['pupuk'],
                'dosis': rule_data['dosis'],
                'metode': rule_data['metode']
            }
            
            cf = rule_data['cf']
            explanation = rule_data['explanation']
            
            # Validate
            if not rule_id or not conditions:
                return {
                    'success': False,
                    'message': 'Rule ID dan conditions tidak boleh kosong'
                }
            
            if not (0 <= cf <= 1):
                return {
                    'success': False,
                    'message': 'CF harus antara 0 dan 1'
                }
            
            # Add rule
            success = self.kb.add_rule(rule_id, conditions, conclusion, cf, explanation)
            
            if success:
                self._log_acquisition('ADD', rule_id, rule_data)
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
        
        except KeyError as e:
            return {
                'success': False,
                'message': f'Field yang diperlukan tidak ada: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def edit_rule(self, rule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit rule yang sudah ada
        
        Args:
            rule_id: ID rule yang akan diedit
            updates: Dictionary field yang akan diupdate
        
        Returns:
            Dictionary hasil operasi
        """
        if rule_id not in self.kb.get_all_rules():
            return {
                'success': False,
                'message': f'Rule {rule_id} tidak ditemukan'
            }
        
        # Validate updates
        valid_fields = ['IF', 'THEN', 'CF', 'explanation']
        invalid_fields = [k for k in updates.keys() if k not in valid_fields]
        
        if invalid_fields:
            return {
                'success': False,
                'message': f'Field tidak valid: {invalid_fields}'
            }
        
        # Validate CF if present
        if 'CF' in updates:
            if not (0 <= updates['CF'] <= 1):
                return {
                    'success': False,
                    'message': 'CF harus antara 0 dan 1'
                }
        
        # Update rule
        success = self.kb.update_rule(rule_id, **updates)
        
        if success:
            self._log_acquisition('EDIT', rule_id, updates)
            return {
                'success': True,
                'message': f'Rule {rule_id} berhasil diupdate',
                'rule_id': rule_id,
                'updates': updates
            }
        else:
            return {
                'success': False,
                'message': f'Gagal mengupdate rule {rule_id}'
            }
    
    def delete_rule(self, rule_id: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Hapus rule dari knowledge base
        
        Args:
            rule_id: ID rule yang akan dihapus
            confirm: Konfirmasi penghapusan
        
        Returns:
            Dictionary hasil operasi
        """
        if rule_id not in self.kb.get_all_rules():
            return {
                'success': False,
                'message': f'Rule {rule_id} tidak ditemukan'
            }
        
        if not confirm:
            return {
                'success': False,
                'message': 'Konfirmasi diperlukan untuk menghapus rule',
                'require_confirm': True
            }
        
        # Backup rule before delete
        rule_backup = self.kb.get_rule(rule_id)
        
        # Delete
        success = self.kb.delete_rule(rule_id)
        
        if success:
            self._log_acquisition('DELETE', rule_id, {'backup': rule_backup})
            return {
                'success': True,
                'message': f'Rule {rule_id} berhasil dihapus',
                'rule_id': rule_id,
                'backup': rule_backup
            }
        else:
            return {
                'success': False,
                'message': f'Gagal menghapus rule {rule_id}'
            }
    
    def validate_rule_structure(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validasi struktur rule sebelum ditambahkan
        
        Args:
            rule_data: Dictionary rule data
        
        Returns:
            Dictionary hasil validasi
        """
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['rule_id', 'conditions', 'diagnosis', 'pupuk', 'dosis', 'metode', 'cf', 'explanation']
        for field in required_fields:
            if field not in rule_data:
                errors.append(f"Field '{field}' tidak ada")
        
        if errors:
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # Validate rule_id format
        if not rule_data['rule_id'].startswith('R'):
            warnings.append("Rule ID sebaiknya dimulai dengan 'R'")
        
        # Validate conditions
        if not isinstance(rule_data['conditions'], list):
            errors.append("Conditions harus berupa list")
        elif len(rule_data['conditions']) < 1:
            errors.append("Minimal harus ada 1 kondisi")
        elif len(rule_data['conditions']) > 10:
            warnings.append("Terlalu banyak kondisi (>10), mungkin terlalu spesifik")
        
        # Validate CF
        if not isinstance(rule_data['cf'], (int, float)):
            errors.append("CF harus berupa angka")
        elif not (0 <= rule_data['cf'] <= 1):
            errors.append("CF harus antara 0 dan 1")
        elif rule_data['cf'] < 0.5:
            warnings.append("CF rendah (<0.5), pertimbangkan validitas rule")
        
        # Validate strings not empty
        for field in ['diagnosis', 'pupuk', 'dosis', 'metode', 'explanation']:
            if not rule_data.get(field, '').strip():
                errors.append(f"Field '{field}' tidak boleh kosong")
        
        # Check duplicate rule_id
        if rule_data['rule_id'] in self.kb.get_all_rules():
            errors.append(f"Rule ID '{rule_data['rule_id']}' sudah ada")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def import_rules_from_json(self, json_file: str) -> Dict[str, Any]:
        """
        Import rules dari file JSON
        
        Args:
            json_file: Path ke file JSON
        
        Returns:
            Dictionary hasil import
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'rules' not in data:
                return {
                    'success': False,
                    'message': 'File JSON tidak memiliki key "rules"'
                }
            
            imported = []
            failed = []
            
            for rule_id, rule in data['rules'].items():
                try:
                    rule_data = {
                        'rule_id': rule_id,
                        'conditions': rule['IF'],
                        'diagnosis': rule['THEN']['diagnosis'],
                        'pupuk': rule['THEN']['pupuk'],
                        'dosis': rule['THEN']['dosis'],
                        'metode': rule['THEN']['metode'],
                        'cf': rule['CF'],
                        'explanation': rule['explanation']
                    }
                    
                    result = self.add_rule_from_dict(rule_data)
                    
                    if result['success']:
                        imported.append(rule_id)
                    else:
                        failed.append({'rule_id': rule_id, 'reason': result['message']})
                
                except Exception as e:
                    failed.append({'rule_id': rule_id, 'reason': str(e)})
            
            self._log_acquisition('IMPORT', 'bulk', {
                'source': json_file,
                'imported': len(imported),
                'failed': len(failed)
            })
            
            return {
                'success': True,
                'message': f'Import selesai: {len(imported)} berhasil, {len(failed)} gagal',
                'imported': imported,
                'failed': failed,
                'total': len(imported) + len(failed)
            }
        
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'File {json_file} tidak ditemukan'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'message': f'Error parsing JSON: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def export_rules_to_json(self, output_file: str, rule_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export rules ke file JSON
        
        Args:
            output_file: Path output file
            rule_ids: Optional list rule IDs untuk export (None = export semua)
        
        Returns:
            Dictionary hasil export
        """
        try:
            all_rules = self.kb.get_all_rules()
            
            if rule_ids:
                rules_to_export = {rid: all_rules[rid] for rid in rule_ids if rid in all_rules}
            else:
                rules_to_export = all_rules
            
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'total_rules': len(rules_to_export),
                    'version': '1.0'
                },
                'rules': rules_to_export
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self._log_acquisition('EXPORT', 'bulk', {
                'destination': output_file,
                'total': len(rules_to_export)
            })
            
            return {
                'success': True,
                'message': f'{len(rules_to_export)} rules berhasil di-export',
                'output_file': output_file,
                'total_rules': len(rules_to_export)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def clone_rule(self, source_rule_id: str, new_rule_id: str) -> Dict[str, Any]:
        """
        Clone rule yang sudah ada dengan ID baru
        
        Args:
            source_rule_id: ID rule sumber
            new_rule_id: ID rule baru
        
        Returns:
            Dictionary hasil clone
        """
        source_rule = self.kb.get_rule(source_rule_id)
        
        if not source_rule:
            return {
                'success': False,
                'message': f'Rule sumber {source_rule_id} tidak ditemukan'
            }
        
        if new_rule_id in self.kb.get_all_rules():
            return {
                'success': False,
                'message': f'Rule {new_rule_id} sudah ada'
            }
        
        # Clone rule
        success = self.kb.add_rule(
            new_rule_id,
            source_rule['IF'].copy(),
            source_rule['THEN'].copy(),
            source_rule['CF'],
            source_rule['explanation']
        )
        
        if success:
            self._log_acquisition('CLONE', new_rule_id, {
                'source': source_rule_id
            })
            return {
                'success': True,
                'message': f'Rule {source_rule_id} berhasil di-clone ke {new_rule_id}',
                'source_rule_id': source_rule_id,
                'new_rule_id': new_rule_id
            }
        else:
            return {
                'success': False,
                'message': f'Gagal clone rule'
            }
    
    def batch_edit_cf(self, rule_ids: List[str], new_cf: float) -> Dict[str, Any]:
        """
        Edit CF untuk multiple rules sekaligus
        
        Args:
            rule_ids: List rule IDs
            new_cf: CF baru
        
        Returns:
            Dictionary hasil operasi
        """
        if not (0 <= new_cf <= 1):
            return {
                'success': False,
                'message': 'CF harus antara 0 dan 1'
            }
        
        updated = []
        failed = []
        
        for rule_id in rule_ids:
            result = self.edit_rule(rule_id, {'CF': new_cf})
            if result['success']:
                updated.append(rule_id)
            else:
                failed.append(rule_id)
        
        return {
            'success': True,
            'message': f'{len(updated)} rules updated, {len(failed)} failed',
            'updated': updated,
            'failed': failed,
            'new_cf': new_cf
        }
    
    def search_and_replace_condition(self, old_condition: str, new_condition: str) -> Dict[str, Any]:
        """
        Search dan replace kondisi di semua rules
        
        Args:
            old_condition: Kondisi lama
            new_condition: Kondisi baru
        
        Returns:
            Dictionary hasil operasi
        """
        affected_rules = []
        
        for rule_id, rule in self.kb.get_all_rules().items():
            if old_condition in rule['IF']:
                new_conditions = [new_condition if c == old_condition else c for c in rule['IF']]
                result = self.edit_rule(rule_id, {'IF': new_conditions})
                if result['success']:
                    affected_rules.append(rule_id)
        
        self._log_acquisition('BATCH_REPLACE', 'multiple', {
            'old': old_condition,
            'new': new_condition,
            'affected': len(affected_rules)
        })
        
        return {
            'success': True,
            'message': f'{len(affected_rules)} rules diupdate',
            'affected_rules': affected_rules,
            'old_condition': old_condition,
            'new_condition': new_condition
        }
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """
        Dapatkan statistik tentang rules
        
        Returns:
            Dictionary statistik
        """
        all_rules = self.kb.get_all_rules()
        
        # Count conditions
        condition_counts = [len(rule['IF']) for rule in all_rules.values()]
        
        # CF distribution
        cf_values = [rule['CF'] for rule in all_rules.values()]
        
        # Diagnoses
        diagnoses = [rule['THEN']['diagnosis'] for rule in all_rules.values()]
        unique_diagnoses = set(diagnoses)
        
        return {
            'total_rules': len(all_rules),
            'unique_diagnoses': len(unique_diagnoses),
            'avg_conditions_per_rule': sum(condition_counts) / len(condition_counts) if condition_counts else 0,
            'min_conditions': min(condition_counts) if condition_counts else 0,
            'max_conditions': max(condition_counts) if condition_counts else 0,
            'avg_cf': sum(cf_values) / len(cf_values) if cf_values else 0,
            'min_cf': min(cf_values) if cf_values else 0,
            'max_cf': max(cf_values) if cf_values else 0,
            'diagnoses_list': list(unique_diagnoses)
        }
    
    def _log_acquisition(self, action: str, rule_id: str, details: Dict):
        """Log acquisition activity"""
        self.acquisition_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'rule_id': rule_id,
            'details': details
        })
    
    def get_acquisition_log(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Dapatkan log aktivitas akuisisi
        
        Args:
            limit: Maksimal jumlah log (None = semua)
        
        Returns:
            List log entries
        """
        if limit:
            return self.acquisition_log[-limit:]
        return self.acquisition_log
    
    def export_acquisition_log(self, output_file: str) -> Dict[str, Any]:
        """
        Export log ke file JSON
        
        Args:
            output_file: Path output file
        
        Returns:
            Dictionary hasil export
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.acquisition_log, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'message': f'Log exported to {output_file}',
                'total_entries': len(self.acquisition_log)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }


# Example usage
if __name__ == "__main__":
    from modules.knowledge_base import KnowledgeBase
    
    # Initialize
    kb = KnowledgeBase('rules.json')
    acq = KnowledgeAcquisition(kb)
    
    print("="*70)
    print("TESTING KNOWLEDGE ACQUISITION MODULE")
    print("="*70)
    
    # Test 1: Add rule from dict
    print("\n### TEST 1: Add Rule from Dict ###")
    new_rule = {
        'rule_id': 'R13',
        'conditions': ['fase_vegetatif', 'daun_keriting', 'pertumbuhan_abnormal'],
        'diagnosis': 'Kekurangan Kalsium (Ca) fase vegetatif',
        'pupuk': 'CaCl2 atau Ca(NO3)2',
        'dosis': '100-150 kg/ha',
        'metode': 'Aplikasi foliar atau soil',
        'cf': 0.82,
        'explanation': 'Kalsium penting untuk struktur sel dan pertumbuhan normal'
    }
    
    result = acq.add_rule_from_dict(new_rule)
    print(f"Result: {result['message']}")
    
    # Test 2: Validate rule
    print("\n### TEST 2: Validate Rule Structure ###")
    validation = acq.validate_rule_structure(new_rule)
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    
    # Test 3: Get statistics
    print("\n### TEST 3: Rule Statistics ###")
    stats = acq.get_rule_statistics()
    print(f"Total Rules: {stats['total_rules']}")
    print(f"Unique Diagnoses: {stats['unique_diagnoses']}")
    print(f"Average CF: {stats['avg_cf']:.3f}")
    print(f"Avg Conditions per Rule: {stats['avg_conditions_per_rule']:.1f}")
    
    # Test 4: Acquisition log
    print("\n### TEST 4: Acquisition Log ###")
    log = acq.get_acquisition_log(limit=5)
    print(f"Recent activities: {len(log)}")
    for entry in log:
        print(f"  {entry['timestamp']}: {entry['action']} - {entry['rule_id']}")
    
    print("\n" + "="*70)
    print("ACQUISITION TESTS COMPLETED")
    print("="*70)