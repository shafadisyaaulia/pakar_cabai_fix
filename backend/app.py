from datetime import datetime
import json
import logging
from flask import send_file
import uuid
from datetime import datetime
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
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        fase = data.get('fase', '')
        user_cfs = data.get('user_cfs', {})

        # Proses diagnosis
        result = app.engine.forward_chaining(symptoms, user_cfs={})
        
        # Generate consultation ID
        consultation_id = str(uuid.uuid4())[:8]
        result['consultation_id'] = consultation_id
        result['symptoms'] = symptoms
        result['fase'] = fase
        
        # ✅ TAMBAH: Generate explanation untuk setiap conclusion
        for conclusion in result.get('conclusions', []):
            try:
                # HOW explanation
                how_explanation = app.explainer.explain_how(
                    conclusion.get('diagnosis', ''),
                    result.get('reasoning_path', [])
                )
                conclusion['how_explanation'] = how_explanation
                
                # Rule details
                rule_id = conclusion.get('rule_id')
                if rule_id:
                    rule_explanation = app.explainer.explain_rule(rule_id)
                    conclusion['rule_details'] = rule_explanation
                    
            except Exception as e:
                logger.warning(f"Failed to generate explanation for {conclusion.get('diagnosis')}: {e}")
                conclusion['how_explanation'] = {
                    'answer': 'Explanation not available',
                    'steps': [],
                    'rules_used': []
                }
        
        # ✅ TAMBAH: Comparison jika ada multiple conclusions
        if len(result.get('conclusions', [])) > 1:
            try:
                comparison = app.explainer.explain_comparison(result['conclusions'])
                result['comparison'] = comparison
            except Exception as e:
                logger.warning(f"Failed to generate comparison: {e}")
        
        # ✅ TAMBAH: Full report (untuk PDF export nanti)
        try:
            full_report = app.explainer.generate_full_report(result)
            result['full_report'] = full_report
        except Exception as e:
            logger.warning(f"Failed to generate full report: {e}")
            result['full_report'] = "Report not available"
        
        # Format hasil
        formatted_result = app.format_helper.format_diagnosis_result(result)
        
        # Log consultation
        try:
            consultation_data = {
                "consultation_id": consultation_id,
                "timestamp": datetime.now().isoformat(),
                "symptoms": symptoms,
                "fase": fase,
                "conclusions": result.get("conclusions", []),
            }
            app.logger.log_consultation(consultation_data)
        except Exception as log_err:
            print(f"[WARN] Gagal log: {log_err}")
        
        return jsonify(result)
    except Exception as e:
        logging.error("Error during diagnosis", exc_info=True)
        return jsonify({"error": "Gagal melakukan diagnosis"}), 500

@app.route('/api/explain/why', methods=['POST'])
def explain_why():
    """
    Endpoint untuk WHY explanation
    Request body: 
    {
        "question": "daun_kuning_merata",
        "context": {
            "current_facts": ["fase_vegetatif", "pertumbuhan_lambat"],
            "potential_goals": ["defisiensi_nitrogen"]
        }
    }
    """
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503
    
    try:
        data = request.get_json()
        question = data.get('question')
        context = data.get('context', {})
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        explanation = app.explainer.explain_why(question, context)
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
    except Exception as e:
        logger.exception("Error in explain_why")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/explain/rule/<rule_id>', methods=['GET'])
def explain_rule_endpoint(rule_id):
    """
    Endpoint untuk detail explanation dari sebuah rule
    """
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503
    
    try:
        explanation = app.explainer.explain_rule(rule_id)
        
        if 'error' in explanation:
            return jsonify(explanation), 404
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
    except Exception as e:
        logger.exception(f"Error explaining rule {rule_id}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


from flask import send_file

# @app.route('/api/export/pdf/<consultation_id>', methods=['GET'])
# def export_pdf(consultation_id):
#     if not safe_require_modules():
#         return jsonify({"error": "Backend modules not available"}), 503
    
#     try:
#         # Load consultation by ID (dari history)
#         history_df = app.logger.load_history()
#         consultation = history_df[history_df['consultation_id'] == consultation_id].to_dict('records')
        
#         if not consultation:
#             return jsonify({"error": "Consultation not found"}), 404
        
#         consultation = consultation[0]
        
#         # Generate PDF
#         pdf_path = app.pdf.export_consultation_report(consultation)
        
#         return send_file(pdf_path, as_attachment=True, download_name=f"report_{consultation_id}.pdf")
#     except Exception as e:
#         logging.exception("Error exporting PDF")
#         return jsonify({"error": str(e)}), 500

@app.route('/api/reports/summary', methods=['GET'])
def get_summary_report():
    """Endpoint untuk get summary report"""
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503
    
    try:
        # Load history
        history_df = app.logger.load_history()
        
        # Generate report
        report = app.reporter.generate_summary_report(history_df)
        
        return jsonify(report)
    except Exception as e:
        logging.exception("Error generating summary report")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/top-diagnoses', methods=['GET'])
def get_top_diagnoses():
    """Endpoint untuk top diagnoses"""
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503
    
    try:
        top_n = request.args.get('top', default=5, type=int)
        
        history_df = app.logger.load_history()
        report = app.reporter.generate_top_diagnoses_report(history_df, top_n)
        
        return jsonify(report)
    except Exception as e:
        logging.exception("Error generating top diagnoses report")
        return jsonify({"error": str(e)}), 500



@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503
    
    try:
        data = request.get_json()
        
        # ⬇️ VALIDASI consultation_id
        consultation_id = data.get('consultation_id')
        if not consultation_id or consultation_id == "NaN":
            consultation_id = str(uuid.uuid4())[:8]

        # Prepare data for PDF
        consultation_data = {
            "consultation_id": consultation_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symptoms": data.get("symptoms", []),
            "fase": data.get("fase", ""),
            "conclusions": data.get("conclusions", [])
        }
        # ✅ TAMBAH: Include explanation dan reasoning_path
        consultation_data = {
            "consultation_id": consultation_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symptoms": data.get("symptoms", []),
            "fase": data.get("fase", ""),
            "conclusions": data.get("conclusions", []),
            # ✅ TAMBAH field-field ini
            "reasoning_path": data.get("reasoning_path", []),
            "used_rules": data.get("used_rules", []),
            "full_report": data.get("full_report", ""),
            "comparison": data.get("comparison", None)
        }
        
        # Generate PDF
        pdf_path = app.pdf.export_consultation_report(consultation_data)

        # Return PDF file
        return send_file(
            pdf_path, 
            as_attachment=True, 
            download_name=f"laporan_diagnosis_{consultation_id}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        logging.exception("Error exporting PDF")
        return jsonify({"error": str(e)}), 500


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
    """Add new rule to knowledge base"""
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        logger.info(f"[ADD RULE] Received data: {data}")

        # ✅ VALIDATE REQUIRED FIELDS
        if 'IF' not in data or not isinstance(data['IF'], list):
            return jsonify({"error": "IF conditions required (must be array)"}), 400
        
        if 'THEN' not in data or not isinstance(data['THEN'], dict):
            return jsonify({"error": "THEN consequent required (must be object)"}), 400
        
        if 'diagnosis' not in data['THEN']:
            return jsonify({"error": "THEN.diagnosis required"}), 400

        # ✅ GENERATE NEW RULE ID - FIX HERE
        existing_rules = app.kb.rules  # Langsung akses property, bukan method
        
        # Get highest rule number
        rule_numbers = []
        for rule_id in existing_rules.keys():
            try:
                # Extract number from R001, R002, etc
                if rule_id.startswith('R'):
                    num = int(rule_id[1:])  # Remove 'R' prefix
                    rule_numbers.append(num)
            except (ValueError, IndexError):
                continue
        
        # Generate new ID
        next_number = max(rule_numbers) + 1 if rule_numbers else 1
        new_rule_id = f"R{next_number:03d}"  # R001, R002, etc.
        
        logger.info(f"[ADD RULE] Generated new rule ID: {new_rule_id}")

        # ✅ CREATE NEW RULE
        new_rule = {
            'IF': data['IF'],
            'THEN': data['THEN'],
            'CF': float(data.get('CF', 0.8)),
            'explanation': data.get('explanation', '')
        }

        # ✅ ADD TO KNOWLEDGE BASE (memory)
        app.kb.rules[new_rule_id] = new_rule
        
        # ✅ SAVE TO FILE
        try:
            import json
            with open('rules.json', 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            # Add new rule
            rules_data['rules'][new_rule_id] = new_rule
            
            # Save back to file
            with open('rules.json', 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[ADD RULE] ✅ Rule {new_rule_id} saved to rules.json")
        except Exception as save_err:
            logger.error(f"[ADD RULE] Failed to save to file: {save_err}")
            # Rollback memory change
            del app.kb.rules[new_rule_id]
            return jsonify({
                "error": f"Failed to save rule: {str(save_err)}"
            }), 500

        return jsonify({
            "success": True,
            "message": f"Rule {new_rule_id} added successfully",
            "rule_id": new_rule_id,
            "rule": new_rule
        }), 201

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
def get_consultation_history():
    """Endpoint untuk mendapatkan riwayat konsultasi"""
    if not safe_require_modules():
        return jsonify({"error": "Backend modules not available"}), 503
    
    try:
        # Load history dari consultation logger
        history_df = app.logger.load_history()
        
        # Convert DataFrame to list of dicts
        if history_df.empty:
            return jsonify([])
        
        # ⬇️ REPLACE NaN dengan None (JSON null) atau default value
        history_df = history_df.fillna({
            "consultation_id": "unknown",
            "timestamp": "",
            "symptoms": "[]",
            "fase": "",
            "diagnosis": "No diagnosis",
            "cf": 0.0
        })
        
        history_list = history_df.to_dict('records')
        
        # Double check: remove NaN jika masih ada
        for item in history_list:
            for key, value in item.items():
                if pd.isna(value):
                    item[key] = None
        
        formatted_history = [
            app.format_helper.format_history_item(item) 
            for item in history_list
        ]
        return jsonify(formatted_history)
    except Exception as e:
        logging.exception("Error loading consultation history")
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
