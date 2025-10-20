from .utils import load_from_json, save_to_json
import os

class KnowledgeBase:
    """
    Manajemen Basis Pengetahuan (Rules) untuk Sistem Pakar.
    Tugas Naufal Farel.
    """
    def __init__(self, filename='rules.json'):
        self.filename = filename
        self.rules = self.load_rules()
        self.symptoms = set()
        self.conclusions = set()
        self._extract_metadata()

    def load_rules(self):
        """Memuat rules dari file JSON."""
        return load_from_json(self.filename)

    def save_rules(self):
        """Menyimpan rules ke file JSON."""
        save_to_json(self.rules, self.filename)
        self._extract_metadata()

    def get_all_rules(self):
        """Mengambil semua rules."""
        return self.rules

    def validate_rule(self, rule_data):
        """Validasi struktur rule."""
        required_keys = ['IF', 'THEN', 'CF']
        if not all(key in rule_data for key in required_keys):
            return False, "Rule harus memiliki kunci 'IF', 'THEN', dan 'CF'."
        if not isinstance(rule_data['IF'], list) or not rule_data['IF']:
            return False, "'IF' harus berupa list gejala yang tidak kosong."
        if not isinstance(rule_data['CF'], (int, float)) or not (0 <= rule_data['CF'] <= 1):
             return False, "'CF' harus berupa angka antara 0 hingga 1."
        return True, "Valid"

    def _extract_metadata(self):
        """Mengekstrak daftar gejala dan kesimpulan yang mungkin dari rules."""
        symptoms_set = set()
        conclusions_set = set()
        for rule_id, rule in self.rules.items():
            if 'IF' in rule:
                # Tambahkan semua kondisi IF, termasuk 'fase'
                symptoms_set.update(rule['IF'])
            if 'THEN' in rule:
                conclusions_set.add(rule['THEN'])
        
        # Gejala yang akan ditanyakan ke user (tidak termasuk 'fase_')
        self.symptoms = {sym for sym in symptoms_set if not sym.startswith('fase_')}
        self.conclusions = conclusions_set

    def get_all_possible_symptoms(self):
        """Mengembalikan set gejala visual yang perlu ditanyakan ke pengguna."""
        return sorted(list(self.symptoms))

    def get_all_conclusions(self):
        """Mengembalikan set kemungkinan diagnosis/kesimpulan."""
        return sorted(list(self.conclusions))
