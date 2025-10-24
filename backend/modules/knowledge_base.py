import json
import csv
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class RuleStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    TESTING = "testing"

class ConfidenceLevel(Enum):
    VERY_HIGH = (0.9, 1.0, "Sangat Tinggi")
    HIGH = (0.7, 0.89, "Tinggi")
    MEDIUM = (0.5, 0.69, "Sedang")
    LOW = (0.3, 0.49, "Rendah")
    VERY_LOW = (0.0, 0.29, "Sangat Rendah")
    
    @classmethod
    def get_level(cls, cf: float) -> str:
        for level in cls:
            if level.value[0] <= cf <= level.value[1]:
                return level.value[2]
        return "Unknown"

@dataclass
class RuleMetadata:
    created_at: str
    updated_at: str
    author: str
    version: str
    status: str
    usage_count: int = 0
    success_rate: float = 0.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class AdvancedKnowledgeBase:
    def __init__(self, rules_file: str = 'rules.json', backup_dir: str = 'backups'):
        self.rules_file = Path(rules_file)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.rules: Dict[str, Dict] = {}
        self.rule_metadata: Dict[str, RuleMetadata] = {}
        self.nutrients: Dict[str, Dict] = {}
        self.growth_phases: Dict[str, Dict] = {}
        self.metadata: Dict[str, Any] = {}
        self.rule_history: Dict[str, List[Dict]] = {}
        self.rule_dependencies: Dict[str, List[str]] = {}
        self.fuzzy_sets: Dict[str, Dict] = {}
        self.analytics: Dict[str, Any] = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        try:
            if not self.rules_file.exists():
                print(f"File {self.rules_file} tidak ditemukan. Membuat knowledge base baru.")
                self.initialize_advanced_knowledge()
                return
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.rules = data.get('rules', {})
            self.nutrients = data.get('nutrient_database', {})
            self.growth_phases = data.get('growth_phases', {})
            self.metadata = data.get('metadata', {})
            self.rule_history = data.get('rule_history', {})
            self.rule_dependencies = data.get('rule_dependencies', {})
            self.fuzzy_sets = data.get('fuzzy_sets', {})
            self.analytics = data.get('analytics', {})
            self.rule_metadata = {}
            for rule_id, meta_dict in data.get('rule_metadata', {}).items():
                self.rule_metadata[rule_id] = RuleMetadata(**meta_dict)
            print(f"✓ Knowledge base loaded successfully")
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON: {e}")
            raise
        except Exception as e:
            print(f"✗ Error loading knowledge base: {e}")
            raise

    def save_knowledge(self, create_backup: bool = True):
        if create_backup and self.rules_file.exists():
            self._create_backup()
        metadata_dict = {rule_id: asdict(meta) for rule_id, meta in self.rule_metadata.items()}
        data = {
            'metadata': {
                **self.metadata,
                'last_updated': datetime.now().isoformat(),
                'total_rules': len(self.rules)
            },
            'rules': self.rules,
            'rule_metadata': metadata_dict,
            'rule_history': self.rule_history,
            'rule_dependencies': self.rule_dependencies,
            'nutrient_database': self.nutrients,
            'growth_phases': self.growth_phases,
            'fuzzy_sets': self.fuzzy_sets,
            'analytics': self.analytics
        }
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Knowledge base saved to {self.rules_file}")
            return True
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
            return False

    def _create_backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"rules_backup_{timestamp}.json"
        try:
            import shutil
            shutil.copy2(self.rules_file, backup_file)
            print(f"Backup created: {backup_file}")
        except Exception as e:
            print(f"Failed to create backup: {e}")

    def initialize_advanced_knowledge(self):
        """Inisialisasi knowledge base dengan data advanced"""
        self.metadata = {
            'version': '2.0',
            'domain': 'Sistem Pakar Pemupukan Tanaman Cabai',
            'expert_source': 'Balai Penelitian Tanaman Sayuran',
            'created_at': datetime.now().isoformat(),
            'inference_method': 'Forward Chaining with Certainty Factor',
            'fuzzy_logic_enabled': True
        }
        
        # Fuzzy sets untuk kondisi tanaman
        self.fuzzy_sets = {
            'pertumbuhan': {
                'lambat': {'min': 0, 'max': 30, 'peak': 20},
                'normal': {'min': 25, 'max': 60, 'peak': 45},
                'cepat': {'min': 55, 'max': 100, 'peak': 80}
            },
            'warna_daun': {
                'sangat_kuning': {'value': 10},
                'kuning': {'value': 30},
                'hijau_muda': {'value': 60},
                'hijau_normal': {'value': 80},
                'hijau_gelap': {'value': 95}
            }
        }
        
        # Enhanced nutrient database
        self.nutrients = {
            'N': {
                'name': 'Nitrogen',
                'symbol': 'N',
                'role': 'Pertumbuhan vegetatif, pembentukan klorofil',
                'deficiency_symptoms': [
                    'Daun menguning merata (klorosis)',
                    'Pertumbuhan terhambat',
                    'Tanaman kerdil',
                    'Daun tua menguning lebih dulu'
                ],
                'excess_symptoms': [
                    'Pertumbuhan vegetatif berlebihan',
                    'Daun sangat hijau gelap',
                    'Rentan terhadap hama dan penyakit',
                    'Pembungaan tertunda'
                ],
                'sources': ['Urea', 'ZA', 'NPK'],
                'mobility': 'Mobile (mudah berpindah dalam tanaman)'
            },
            'P': {
                'name': 'Fosfor',
                'symbol': 'P',
                'role': 'Pembentukan akar, bunga, dan buah',
                'deficiency_symptoms': [
                    'Daun tua keunguan atau kemerahan',
                    'Pertumbuhan akar terhambat',
                    'Pembungaan tertunda',
                    'Ukuran buah kecil'
                ],
                'excess_symptoms': [
                    'Defisiensi unsur mikro (Zn, Fe)',
                    'Daun menguning'
                ],
                'sources': ['SP-36', 'TSP', 'NPK'],
                'mobility': 'Mobile'
            },
            'K': {
                'name': 'Kalium',
                'symbol': 'K',
                'role': 'Kualitas buah, ketahanan terhadap penyakit',
                'deficiency_symptoms': [
                    'Tepi daun terbakar (necrosis)',
                    'Daun tua menguning di tepi',
                    'Buah kecil dan tidak berkualitas',
                    'Tanaman lemah'
                ],
                'excess_symptoms': [
                    'Defisiensi Mg dan Ca',
                    'Pertumbuhan terhambat'
                ],
                'sources': ['KCl', 'KNO3', 'NPK'],
                'mobility': 'Mobile'
            }
        }
        
        # Growth phases dengan detail
        self.growth_phases = {
            'vegetatif_awal': {
                'duration': '0-21 hari setelah tanam',
                'focus': 'Pertumbuhan akar dan batang',
                'key_nutrients': ['N', 'P'],
                'ratio_npk': '1:2:1',
                'description': 'Fase pembentukan sistem perakaran yang kuat'
            },
            'vegetatif_lanjut': {
                'duration': '22-42 hari setelah tanam',
                'focus': 'Pertumbuhan daun dan cabang',
                'key_nutrients': ['N'],
                'ratio_npk': '2:1:1',
                'description': 'Fase pertumbuhan vegetatif maksimal'
            },
            'generatif_awal': {
                'duration': '43-70 hari setelah tanam',
                'focus': 'Pembungaan',
                'key_nutrients': ['P', 'K'],
                'ratio_npk': '1:2:2',
                'description': 'Fase pembentukan bunga dan pentil buah'
            },
            'generatif_lanjut': {
                'duration': '71-120+ hari setelah tanam',
                'focus': 'Pembuahan',
                'key_nutrients': ['K', 'P'],
                'ratio_npk': '1:1:3',
                'description': 'Fase pembesaran dan pematangan buah'
            }
        }
        
        # Sample rules dengan struktur enhanced
        self.add_rule(
            rule_id='R001',
            conditions=['fase_vegetatif_lanjut', 'daun_kuning_merata', 'pertumbuhan_lambat'],
            conclusion={
                'diagnosis': 'Kekurangan Nitrogen (N)',
                'severity': 'Tinggi',
                'pupuk': 'Urea atau ZA',
                'dosis': '150-200 kg/ha',
                'dosis_per_tanaman': '5-7 gram/tanaman',
                'metode': 'Kocor atau tabur, aplikasi bertahap setiap 2 minggu',
                'waktu_aplikasi': 'Pagi atau sore hari',
                'precaution': 'Hindari aplikasi saat hujan, segera siram setelah aplikasi'
            },
            cf=0.9,
            explanation='Nitrogen sangat penting untuk pertumbuhan vegetatif. Gejala klorosis merata pada daun muda menunjukkan defisiensi N yang parah.',
            author='Expert System',
            tags=['nitrogen', 'vegetatif', 'klorosis', 'urgent']
        )
        
        self.save_knowledge(create_backup=False)
    
    def add_rule(self, rule_id: str, conditions: List[str], 
                 conclusion: Dict[str, str], cf: float, 
                 explanation: str, author: str = 'System',
                 tags: List[str] = None, status: RuleStatus = RuleStatus.ACTIVE,
                 dependencies: List[str] = None):
        """
        Tambah rule baru dengan metadata lengkap
        
        Args:
            rule_id: ID unik untuk rule
            conditions: List kondisi IF
            conclusion: Dictionary berisi diagnosis dan rekomendasi lengkap
            cf: Certainty Factor (0-1)
            explanation: Penjelasan detail rule
            author: Pembuat rule
            tags: Tags untuk kategorisasi
            status: Status rule (active/inactive/deprecated/testing)
            dependencies: Rule IDs yang menjadi prerequisite
        """
        if rule_id in self.rules:
            print(f"⚠ Rule {rule_id} sudah ada. Gunakan update_rule() untuk mengubah.")
            return False
        
        # Validasi input
        validation = self._validate_rule_structure(conditions, conclusion, cf)
        if not validation['valid']:
            print(f"✗ Validation failed: {validation['error']}")
            return False
        
        # Generate rule hash untuk tracking
        rule_hash = self._generate_rule_hash(rule_id, conditions, conclusion)
        
        # Create rule
        self.rules[rule_id] = {
            'IF': conditions,
            'THEN': conclusion,
            'CF': cf,
            'explanation': explanation,
            'hash': rule_hash,
            'confidence_level': ConfidenceLevel.get_level(cf)
        }
        
        # Create metadata
        now = datetime.now().isoformat()
        self.rule_metadata[rule_id] = RuleMetadata(
            created_at=now,
            updated_at=now,
            author=author,
            version='1.0',
            status=status.value,
            tags=tags or [],
            usage_count=0,
            success_rate=0.0
        )
        
        # Save dependencies
        if dependencies:
            self.rule_dependencies[rule_id] = dependencies
        
        # Initialize history
        self.rule_history[rule_id] = [{
            'action': 'created',
            'timestamp': now,
            'author': author,
            'version': '1.0'
        }]
        
        self.save_knowledge()
        print(f"Rule {rule_id} berhasil ditambahkan")
        print(f"  CF: {cf} ({ConfidenceLevel.get_level(cf)})")
        print(f"  Tags: {', '.join(tags or ['none'])}")
        return True
    
    def update_rule(self, rule_id: str, author: str = 'System', **kwargs):
        """
        Update rule dengan version tracking
        
        Args:
            rule_id: ID rule yang akan diupdate
            author: Nama yang melakukan update
            **kwargs: Field yang akan diupdate
        """
        if rule_id not in self.rules:
            print(f"Rule {rule_id} tidak ditemukan")
            return False
        
        # Backup current state to history
        current_rule = self.rules[rule_id].copy()
        current_meta = self.rule_metadata[rule_id]
        
        self.rule_history[rule_id].append({
            'action': 'updated',
            'timestamp': datetime.now().isoformat(),
            'author': author,
            'version': current_meta.version,
            'previous_state': current_rule
        })
        
        # Update rule
        for key, value in kwargs.items():
            if key in ['IF', 'THEN', 'CF', 'explanation']:
                self.rules[rule_id][key] = value
        
        # Update CF level if CF changed
        if 'CF' in kwargs:
            self.rules[rule_id]['confidence_level'] = ConfidenceLevel.get_level(kwargs['CF'])
        
        # Update metadata
        current_meta.updated_at = datetime.now().isoformat()
        version_parts = current_meta.version.split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        current_meta.version = '.'.join(version_parts)
        
        # Regenerate hash
        self.rules[rule_id]['hash'] = self._generate_rule_hash(
            rule_id, 
            self.rules[rule_id]['IF'],
            self.rules[rule_id]['THEN']
        )
        
        self.save_knowledge()
        print(f"Rule {rule_id} berhasil diupdate ke v{current_meta.version}")
        return True
    
    def delete_rule(self, rule_id: str, soft_delete: bool = True):
        """
        Hapus rule dengan opsi soft delete
        
        Args:
            rule_id: ID rule yang akan dihapus
            soft_delete: Jika True, set status ke deprecated instead of delete
        """
        if rule_id not in self.rules:
            print(f"Rule {rule_id} tidak ditemukan")
            return False
        
        if soft_delete:
            self.rule_metadata[rule_id].status = RuleStatus.DEPRECATED.value
            self.rule_history[rule_id].append({
                'action': 'deprecated',
                'timestamp': datetime.now().isoformat(),
                'author': 'System'
            })
            print(f"Rule {rule_id} di-deprecated")
        else:
            del self.rules[rule_id]
            del self.rule_metadata[rule_id]
            if rule_id in self.rule_dependencies:
                del self.rule_dependencies[rule_id]
            print(f"Rule {rule_id} dihapus permanent")
        
        self.save_knowledge()
        return True
    
    def get_rule(self, rule_id: str, include_metadata: bool = False) -> Optional[Dict[str, Any]]:
        """Dapatkan detail rule dengan opsi metadata"""
        if rule_id not in self.rules:
            return None
        
        if include_metadata:
            return {
                'rule': self.rules[rule_id],
                'metadata': asdict(self.rule_metadata[rule_id]),
                'history': self.rule_history.get(rule_id, []),
                'dependencies': self.rule_dependencies.get(rule_id, [])
            }
        return self.rules[rule_id]
    
    def get_active_rules(self) -> Dict[str, Any]:
        """Dapatkan hanya rules yang aktif. Aman terhadap entries orphan/metadata hilang."""
        return {
        rule_id: rule
        for rule_id, rule in self.rules.items()
        if rule_id in self.rule_metadata and self.rule_metadata[rule_id].status == RuleStatus.ACTIVE.value
    }
    
    def search_rules(self, 
                    condition: str = None,
                    diagnosis: str = None,
                    tags: List[str] = None,
                    min_cf: float = None,
                    status: RuleStatus = None) -> List[Tuple[str, Dict]]:
        """
        Advanced search dengan multiple filters
        
        Args:
            condition: Cari berdasarkan kondisi
            diagnosis: Cari berdasarkan diagnosis
            tags: Cari berdasarkan tags
            min_cf: Minimum certainty factor
            status: Status rule
            
        Returns:
            List of (rule_id, rule) tuples
        """
        results = []
        
        for rule_id, rule in self.rules.items():
            meta = self.rule_metadata[rule_id]
            
            # Filter by condition
            if condition and condition not in rule['IF']:
                continue
            
            # Filter by diagnosis
            if diagnosis and diagnosis.lower() not in rule['THEN'].get('diagnosis', '').lower():
                continue
            
            # Filter by tags
            if tags and not any(tag in meta.tags for tag in tags):
                continue
            
            # Filter by CF
            if min_cf and rule['CF'] < min_cf:
                continue
            
            # Filter by status
            if status and meta.status != status.value:
                continue
            
            results.append((rule_id, rule))
        
        return results
    
    def track_rule_usage(self, rule_id: str, success: bool = True):
        """Track penggunaan dan success rate rule"""
        if rule_id not in self.rule_metadata:
            return
        
        meta = self.rule_metadata[rule_id]
        meta.usage_count += 1
        
        # Update success rate dengan moving average
        if meta.usage_count == 1:
            meta.success_rate = 1.0 if success else 0.0
        else:
            weight = 0.1  # Weight untuk data baru
            meta.success_rate = (1 - weight) * meta.success_rate + weight * (1.0 if success else 0.0)
        
        self.save_knowledge()
    
    def get_rule_analytics(self, rule_id: str = None) -> Dict[str, Any]:
        """Dapatkan analytics untuk rule tertentu atau semua rules"""
        if rule_id:
            if rule_id not in self.rule_metadata:
                return {}
            
            meta = self.rule_metadata[rule_id]
            return {
                'rule_id': rule_id,
                'usage_count': meta.usage_count,
                'success_rate': round(meta.success_rate, 3),
                'version': meta.version,
                'age_days': self._calculate_age(meta.created_at),
                'last_updated': meta.updated_at,
                'status': meta.status
            }
        else:
            # Global analytics
            total_rules = len(self.rules)
            active_rules = sum(1 for m in self.rule_metadata.values() 
                             if m.status == RuleStatus.ACTIVE.value)
            
            total_usage = sum(m.usage_count for m in self.rule_metadata.values())
            avg_success_rate = (sum(m.success_rate for m in self.rule_metadata.values()) 
                              / total_rules if total_rules > 0 else 0)
            
            # Most used rules
            most_used = sorted(
                [(rid, m.usage_count) for rid, m in self.rule_metadata.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                'total_rules': total_rules,
                'active_rules': active_rules,
                'total_usage': total_usage,
                'average_success_rate': round(avg_success_rate, 3),
                'most_used_rules': most_used,
                'last_updated': self.metadata.get('last_updated', 'N/A')
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Dapatkan statistik lengkap knowledge base"""
        total_rules = len(self.rules)
        
        # Rules per fase
        fase_counts = {}
        for rule in self.rules.values():
            for condition in rule['IF']:
                if 'fase_' in condition:
                    fase_counts[condition] = fase_counts.get(condition, 0) + 1
        
        # Diagnosis distribution
        diagnoses = {}
        for rule in self.rules.values():
            diag = rule['THEN'].get('diagnosis', 'Unknown')
            diagnoses[diag] = diagnoses.get(diag, 0) + 1
        
        # CF distribution
        cf_distribution = {
            'very_high': sum(1 for r in self.rules.values() if r['CF'] >= 0.9),
            'high': sum(1 for r in self.rules.values() if 0.7 <= r['CF'] < 0.9),
            'medium': sum(1 for r in self.rules.values() if 0.5 <= r['CF'] < 0.7),
            'low': sum(1 for r in self.rules.values() if r['CF'] < 0.5)
        }
        
        # Status distribution
        status_counts = {}
        for meta in self.rule_metadata.values():
            status_counts[meta.status] = status_counts.get(meta.status, 0) + 1
        
        return {
            'version': self.metadata.get('version', 'N/A'),
            'total_rules': total_rules,
            'rules_by_phase': fase_counts,
            'total_nutrients': len(self.nutrients),
            'total_growth_phases': len(self.growth_phases),
            'diagnoses_distribution': diagnoses,
            'cf_distribution': cf_distribution,
            'status_distribution': status_counts,
            'total_backups': len(list(self.backup_dir.glob('*.json'))),
            'last_updated': self.metadata.get('last_updated', 'N/A')
        }
    
    def export_to_csv(self, output_file: str = 'rules_export.csv'):
        """Export rules ke CSV dengan informasi lengkap"""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Rule_ID', 'Status', 'Version', 'Conditions', 'Diagnosis', 
                         'Severity', 'Pupuk', 'Dosis', 'Metode', 'CF', 'Confidence_Level',
                         'Usage_Count', 'Success_Rate', 'Author', 'Created', 'Tags']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for rule_id, rule in self.rules.items():
                meta = self.rule_metadata[rule_id]
                writer.writerow({
                    'Rule_ID': rule_id,
                    'Status': meta.status,
                    'Version': meta.version,
                    'Conditions': ' AND '.join(rule['IF']),
                    'Diagnosis': rule['THEN'].get('diagnosis', ''),
                    'Severity': rule['THEN'].get('severity', ''),
                    'Pupuk': rule['THEN'].get('pupuk', ''),
                    'Dosis': rule['THEN'].get('dosis', ''),
                    'Metode': rule['THEN'].get('metode', ''),
                    'CF': rule['CF'],
                    'Confidence_Level': rule.get('confidence_level', ''),
                    'Usage_Count': meta.usage_count,
                    'Success_Rate': round(meta.success_rate, 3),
                    'Author': meta.author,
                    'Created': meta.created_at,
                    'Tags': ', '.join(meta.tags)
                })
        
        print(f"Rules exported to {output_file}")
    
    def export_to_markdown(self, output_file: str = 'knowledge_base.md'):
        """Export knowledge base ke format Markdown untuk dokumentasi"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Knowledge Base - {self.metadata.get('domain', 'Expert System')}\n\n")
            f.write(f"**Version:** {self.metadata.get('version', 'N/A')}  \n")
            f.write(f"**Last Updated:** {self.metadata.get('last_updated', 'N/A')}  \n")
            f.write(f"**Total Rules:** {len(self.rules)}  \n\n")
            
            f.write("## Rules\n\n")
            for rule_id, rule in sorted(self.rules.items()):
                meta = self.rule_metadata[rule_id]
                f.write(f"### {rule_id} - {rule['THEN'].get('diagnosis', 'N/A')}\n\n")
                f.write(f"**Status:** {meta.status} | **Version:** {meta.version} | ")
                f.write(f"**CF:** {rule['CF']} ({rule.get('confidence_level', 'N/A')})\n\n")
                
                f.write(f"**Conditions:**\n")
                for cond in rule['IF']:
                    f.write(f"- {cond}\n")
                
                f.write(f"\n**Recommendations:**\n")
                for key, value in rule['THEN'].items():
                    f.write(f"- **{key.title()}:** {value}\n")
                
                f.write(f"\n**Explanation:** {rule['explanation']}\n\n")
                f.write(f"**Tags:** {', '.join(meta.tags) if meta.tags else 'None'}\n\n")
                f.write("---\n\n")
        
        print(f"Knowledge base exported to {output_file}")
    
    def restore_from_backup(self, backup_file: str):
        """Restore knowledge base dari backup"""
        backup_path = Path(backup_file)
        if not backup_path.exists():
            print(f"Backup file {backup_file} tidak ditemukan")
            return False
        
        try:
            # Backup current state first
            self._create_backup()
            
            # Restore from backup
            import shutil
            shutil.copy2(backup_path, self.rules_file)
            
            # Reload
            self.load_knowledge()
            print(f"Knowledge base restored from {backup_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to restore: {e}")
            return False

    def get_symptoms(self) -> dict:
        """
        Mendapatkan daftar gejala yang dikelompokkan per kategori berdasarkan kondisi IF rules.
        """
        all_symptoms = set()
        for rule in self.rules.values():
            for condition in rule['IF']:
                # Biasanya kondisi "fase_xxx" bukan gejala
                if not condition.lower().startswith("fase"):
                    all_symptoms.add(condition)

        # Grup sederhana berdasarkan kata kunci umum
        symptom_categories = {"Gejala Daun": [], "Gejala Pertumbuhan": [], "Gejala Bunga/Buah": [], "Gejala Lain": []}
        for symptom in sorted(all_symptoms):
            s = symptom.lower()
            if "daun" in s or "klorosis" in s or "nekro" in s:
                symptom_categories["Gejala Daun"].append(symptom)
            elif "pertumbuhan" in s or "kerdil" in s or "batang" in s or "ruas" in s:
                symptom_categories["Gejala Pertumbuhan"].append(symptom)
            elif "bunga" in s or "buah" in s or "bercak" in s or "pembentukan" in s or "pematangan" in s or "ujung" in s:
                symptom_categories["Gejala Bunga/Buah"].append(symptom)
            else:
                symptom_categories["Gejala Lain"].append(symptom)
        # Only non-empty categories returned
        return {k: v for k, v in symptom_categories.items() if v}
   