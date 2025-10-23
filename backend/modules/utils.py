"""
Utilities Module
Fungsi-fungsi utility untuk export, logging, dan helper functions
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ConsultationLogger:
    """Class untuk logging konsultasi"""
    
    def __init__(self, log_file: str = 'data/consultations.csv'):
        """
        Inisialisasi logger
        
        Args:
            log_file: Path ke file log CSV
        """
        self.log_file = log_file
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Pastikan file log dan direktori ada"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'consultation_id', 'facts_count', 
                    'diagnosis', 'cf', 'pupuk', 'dosis', 'rules_used'
                ])
    
    def log_consultation(self, consultation_data: Dict[str, Any]) -> bool:
        """
        Log hasil konsultasi ke CSV
        
        Args:
            consultation_data: Data konsultasi
        
        Returns:
            True jika berhasil
        """
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                conclusions = consultation_data.get('conclusions', [])
                top_conclusion = conclusions[0] if conclusions else {}
                
                writer.writerow([
                    datetime.now().isoformat(),
                    consultation_data.get('consultation_id', 'N/A'),
                    len(consultation_data.get('facts', [])),
                    top_conclusion.get('diagnosis', 'N/A'),
                    top_conclusion.get('cf', 0),
                    top_conclusion.get('recommendation', {}).get('pupuk', 'N/A'),
                    top_conclusion.get('recommendation', {}).get('dosis', 'N/A'),
                    ','.join(consultation_data.get('used_rules', []))
                ])
            return True
        except Exception as e:
            print(f"Error logging consultation: {e}")
            return False
    
    def get_consultation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Ambil riwayat konsultasi
        
        Args:
            limit: Maksimal jumlah records (None = semua)
        
        Returns:
            List consultation records
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
                
                if limit:
                    return records[-limit:]
                return records
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error reading consultation history: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Dapatkan statistik dari log konsultasi"""
        records = self.get_consultation_history()
        
        if not records:
            return {
                'total_consultations': 0,
                'unique_diagnoses': 0,
                'avg_cf': 0,
                'most_common_diagnosis': 'N/A'
            }
        
        # Parse data
        diagnoses = [r['diagnosis'] for r in records if r['diagnosis'] != 'N/A']
        cfs = [float(r['cf']) for r in records if r['cf'] and r['cf'] != 'N/A']
        
        # Count diagnosis frequency
        diagnosis_count = {}
        for d in diagnoses:
            diagnosis_count[d] = diagnosis_count.get(d, 0) + 1
        
        most_common = max(diagnosis_count.items(), key=lambda x: x[1])[0] if diagnosis_count else 'N/A'
        
        return {
            'total_consultations': len(records),
            'unique_diagnoses': len(set(diagnoses)),
            'avg_cf': sum(cfs) / len(cfs) if cfs else 0,
            'most_common_diagnosis': most_common,
            'diagnosis_distribution': diagnosis_count
        }


class PDFExporter:
    """Class untuk export laporan ke PDF"""
    
    def __init__(self):
        """Inisialisasi PDF Exporter"""
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self):
        """Tambahkan custom styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1B5E20'),
            spaceAfter=12
        ))
    
    def export_consultation_report(self, consultation_data: Dict[str, Any], 
                                   output_file: str) -> bool:
        """
        Export consultation report ke PDF
        
        Args:
            consultation_data: Data konsultasi
            output_file: Path output file
        
        Returns:
            True jika berhasil
        """
        try:
            doc = SimpleDocTemplate(output_file, pagesize=A4)
            story = []
            
            # Title
            title = Paragraph("LAPORAN KONSULTASI<br/>SISTEM PAKAR PUPUK CABAI", 
                            self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            # Metadata
            metadata_data = [
                ['Tanggal', datetime.now().strftime("%d %B %Y, %H:%M:%S")],
                ['ID Konsultasi', consultation_data.get('consultation_id', 'N/A')],
                ['Jumlah Gejala', str(len(consultation_data.get('facts', [])))]
            ]
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(metadata_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Fakta Input
            story.append(Paragraph("1. FAKTA INPUT", self.styles['CustomHeading']))
            facts = consultation_data.get('facts', [])
            for i, fact in enumerate(facts, 1):
                story.append(Paragraph(f"   {i}. {fact}", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Hasil Diagnosis
            story.append(Paragraph("2. HASIL DIAGNOSIS", self.styles['CustomHeading']))
            conclusions = consultation_data.get('conclusions', [])
            
            for i, conclusion in enumerate(conclusions[:3], 1):
                # Diagnosis header
                diag_text = f"<b>{i}. {conclusion['diagnosis']}</b>"
                story.append(Paragraph(diag_text, self.styles['Normal']))
                
                # Detail table
                detail_data = [
                    ['Tingkat Kepercayaan', f"{conclusion['cf']*100:.1f}% ({conclusion['cf_interpretation']})"],
                    ['Pupuk', conclusion['recommendation']['pupuk']],
                    ['Dosis', conclusion['recommendation']['dosis']],
                    ['Metode', conclusion['recommendation']['metode']]
                ]
                
                detail_table = Table(detail_data, colWidths=[2*inch, 4*inch])
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F8E9')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(detail_table)
                story.append(Spacer(1, 0.15*inch))
            
            # Alur Penalaran
            story.append(PageBreak())
            story.append(Paragraph("3. ALUR PENALARAN", self.styles['CustomHeading']))
            
            reasoning_path = consultation_data.get('reasoning_path', [])
            for step in reasoning_path:
                step_text = f"<b>Step {step['step']}: Rule {step['rule']}</b>"
                story.append(Paragraph(step_text, self.styles['Normal']))
                story.append(Paragraph(f"IF: {' AND '.join(step['conditions'])}", 
                                     self.styles['Normal']))
                story.append(Paragraph(f"THEN: {step['conclusion']}", 
                                     self.styles['Normal']))
                story.append(Paragraph(f"CF: {step['cf']*100:.1f}%", 
                                     self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            # Rules Used
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("4. RULES YANG DIGUNAKAN", self.styles['CustomHeading']))
            used_rules = consultation_data.get('used_rules', [])
            rules_text = f"Total: {len(used_rules)} rules<br/>"
            rules_text += f"Rules: {', '.join(used_rules)}"
            story.append(Paragraph(rules_text, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            return True
        
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return False


class DataExporter:
    """Class untuk berbagai format export"""
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], output_file: str) -> bool:
        """Export data ke JSON"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False
    
    @staticmethod
    def export_to_csv(data: List[Dict], output_file: str) -> bool:
        """Export data ke CSV"""
        try:
            if not data:
                return False
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False
    
    @staticmethod
    def export_to_txt(content: str, output_file: str) -> bool:
        """Export content ke TXT"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error exporting TXT: {e}")
            return False


class ValidationHelper:
    """Helper untuk validasi input"""
    
    @staticmethod
    def validate_cf(cf: float) -> bool:
        """Validasi Certainty Factor"""
        return isinstance(cf, (int, float)) and 0 <= cf <= 1
    
    @staticmethod
    def validate_rule_id(rule_id: str) -> bool:
        """Validasi format Rule ID"""
        return isinstance(rule_id, str) and rule_id.strip() != ''
    
    @staticmethod
    def validate_conditions(conditions: List[str]) -> bool:
        """Validasi list kondisi"""
        return isinstance(conditions, list) and len(conditions) > 0 and all(isinstance(c, str) for c in conditions)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input text"""
        return text.strip().replace('\n', ' ').replace('\r', '')


class FormatHelper:
    """Helper untuk formatting output"""
    
    @staticmethod
    def format_cf(cf: float, show_interpretation: bool = False) -> str:
        """Format CF untuk display"""
        percentage = f"{cf*100:.1f}%"
        
        if show_interpretation:
            if cf >= 0.8:
                interp = "Sangat Yakin"
            elif cf >= 0.6:
                interp = "Yakin"
            elif cf >= 0.4:
                interp = "Cukup Yakin"
            elif cf >= 0.2:
                interp = "Kurang Yakin"
            else:
                interp = "Tidak Yakin"
            return f"{percentage} ({interp})"
        
        return percentage
    
    @staticmethod
    def format_timestamp(timestamp_str: str = None) -> str:
        """Format timestamp untuk display"""
        if timestamp_str:
            try:
                dt = datetime.fromisoformat(timestamp_str)
            except:
                return timestamp_str
        else:
            dt = datetime.now()
        
        return dt.strftime("%d %B %Y, %H:%M:%S")
    
    @staticmethod
    def format_list_with_numbers(items: List[str]) -> str:
        """Format list dengan numbering"""
        return '\n'.join([f"{i}. {item}" for i, item in enumerate(items, 1)])
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
        """Truncate text dengan suffix"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


class StatisticsHelper:
    """Helper untuk perhitungan statistik"""
    
    @staticmethod
    def calculate_average(values: List[float]) -> float:
        """Hitung rata-rata"""
        return sum(values) / len(values) if values else 0.0
    
    @staticmethod
    def calculate_median(values: List[float]) -> float:
        """Hitung median"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    @staticmethod
    def calculate_mode(values: List) -> Any:
        """Hitung mode (nilai paling sering muncul)"""
        if not values:
            return None
        
        from collections import Counter
        counter = Counter(values)
        return counter.most_common(1)[0][0]
    
    @staticmethod
    def calculate_distribution(values: List, bins: List[tuple]) -> Dict[str, int]:
        """Hitung distribusi nilai ke dalam bins"""
        distribution = {f"{b[0]}-{b[1]}": 0 for b in bins}
        
        for value in values:
            for bin_range in bins:
                if bin_range[0] <= value < bin_range[1]:
                    distribution[f"{bin_range[0]}-{bin_range[1]}"] += 1
                    break
        
        return distribution


class FileHelper:
    """Helper untuk operasi file"""
    
    @staticmethod
    def ensure_directory(directory: str):
        """Pastikan direktori ada"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_file_size(file_path: str) -> str:
        """Dapatkan ukuran file dalam format readable"""
        try:
            size_bytes = os.path.getsize(file_path)
            
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            
            return f"{size_bytes:.2f} TB"
        except:
            return "Unknown"
    
    @staticmethod
    def get_file_age(file_path: str) -> str:
        """Dapatkan umur file"""
        try:
            mtime = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(mtime)
            now = datetime.now()
            delta = now - file_date
            
            if delta.days == 0:
                return "Hari ini"
            elif delta.days == 1:
                return "Kemarin"
            elif delta.days < 7:
                return f"{delta.days} hari yang lalu"
            elif delta.days < 30:
                return f"{delta.days // 7} minggu yang lalu"
            elif delta.days < 365:
                return f"{delta.days // 30} bulan yang lalu"
            else:
                return f"{delta.days // 365} tahun yang lalu"
        except:
            return "Unknown"
    
    @staticmethod
    def backup_file(file_path: str) -> bool:
        """Buat backup file"""
        try:
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False


class ColorHelper:
    """Helper untuk color coding berdasarkan CF"""
    
    @staticmethod
    def get_cf_color(cf: float) -> str:
        """Dapatkan warna berdasarkan CF untuk terminal/UI"""
        if cf >= 0.8:
            return 'green'
        elif cf >= 0.6:
            return 'lightgreen'
        elif cf >= 0.4:
            return 'yellow'
        elif cf >= 0.2:
            return 'orange'
        else:
            return 'red'
    
    @staticmethod
    def get_cf_hex_color(cf: float) -> str:
        """Dapatkan hex color berdasarkan CF"""
        if cf >= 0.8:
            return '#4CAF50'  # Green
        elif cf >= 0.6:
            return '#8BC34A'  # Light Green
        elif cf >= 0.4:
            return '#FFC107'  # Amber
        elif cf >= 0.2:
            return '#FF9800'  # Orange
        else:
            return '#F44336'  # Red


class ReportGenerator:
    """Generator untuk berbagai jenis report"""
    
    @staticmethod
    def generate_text_report(consultation_data: Dict[str, Any]) -> str:
        """Generate text report"""
        report = []
        report.append("=" * 70)
        report.append("LAPORAN KONSULTASI SISTEM PAKAR PUPUK CABAI")
        report.append("=" * 70)
        report.append("")
        
        # Metadata
        report.append(f"Tanggal: {FormatHelper.format_timestamp()}")
        report.append(f"ID Konsultasi: {consultation_data.get('consultation_id', 'N/A')}")
        report.append("")
        
        # Fakta
        report.append("FAKTA INPUT:")
        report.append("-" * 70)
        facts = consultation_data.get('facts', [])
        for i, fact in enumerate(facts, 1):
            report.append(f"{i}. {fact}")
        report.append("")
        
        # Diagnosis
        report.append("HASIL DIAGNOSIS:")
        report.append("-" * 70)
        conclusions = consultation_data.get('conclusions', [])
        for i, conclusion in enumerate(conclusions[:3], 1):
            report.append(f"\n{i}. {conclusion['diagnosis']}")
            report.append(f"   Certainty Factor: {FormatHelper.format_cf(conclusion['cf'], True)}")
            report.append(f"   Pupuk: {conclusion['recommendation']['pupuk']}")
            report.append(f"   Dosis: {conclusion['recommendation']['dosis']}")
            report.append(f"   Metode: {conclusion['recommendation']['metode']}")
            report.append(f"   Penjelasan: {conclusion['explanation']}")
        
        report.append("")
        report.append("ALUR PENALARAN:")
        report.append("-" * 70)
        reasoning_path = consultation_data.get('reasoning_path', [])
        for step in reasoning_path:
            report.append(f"\nStep {step['step']}: Rule {step['rule']}")
            report.append(f"IF: {' AND '.join(step['conditions'])}")
            report.append(f"THEN: {step['conclusion']}")
            report.append(f"CF: {FormatHelper.format_cf(step['cf'])}")
        
        report.append("")
        report.append("RULES YANG DIGUNAKAN:")
        report.append("-" * 70)
        used_rules = consultation_data.get('used_rules', [])
        report.append(f"Total: {len(used_rules)} rules")
        report.append(f"Rules: {', '.join(used_rules)}")
        
        report.append("")
        report.append("=" * 70)
        
        return '\n'.join(report)
    
    @staticmethod
    def generate_summary_report(statistics: Dict[str, Any]) -> str:
        """Generate summary statistics report"""
        report = []
        report.append("=" * 70)
        report.append("LAPORAN STATISTIK SISTEM PAKAR")
        report.append("=" * 70)
        report.append("")
        
        report.append(f"Total Konsultasi: {statistics.get('total_consultations', 0)}")
        report.append(f"Diagnosis Unik: {statistics.get('unique_diagnoses', 0)}")
        report.append(f"Average CF: {statistics.get('avg_cf', 0):.3f}")
        report.append(f"Diagnosis Paling Umum: {statistics.get('most_common_diagnosis', 'N/A')}")
        
        report.append("")
        report.append("DISTRIBUSI DIAGNOSIS:")
        report.append("-" * 70)
        
        distribution = statistics.get('diagnosis_distribution', {})
        for diagnosis, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / statistics.get('total_consultations', 1)) * 100
            report.append(f"{diagnosis}: {count} ({percentage:.1f}%)")
        
        report.append("")
        report.append("=" * 70)
        
        return '\n'.join(report)


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("TESTING UTILITIES MODULE")
    print("=" * 70)
    
    # Test 1: Consultation Logger
    print("\n### TEST 1: Consultation Logger ###")
    logger = ConsultationLogger('data/consultations.csv')
    
    test_consultation = {
        'consultation_id': 'CONS001',
        'facts': ['fase_vegetatif', 'daun_kuning_merata', 'pertumbuhan_lambat'],
        'conclusions': [{
            'diagnosis': 'Kekurangan Nitrogen (N)',
            'cf': 0.85,
            'cf_interpretation': 'Sangat Yakin',
            'recommendation': {
                'pupuk': 'Urea',
                'dosis': '150-200 kg/ha',
                'metode': 'Aplikasi bertahap'
            }
        }],
        'used_rules': ['R1']
    }
    
    success = logger.log_consultation(test_consultation)
    print(f"Logging success: {success}")
    
    # Test 2: Format Helper
    print("\n### TEST 2: Format Helper ###")
    print(f"CF Formatted: {FormatHelper.format_cf(0.85, True)}")
    print(f"Timestamp: {FormatHelper.format_timestamp()}")
    
    # Test 3: Statistics Helper
    print("\n### TEST 3: Statistics Helper ###")
    values = [0.7, 0.8, 0.9, 0.75, 0.85]
    print(f"Average: {StatisticsHelper.calculate_average(values):.3f}")
    print(f"Median: {StatisticsHelper.calculate_median(values):.3f}")
    
    # Test 4: Validation Helper
    print("\n### TEST 4: Validation Helper ###")
    print(f"Valid CF 0.8: {ValidationHelper.validate_cf(0.8)}")
    print(f"Valid CF 1.5: {ValidationHelper.validate_cf(1.5)}")
    print(f"Valid Rule ID 'R1': {ValidationHelper.validate_rule_id('R1')}")
    
    # Test 5: Report Generator
    print("\n### TEST 5: Report Generator ###")
    report = ReportGenerator.generate_text_report(test_consultation)
    print("Text report generated (first 200 chars):")
    print(report[:200] + "...")
    
    # Test 6: PDF Exporter
    print("\n### TEST 6: PDF Exporter ###")
    pdf_exporter = PDFExporter()
    pdf_success = pdf_exporter.export_consultation_report(
        test_consultation, 
        'test_report.pdf'
    )
    print(f"PDF export success: {pdf_success}")
    
    print("\n" + "=" * 70)
    print("UTILITIES TESTS COMPLETED")
    print("=" * 70)