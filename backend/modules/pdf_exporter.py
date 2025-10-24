from fpdf import FPDF

class PDFExporter:
    def __init__(self):
        pass
    
    def export(self, consultation_data, output_path="output.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(0, 10, "Hasil Konsultasi Sistem Pakar", ln=True, align='C')
        pdf.ln(10)
        
        pdf.cell(0, 10, f"ID Konsultasi: {consultation_data.get('consultation_id', '')}", ln=True)
        pdf.cell(0, 10, f"Waktu: {consultation_data.get('timestamp', '')}", ln=True)
        pdf.ln(10)
        
        pdf.cell(0, 10, "Gejala:", ln=True)
        for sym in consultation_data.get('facts', []):
            pdf.cell(0, 10, f"- {sym}", ln=True)
        pdf.ln(10)
        
        pdf.cell(0, 10, "Hasil Diagnosa:", ln=True)
        for conclusion in consultation_data.get('conclusions', []):
            diagnosis = conclusion.get('diagnosis', '')
            cf = conclusion.get('cf', 0)
            pdf.cell(0, 10, f"- {diagnosis} (CF: {cf})", ln=True)
        
        pdf.output(output_path)
        return output_path
