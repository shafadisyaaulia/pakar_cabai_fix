from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Tambahkan modul ke Python path agar bisa diimpor
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.knowledge_base import KnowledgeBase
from modules.inference_engine import InferenceEngine
from modules.explanation import generate_how_explanation
from modules.knowledge_acq import add_or_update_rule, delete_rule
from modules.utils import log_consultation

# Set working directory ke folder backend
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
# Hanya untuk development, izinkan semua domain
CORS(app) 

# Inisialisasi Modul Sistem Pakar
# Memuat KnowledgeBase dan InferenceEngine saat aplikasi dimulai
try:
    KB = KnowledgeBase('rules.json') 
    Engine = InferenceEngine(KB)
    print("Sistem Pakar: Basis Pengetahuan berhasil dimuat.")
except Exception as e:
    print(f"ERROR saat inisialisasi KnowledgeBase: {e}")
    KB = None
    Engine = None

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Endpoint utama untuk menjalankan inferensi (Tugas Riyan)."""
    if not Engine:
        return jsonify({"success": False, "message": "Sistem Pakar tidak terinisialisasi. Cek file rules.json."}), 500

    data = request.json
    symptoms = data.get('symptoms', [])
    fase = data.get('fase', 'fase_vegetatif')

    # 1. Jalankan Mesin Inferensi (Tugas Riyan & Abdul)
    result = Engine.forward_chaining(symptoms, fase)
    
    # 2. Tambahkan Penjelasan (Tugas Davina)
    result['explanation'] = generate_how_explanation(
        result['diagnosis'], 
        result['certainty_factor'], 
        result['reasoning_path'], 
        KB.get_all_rules()
    )
    
    # 3. Log Hasil (Tugas Thahira)
    log_consultation({
        "fase": fase,
        **result
    })
    
    return jsonify({"success": True, "result": result})

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Endpoint untuk mengambil daftar gejala yang mungkin dari KB."""
    if not KB:
        return jsonify({"success": False, "message": "KnowledgeBase tidak tersedia."}), 500
        
    return jsonify({
        "success": True, 
        "symptoms": KB.get_all_possible_symptoms()
    })

# --- Knowledge Acquisition Endpoints (Tugas Caesar) ---

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Endpoint untuk mengambil semua rules."""
    if not KB:
        return jsonify({"success": False, "message": "KnowledgeBase tidak tersedia."}), 500
        
    return jsonify({
        "success": True, 
        "rules": KB.get_all_rules()
    })

@app.route('/api/rules', methods=['POST'])
def handle_add_or_update_rule():
    """Endpoint untuk menambah/mengupdate rule (Tugas Caesar)."""
    if not KB:
        return jsonify({"success": False, "message": "KnowledgeBase tidak tersedia."}), 500
        
    data = request.json
    rule_id = data.get('rule_id', '')
    if_conditions = data.get('if_conditions', [])
    then_conclusion = data.get('then_conclusion', '')
    cf_value = data.get('cf_value', 0.0)

    success, message = add_or_update_rule(KB, rule_id, if_conditions, then_conclusion, cf_value)
    
    return jsonify({"success": success, "message": message})

@app.route('/api/rules/<string:rule_id>', methods=['DELETE'])
def handle_remove_rule(rule_id):
    """Endpoint untuk menghapus rule (Tugas Caesar)."""
    if not KB:
        return jsonify({"success": False, "message": "KnowledgeBase tidak tersedia."}), 500
        
    success, message = delete_rule(KB, rule_id)
    return jsonify({"success": success, "message": message})


if __name__ == '__main__':
    print("--- Sistem Pakar Cabai (Backend Flask) ---")
    print("API berjalan di: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
