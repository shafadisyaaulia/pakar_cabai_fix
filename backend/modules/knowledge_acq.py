# Tugas Caesar: Modul CRUD Rules

from .knowledge_base import KnowledgeBase
import uuid

def generate_new_rule_id(kb):
    """Menghasilkan ID rule unik (Rxx)."""
    # Cari ID R maksimal yang ada, lalu tambah 1
    existing_ids = [int(rid[1:]) for rid in kb.get_all_rules().keys() if rid.startswith('R') and rid[1:].isdigit()]
    new_num = max(existing_ids) + 1 if existing_ids else 1
    return f"R{new_num}"

def add_or_update_rule(kb: KnowledgeBase, rule_id, if_conditions, then_conclusion, cf_value):
    """
    Menambahkan rule baru atau mengupdate rule yang sudah ada.
    """
    
    # Cleaning dan persiapan data
    if_conditions = [c.strip() for c in if_conditions if c.strip()]
    then_conclusion = then_conclusion.strip()
    
    if not if_conditions or not then_conclusion:
        return False, "Kondisi IF dan Kesimpulan THEN tidak boleh kosong."
        
    rule_data = {
        'IF': if_conditions,
        'THEN': then_conclusion,
        'CF': float(cf_value)
    }

    is_valid, message = kb.validate_rule(rule_data)
    if not is_valid:
        return False, f"Validasi Gagal: {message}"

    is_update = rule_id and rule_id in kb.get_all_rules()

    if is_update:
        kb.rules[rule_id] = rule_data
        kb.save_rules()
        return True, f"Rule {rule_id} berhasil diupdate."
    else:
        new_rule_id = generate_new_rule_id(kb)
        kb.rules[new_rule_id] = rule_data
        kb.save_rules()
        return True, f"Rule baru {new_rule_id} berhasil ditambahkan."

def delete_rule(kb: KnowledgeBase, rule_id):
    """
    Menghapus rule dari Knowledge Base.
    """
    if rule_id in kb.get_all_rules():
        del kb.rules[rule_id]
        kb.save_rules()
        return True, f"Rule {rule_id} berhasil dihapus."
    return False, f"Rule {rule_id} tidak ditemukan."
