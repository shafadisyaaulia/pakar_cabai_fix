"""
PDF Exporter Module
Generate PDF reports dari hasil konsultasi
"""

from fpdf import FPDF
from datetime import datetime
from pathlib import Path


class PDFExporter:
    """Class untuk export hasil konsultasi ke PDF"""
    
    def __init__(self, output_dir="data/reports"):
        self.output_dir = output_dir
        # Pastikan folder output ada
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def export_consultation_report(self, consultation_data):
        """
        Generate PDF report dari data konsultasi
        
        Args:
            consultation_data (dict): Data konsultasi dengan keys:
                - consultation_id
                - timestamp
                - symptoms
                - fase
                - conclusions
        
        Returns:
            str: Path file PDF yang di-generate
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        # Header
        pdf.cell(0, 10, "Laporan Diagnosis - Sistem Pakar Pemupukan Cabai", ln=True, align="C")
        pdf.ln(5)
        
        # Info Konsultasi
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"ID Konsultasi: {consultation_data.get('consultation_id', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"Tanggal: {consultation_data.get('timestamp', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"Fase: {consultation_data.get('fase', 'N/A')}", ln=True)
        pdf.ln(5)
        
        # Gejala yang dipilih
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Gejala yang Terdeteksi:", ln=True)
        pdf.set_font("Arial", "", 10)
        for symptom in consultation_data.get('symptoms', []):
            pdf.cell(0, 6, f"  - {symptom.replace('_', ' ').title()}", ln=True)
        pdf.ln(5)
        
        # Hasil Diagnosis
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Hasil Diagnosis:", ln=True)
        
        conclusions = consultation_data.get('conclusions', [])
        if not conclusions:
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, "Tidak ditemukan diagnosis.", ln=True)
        else:
            for idx, conclusion in enumerate(conclusions, 1):
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, f"{idx}. {conclusion.get('diagnosis', 'N/A')}", ln=True)
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"   Tingkat Kepercayaan: {conclusion.get('cf', 0) * 100:.1f}%", ln=True)
                
                rec = conclusion.get('recommendation', {})
                pdf.cell(0, 6, f"   Pupuk: {rec.get('pupuk', 'N/A')}", ln=True)
                pdf.cell(0, 6, f"   Dosis: {rec.get('dosis', 'N/A')}", ln=True)
                pdf.cell(0, 6, f"   Metode: {rec.get('metode', 'N/A')}", ln=True)
                pdf.ln(3)
        
        # Save PDF
        filename = f"laporan_{consultation_data.get('consultation_id', 'unknown')}.pdf"
        filepath = Path(self.output_dir) / filename
        pdf.output(str(filepath))
        
        return str(filepath)
