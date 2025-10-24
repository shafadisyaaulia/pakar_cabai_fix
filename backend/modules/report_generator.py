class ReportGenerator:
    def __init__(self):
        pass
    
    def generate_summary_report(self, consultations: list):
        report = {
            'total_consultations': len(consultations),
            'most_common_diagnosis': None,
            'diagnosis_counts': {}
        }
        for consult in consultations:
            for conclusion in consult.get('conclusions', []):
                diagnosis = conclusion.get('diagnosis', 'Unknown')
                report['diagnosis_counts'][diagnosis] = report['diagnosis_counts'].get(diagnosis, 0) + 1
        
        if report['diagnosis_counts']:
            report['most_common_diagnosis'] = max(report['diagnosis_counts'], key=report['diagnosis_counts'].get)
        
        return report
