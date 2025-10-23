"""
app.py

Streamlit main application for "Sistem Pakar Pupuk Cabai".

Prereqs:
- modules package with:
    - KnowledgeBase
    - InferenceEngine
    - CertaintyFactor
    - ExplanationFacility
    - KnowledgeAcquisition
    - ConsultationLogger
    - PDFExporter
    - ReportGenerator
    - FormatHelper

If some modules are missing this app will show helpful errors in the UI.
"""

from datetime import datetime
import json
import logging
from typing import Any, Dict, List

import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Configure app logger
logger = logging.getLogger("sistem_pakar_app")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(ch)

# --- Try import modules with graceful fallback messages ---
MODULES_OK = True
missing_modules = []
try:
    from modules import (
        KnowledgeBase,
        InferenceEngine,
        CertaintyFactor,
        ExplanationFacility,
        KnowledgeAcquisition,
        ConsultationLogger,
        PDFExporter,
        ReportGenerator,
        FormatHelper,
    )
except Exception as e:
    MODULES_OK = False
    missing_modules.append(str(e))
    # Create minimal placeholders so UI still loads but shows notice
    class _Dummy:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Required module missing: " + str(e))

    KnowledgeBase = InferenceEngine = CertaintyFactor = ExplanationFacility = KnowledgeAcquisition = ConsultationLogger = PDFExporter = ReportGenerator = FormatHelper = _Dummy

# --- Page configuration ---
st.set_page_config(
    page_title="Sistem Pakar Pupuk Cabai",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for visual nicety
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.2rem;
        color: #2E7D32;
        text-align: center;
        padding: 0.6rem;
        background: linear-gradient(90deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .diagnosis-box {
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        background-color: #F1F8E9;
        margin-bottom: 0.6rem;
    }
    .metric-card {
        background: white;
        padding: 0.8rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Initialize session state safely ---
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True
    try:
        if MODULES_OK:
            st.session_state.kb = KnowledgeBase("rules.json")
            st.session_state.engine = InferenceEngine(st.session_state.kb)
            st.session_state.cf_calc = CertaintyFactor()
            st.session_state.explainer = ExplanationFacility(st.session_state.kb, st.session_state.engine)
            st.session_state.acq = KnowledgeAcquisition(st.session_state.kb)
            st.session_state.logger = ConsultationLogger(data_path="data/consultations.csv")
            st.session_state.pdf = PDFExporter()
            st.session_state.reporter = ReportGenerator()
            st.session_state.format_helper = FormatHelper()
        else:
            # Keeps app alive; operations will show error notices later
            st.session_state.kb = None
            st.session_state.engine = None
            st.session_state.cf_calc = None
            st.session_state.explainer = None
            st.session_state.acq = None
            st.session_state.logger = None
            st.session_state.pdf = None
            st.session_state.reporter = None
            st.session_state.format_helper = None
    except Exception as e:
        logger.exception("Failed to initialize modules: %s", e)
        st.session_state.kb = None
        st.session_state.engine = None
        st.session_state.cf_calc = None
        st.session_state.explainer = None
        st.session_state.acq = None
        st.session_state.logger = None
        st.session_state.pdf = None
        st.session_state.reporter = None

    st.session_state.consultation_result = None

# --- Helper functions ---
def safe_require_modules() -> bool:
    if st.session_state.kb is None:
        st.error(
            "Beberapa modul backend belum terpasang / gagal diinisialisasi. "
            "Pastikan folder `modules/` berisi semua file yang diperlukan (knowledge_base, inference_engine, dll)."
        )
        return False
    return True


def cf_interpretation(cf: float) -> str:
    """Simple textual interpretation for CF value (0..1)."""
    if cf >= 0.85:
        return "Sangat Meyakinkan"
    if cf >= 0.7:
        return "Meyakinkan"
    if cf >= 0.4:
        return "Cukup"
    if cf >= 0.2:
        return "Ragu-ragu"
    return "Sangat Ragu"


def display_results(result: Dict[str, Any]) -> None:
    """Render consultation result in UI."""
    st.success("✅ Diagnosis Selesai!")
    st.subheader("📋 Hasil Diagnosis")

    conclusions = result.get("conclusions", [])[:5]
    for i, c in enumerate(conclusions, 1):
        with st.container():
            st.markdown(
                f"""
            <div class="diagnosis-box">
                <h4 style="margin:0">{i}. {c.get('diagnosis')}</h4>
                <div><b>Tingkat Kepercayaan:</b> {c.get('cf',0)*100:.1f}% ({c.get('cf_interpretation','')})</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                rec = c.get("recommendation", {})
                st.info(f"**Pupuk:** {rec.get('pupuk','-')}")
                st.info(f"**Dosis:** {rec.get('dosis','-')}")
            with col2:
                st.info(f"**Metode:** {rec.get('metode','-')}")
            with st.expander("📖 Penjelasan (Why)"):
                st.write(c.get("explanation", "Tidak ada penjelasan tersedia."))

    # Reasoning / How
    with st.expander("🔍 Alur Penalaran (How Explanation)"):
        for step in result.get("reasoning_path", []):
            st.markdown(
                f"**Step {step.get('step')} — Rule {step.get('rule')}**  \n"
                f"- IF: {' AND '.join(step.get('conditions', []))}  \n"
                f"- THEN: {step.get('conclusion')}  \n"
                f"- CF (rule): {step.get('rule_cf',0)*100:.1f}  \n"
                f"- CF (inferred): {step.get('cf',0)*100:.1f}"
            )

    # Export buttons
    st.markdown("---")
    st.subheader("📥 Ekspor Hasil")
    col1, col2, col3 = st.columns(3)
    consultation_id = result.get("consultation_id", f"CONS{datetime.now().strftime('%Y%m%d%H%M%S')}")
    if col1.button("📄 Export PDF"):
        if st.session_state.pdf:
            filename = f"laporan_{consultation_id}.pdf"
            try:
                st.session_state.pdf.export_consultation_report(result, filename)
                with open(filename, "rb") as f:
                    st.download_button("Download PDF", f, file_name=filename, mime="application/pdf")
            except Exception as e:
                st.error(f"Gagal membuat PDF: {e}")
        else:
            st.error("PDFExporter belum tersedia di modul.")

    if col2.button("📝 Export TXT"):
        txt = st.session_state.reporter.generate_text_report(result) if st.session_state.reporter else json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button("Download TXT", txt, file_name=f"{consultation_id}.txt", mime="text/plain")

    if col3.button("📊 Export JSON"):
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button("Download JSON", json_data, file_name=f"{consultation_id}.json", mime="application/json")


# --- Page definitions ---
def page_home() -> None:
    st.markdown('<div class="main-header">🌶️ Sistem Pakar Pemupukan Cabai</div>', unsafe_allow_html=True)
    st.markdown("**Expert System for Chili Fertilization Recommendation**")
    st.write(
        "Sistem ini menggunakan aturan berbasis IF-THEN dan mekanisme penalaran Forward Chaining "
        "dengan Certainty Factor (CF) untuk merekomendasikan jenis dan dosis pupuk."
    )

    if not safe_require_modules():
        return

    # Quick stats
    stats = st.session_state.kb.get_statistics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rules", stats.get("total_rules", 0))
    c2.metric("Unique Diagnoses", stats.get("unique_diagnoses", 0))
    c3.metric("Avg CF", f"{stats.get('average_cf', 0):.2f}")
    c4.metric("Total Nutrients", stats.get("total_nutrients", 0))

    st.markdown("---")
    st.subheader("🚀 Mulai Konsultasi")
    st.write("Pilih menu **Konsultasi** di sidebar untuk memulai.")


def page_consultation() -> None:
    st.header("🔍 Konsultasi Pemupukan")

    if not safe_require_modules():
        return

    # Fase
    st.subheader("Step 1: Pilih Fase Pertumbuhan")
    col1, col2 = st.columns(2)
    fase_vegetatif = col1.checkbox("Fase Vegetatif (0-60 HST)")
    fase_generatif = col2.checkbox("Fase Generatif (>60 HST)")

    if not (fase_vegetatif or fase_generatif):
        st.warning("Pilih minimal satu fase pertumbuhan agar rekomendasi lebih spesifik.")
        # Allow still to pick symptoms, but warn

    # Symptoms list from KB (if available)
    symptoms_catalog = st.session_state.kb.get_symptoms() if st.session_state.kb else {}
    st.subheader("Step 2: Pilih Gejala yang Terlihat")
    selected_symptoms = []
    user_cfs = {}

    # Display symptoms grouped if KB provides categories, else fallback to available list
    if isinstance(symptoms_catalog, dict) and symptoms_catalog:
        for cat, syms in symptoms_catalog.items():
            with st.expander(f"📋 {cat}"):
                for s in syms:
                    colA, colB = st.columns([4,1])
                    with colA:
                        checked = st.checkbox(s.replace("_", " ").title(), key=f"sym_{s}")
                    with colB:
                        if checked:
                            cf_val = st.slider("CF", 0.0, 1.0, 0.8, key=f"cf_{s}", label_visibility="collapsed")
                            selected_symptoms.append(s)
                            user_cfs[s] = cf_val
    else:
        # fallback sample list (small)
        fallback_symptoms = [
            "daun_kuning_merata","daun_muda_kuning","pertumbuhan_lambat","bunga_rontok","tanah_pH_rendah"
        ]
        with st.expander("📋 Gejala Umum"):
            for s in fallback_symptoms:
                colA, colB = st.columns([4,1])
                with colA:
                    checked = st.checkbox(s.replace("_", " ").title(), key=f"sym_{s}")
                with colB:
                    if checked:
                        cf_val = st.slider("CF", 0.0, 1.0, 0.8, key=f"cf_{s}", label_visibility="collapsed")
                        selected_symptoms.append(s)
                        user_cfs[s] = cf_val

    if fase_vegetatif:
        selected_symptoms.append("fase_vegetatif")
        user_cfs["fase_vegetatif"] = 1.0
    if fase_generatif:
        selected_symptoms.append("fase_generatif")
        user_cfs["fase_generatif"] = 1.0

    # Diagnosis buttons
    st.markdown("---")
    col_run, col_reset = st.columns([1,1])
    run = col_run.button("🧠 Diagnosis")
    reset = col_reset.button("🔄 Reset")

    if reset:
        st.session_state.consultation_result = None
        st.experimental_rerun()

    if run:
        if len(selected_symptoms) < 1:
            st.error("Pilih minimal 1 gejala untuk menjalankan diagnosis.")
        else:
            with st.spinner("Menjalankan inference..."):
                try:
                    result = st.session_state.engine.forward_chaining(selected_symptoms, user_cfs)
                    # add metadata
                    result["consultation_id"] = f"CONS{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    result["timestamp"] = datetime.now().isoformat()
                    result["facts"] = selected_symptoms
                    # fill interpretation
                    for c in result.get("conclusions", []):
                        c["cf_interpretation"] = cf_interpretation(c.get("cf", 0.0))
                    st.session_state.consultation_result = result
                    # log consultation
                    try:
                        st.session_state.logger.log_consultation(result)
                    except Exception as e:
                        st.warning(f"Gagal menyimpan log konsultasi: {e}")
                except Exception as e:
                    st.error(f"Gagal melakukan inference: {e}")
                    logger.exception("Inference error")

    if st.session_state.consultation_result:
        display_results(st.session_state.consultation_result)


def page_knowledge_base() -> None:
    st.header("📚 Knowledge Base")

    if not safe_require_modules():
        return

    rules = st.session_state.kb.get_all_rules()
    st.subheader("Daftar Rules")
    # Present rules in dataframe form
    rows = []
    for r in rules:
        rows.append({
            "id": r.get("id"),
            "antecedents": " AND ".join(r.get("antecedents", [])),
            "consequent": r.get("consequent"),
            "cf_rule": r.get("cf", 0.0),
            "recommendation": json.dumps(r.get("recommendation", {}), ensure_ascii=False)
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    with st.expander("📥 Export Rules (JSON)"):
        if st.button("Download rules.json"):
            st.download_button("Download rules.json", json.dumps(rules, ensure_ascii=False, indent=2), file_name="rules_export.json", mime="application/json")


def page_manage_rules() -> None:
    st.header("➕ Kelola Rules (Knowledge Acquisition)")

    if not safe_require_modules():
        return

    st.subheader("Tambah Rule Baru")
    with st.form("add_rule_form"):
        rule_id = st.text_input("Rule ID (unik)", value=f"R{int(datetime.now().timestamp())}")
        antecedents_txt = st.text_area("Antecedents (pisahkan koma)", help="Contoh: daun_kuning_merata, fase_vegetatif")
        consequent = st.text_input("Consequent / Diagnosis", value="")
        cf_rule = st.slider("CF Rule (0..1)", 0.0, 1.0, 0.8)
        pupuk = st.text_input("Rekomendasi Pupuk")
        dosis = st.text_input("Dosis (format teks)")
        metode = st.selectbox("Metode Aplikasi", ["Permukaan", "Aplikasi Daun", "Irigrasi", "Campur Tanah"])
        explanation = st.text_area("Penjelasan singkat (why)")

        submitted = st.form_submit_button("Tambah Rule")
        if submitted:
            antecedents = [a.strip() for a in antecedents_txt.split(",") if a.strip()]
            new_rule = {
                "id": rule_id,
                "antecedents": antecedents,
                "consequent": consequent,
                "cf": cf_rule,
                "recommendation": {"pupuk": pupuk, "dosis": dosis, "metode": metode},
                "explanation": explanation
            }
            try:
                st.session_state.acq.add_rule(new_rule)
                st.success(f"Rule {rule_id} berhasil ditambahkan.")
            except Exception as e:
                st.error(f"Gagal menambahkan rule: {e}")

    st.markdown("---")
    st.subheader("Edit / Hapus Rule")
    rules = st.session_state.kb.get_all_rules()
    rule_ids = [r.get("id") for r in rules]
    sel = st.selectbox("Pilih Rule untuk edit/hapus", [""] + rule_ids)
    if sel:
        rule = st.session_state.kb.get_rule(sel)
        with st.form("edit_rule_form"):
            antecedents_txt = st.text_area("Antecedents (pisahkan koma)", value=", ".join(rule.get("antecedents", [])))
            consequent = st.text_input("Consequent / Diagnosis", value=rule.get("consequent", ""))
            cf_rule = st.slider("CF Rule (0..1)", 0.0, 1.0, rule.get("cf", 0.8))
            pupuk = st.text_input("Rekomendasi Pupuk", value=rule.get("recommendation", {}).get("pupuk", ""))
            dosis = st.text_input("Dosis (format teks)", value=rule.get("recommendation", {}).get("dosis", ""))
            metode = st.selectbox("Metode Aplikasi", ["Permukaan", "Aplikasi Daun", "Irigrasi", "Campur Tanah"], index=0)
            explanation = st.text_area("Penjelasan singkat (why)", value=rule.get("explanation", ""))

            save = st.form_submit_button("Simpan Perubahan")
            delete = st.form_submit_button("Hapus Rule")

            if save:
                new_rule = {
                    "id": sel,
                    "antecedents": [a.strip() for a in antecedents_txt.split(",") if a.strip()],
                    "consequent": consequent,
                    "cf": cf_rule,
                    "recommendation": {"pupuk": pupuk, "dosis": dosis, "metode": metode},
                    "explanation": explanation,
                }
                try:
                    st.session_state.acq.update_rule(sel, new_rule)
                    st.success("Perubahan tersimpan.")
                except Exception as e:
                    st.error(f"Gagal menyimpan perubahan: {e}")

            if delete:
                try:
                    st.session_state.acq.delete_rule(sel)
                    st.success("Rule dihapus.")
                except Exception as e:
                    st.error(f"Gagal menghapus rule: {e}")


def page_statistics() -> None:
    st.header("📊 Statistik & Riwayat Konsultasi")

    # KB stats
    if st.session_state.kb:
        stats = st.session_state.kb.get_statistics()
        st.subheader("Statistik Knowledge Base")
        st.write(stats)
    else:
        st.info("KnowledgeBase belum tersedia.")

    st.markdown("---")
    st.subheader("Riwayat Konsultasi")
    try:
        history_df = st.session_state.logger.load_history() if st.session_state.logger else pd.DataFrame()
        if isinstance(history_df, pd.DataFrame) and not history_df.empty:
            st.dataframe(history_df.sort_values("timestamp", ascending=False), use_container_width=True)
            if st.button("Hapus Riwayat"):
                st.session_state.logger.clear_history()
                st.success("Riwayat dihapus.")
        else:
            st.info("Belum ada riwayat konsultasi.")
    except Exception as e:
        st.error(f"Gagal memuat riwayat: {e}")


def page_about() -> None:
    st.header("ℹ️ Tentang Sistem")
    st.markdown(
        """
        **Sistem Pakar Pemupukan Cabai**  
        - Pengembang : [Isi Nama Anda]  
        - Versi     : 1.0  
        - Metode    : Rule-based system (IF-THEN), Forward Chaining + Certainty Factor  
        
        **Catatan teknis**: Pastikan folder `modules/` berisi semua file modul yang disebutkan. 
        Apabila Anda melihat pesan error terkait modul, periksa kembali file-file di `modules/`.
        """
    )
    st.markdown("---")
    st.subheader("Kontak / Dokumentasi")
    st.write("README.md dan docs/Laporan_Teknis.md tersedia di repositori project.")


# --- Sidebar / Navigation ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/chili-pepper.png", width=80)
    st.title("Menu Navigasi")
    menu = st.radio(
        "Pilih Menu:",
        [
            "🏠 Beranda",
            "🔍 Konsultasi",
            "📚 Knowledge Base",
            "➕ Kelola Rules",
            "📊 Statistik & Riwayat",
            "ℹ️ Tentang Sistem",
        ],
        index=0,
    )
    st.markdown("---")
    if not MODULES_OK:
        st.error("Backend modules belum sepenuhnya tersedia. Periksa error di bawah.")
        for m in missing_modules:
            st.caption(m)

# --- Routing ---
if menu == "🏠 Beranda":
    page_home()
elif menu == "🔍 Konsultasi":
    page_consultation()
elif menu == "📚 Knowledge Base":
    page_knowledge_base()
elif menu == "➕ Kelola Rules":
    page_manage_rules()
elif menu == "📊 Statistik & Riwayat":
    page_statistics()
elif menu == "ℹ️ Tentang Sistem":
    page_about()
else:
    st.write("Pilihan tidak dikenali.")
