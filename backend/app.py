from datetime import datetime
import json
import logging

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))


# Import AdvancedKnowledgeBase dan modul terkait
try:
    from modules.knowledge_base import AdvancedKnowledgeBase
    from modules.inference_engine import InferenceEngine
    from modules.certainty_factor import CertaintyFactor
    from modules.explanation import ExplanationFacility
    from modules.knowledge_acq import KnowledgeAcquisition
    from modules.consultation_logger import ConsultationLogger
    from modules.pdf_exporter import PDFExporter
    from modules.report_generator import ReportGenerator
    from modules.format_helper import FormatHelper
    MODULES_OK = True
except Exception as e:
    MODULES_OK = False
    error_msg = str(e)


# Configure app logger
logger = logging.getLogger("sistem_pakar_api")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(ch)


app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend


# Initialize app module instances
if not hasattr(app, 'kb'):
    try:
        if MODULES_OK:
            app.kb = AdvancedKnowledgeBase("rules.json")
            app.engine = InferenceEngine(app.kb)
            app.cf_calc = CertaintyFactor()
            app.explainer = ExplanationFacility(app.kb, app.engine)
            app.acq = KnowledgeAcquisition(app.kb)
            app.logger = ConsultationLogger("data/consultations.csv")
            app.pdf = PDFExporter()
            app.reporter = ReportGenerator()
            app.format_helper = FormatHelper()
        else:
            logger.error(f"Modules failed to load: {error_msg}")
            app.kb = None
            app.engine = None
            app.cf_calc = None
            app.explainer = None
            app.acq = None
            app.logger = None
            app.pdf = None
            app.reporter = None
            app.format_helper = None
    except Exception as e:
        logger.exception("Failed to initialize modules: %s", e)
        app.kb = None
        app.engine = None
        app.cf_calc = None
        app.explainer = None
        app.acq = None
        app.logger = None
        app.pdf = None
        app.reporter = None
        app.format_helper = None


def safe_require_modules() -> bool:
    return app.kb is not None


def cf_interpretation(cf: float) -> str:
    if cf >= 0.85:
        return "Sangat Meyakinkan"
    if cf >= 0.7:
        return "Meyakinkan"
    if cf >= 0.4:
        return "Cukup"
    if cf >= 0.2:
        return "Ragu-ragu"
    return "Sangat Ragu"


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        stats = app.kb.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.exception("Error getting statistics")
        return jsonify({"error": str(e)}), 500


@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        symptoms = app.kb.get_symptoms()
        return jsonify(symptoms)
    except Exception as e:
        logger.exception("Error getting symptoms")
        return jsonify({"error": str(e)}), 500


import logging

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        fase = data.get('fase', '')
        # proses diagnose...
        result = app.engine.forward_chaining(symptoms, user_cfs={})
        return jsonify(result)
    except Exception as e:
        # Gunakan logger Flask asli jika memungkinkan
        app.logger.error("Error during diagnosis", exc_info=True)
        return jsonify({"error": "Gagal melakukan diagnosis. Coba lagi."}), 500


@app.route('/api/rules', methods=['GET'])
def get_rules():
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        rules = app.kb.get_active_rules()
        rules_list = []
        for rule_id, rule in rules.items():
            meta = app.kb.rule_metadata.get(rule_id)
            rule_data = {
                "id": rule_id,
                "antecedents": rule.get("IF", []),
                "consequent": rule.get("THEN", {}).get("diagnosis", ""),
                "cf": rule.get("CF", 0.0),
                "recommendation": rule.get("THEN", {}),
                "explanation": rule.get("explanation", ""),
                "version": meta.version if meta else "N/A",
                "status": meta.status if meta else "unknown"
            }
            rules_list.append(rule_data)

        return jsonify(rules_list)
    except Exception as e:
        logger.exception("Error getting rules")
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules', methods=['POST'])
def add_rule():
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = app.acq.add_rule_from_dict(data)
        if result['success']:
            return jsonify({"message": result['message']}), 201
        else:
            return jsonify({"error": result['message']}), 400

    except Exception as e:
        logger.exception("Error adding rule")
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    try:
        updated_rule = request.get_json()
        if not updated_rule:
            return jsonify({"error": "Invalid data"}), 400

        # Update rule dalam rules.json
        with open('rules.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        if rule_id not in data["rules"]:
            return jsonify({"error": f"Rule {rule_id} not found"}), 404

        data["rules"][rule_id].update(updated_rule)

        with open('rules.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[INFO] ✅ Rule {rule_id} berhasil diperbarui")
        return jsonify({"message": "Rule updated successfully"}), 200

    except Exception as e:
        print(f"[ERROR] Gagal update rule {rule_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        # Bisa menambahkan parameter konfirmasi jika perlu
        result = app.acq.delete_rule(rule_id, confirm=True)
        if result['success']:
            return jsonify({"message": result['message']})
        else:
            return jsonify({"error": result['message']}), 404

    except Exception as e:
        logger.exception("Error deleting rule")
        return jsonify({"error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        history_df = app.logger.load_history()
        if isinstance(history_df, pd.DataFrame) and not history_df.empty:
            history = history_df.sort_values("timestamp", ascending=False).to_dict('records')
            return jsonify(history)
        else:
            return jsonify([])
    except Exception as e:
        logger.exception("Error getting history")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "modules_loaded": MODULES_OK,
        "timestamp": datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
