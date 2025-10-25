"""
Report Generator Module
Generate statistical reports dari consultation history
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter


class ReportGenerator:
    """Class untuk generate berbagai jenis laporan"""
    
    def __init__(self):
        pass
    
    def generate_summary_report(self, history_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary report dari consultation history
        
        Args:
            history_df: DataFrame berisi history konsultasi
            
        Returns:
            Dictionary berisi statistik summary
        """
        if history_df.empty:
            return {
                "total_consultations": 0,
                "most_common_diagnosis": None,
                "avg_cf": 0.0,
                "unique_diagnoses": 0,
                "message": "Belum ada data konsultasi"
            }
        
        # Basic statistics
        total = len(history_df)
        unique_diagnoses = history_df['diagnosis'].nunique()
        
        # Most common diagnosis
        diagnosis_counts = history_df['diagnosis'].value_counts()
        most_common = diagnosis_counts.index[0] if not diagnosis_counts.empty else None
        most_common_count = diagnosis_counts.iloc[0] if not diagnosis_counts.empty else 0
        
        # Average CF
        avg_cf = history_df['cf'].mean() if 'cf' in history_df.columns else 0.0
        
        # Diagnosis distribution
        diagnosis_distribution = diagnosis_counts.to_dict()
        
        # CF distribution by diagnosis
        cf_by_diagnosis = history_df.groupby('diagnosis')['cf'].agg(['mean', 'min', 'max']).to_dict('index')
        
        # Recent trend (last 7 days)
        if 'timestamp' in history_df.columns:
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            last_7_days = datetime.now() - timedelta(days=7)
            recent = history_df[history_df['timestamp'] >= last_7_days]
            recent_count = len(recent)
        else:
            recent_count = 0
        
        # Fase distribution
        fase_distribution = {}
        if 'fase' in history_df.columns:
            fase_distribution = history_df['fase'].value_counts().to_dict()
        
        return {
            "total_consultations": total,
            "most_common_diagnosis": most_common,
            "most_common_count": int(most_common_count),
            "avg_cf": round(float(avg_cf), 3),
            "avg_cf_percentage": f"{float(avg_cf) * 100:.1f}%",
            "unique_diagnoses": int(unique_diagnoses),
            "diagnosis_distribution": diagnosis_distribution,
            "cf_by_diagnosis": cf_by_diagnosis,
            "consultations_last_7_days": recent_count,
            "fase_distribution": fase_distribution,
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_diagnosis_report(self, history_df: pd.DataFrame, diagnosis_name: str) -> Dict[str, Any]:
        """
        Generate detailed report untuk satu diagnosis
        
        Args:
            history_df: DataFrame history
            diagnosis_name: Nama diagnosis yang ingin di-report
            
        Returns:
            Detailed report untuk diagnosis tersebut
        """
        filtered = history_df[history_df['diagnosis'] == diagnosis_name]
        
        if filtered.empty:
            return {
                "diagnosis": diagnosis_name,
                "total_cases": 0,
                "message": f"Tidak ada data untuk diagnosis: {diagnosis_name}"
            }
        
        return {
            "diagnosis": diagnosis_name,
            "total_cases": len(filtered),
            "avg_cf": round(filtered['cf'].mean(), 3),
            "min_cf": round(filtered['cf'].min(), 3),
            "max_cf": round(filtered['cf'].max(), 3),
            "first_occurrence": filtered['timestamp'].min() if 'timestamp' in filtered.columns else None,
            "last_occurrence": filtered['timestamp'].max() if 'timestamp' in filtered.columns else None
        }
    
    def generate_trend_report(self, history_df: pd.DataFrame, days: int = 30) -> Dict[str, Any]:
        """
        Generate trend report untuk N hari terakhir
        
        Args:
            history_df: DataFrame history
            days: Jumlah hari untuk analisis trend
            
        Returns:
            Trend data
        """
        if 'timestamp' not in history_df.columns or history_df.empty:
            return {
                "message": "Data timestamp tidak tersedia",
                "consultations_by_day": {}
            }
        
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        cutoff_date = datetime.now() - timedelta(days=days)
        recent = history_df[history_df['timestamp'] >= cutoff_date]
        
        # Group by date
        recent['date'] = recent['timestamp'].dt.date
        consultations_by_day = recent.groupby('date').size().to_dict()
        
        # Convert date objects to strings
        consultations_by_day = {str(k): int(v) for k, v in consultations_by_day.items()}
        
        return {
            "period_days": days,
            "total_consultations": len(recent),
            "consultations_by_day": consultations_by_day,
            "avg_per_day": round(len(recent) / days, 2)
        }
    
    def generate_top_diagnoses_report(self, history_df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """
        Generate report untuk top N diagnosis terbanyak
        
        Args:
            history_df: DataFrame history
            top_n: Jumlah top diagnosis
            
        Returns:
            List of top diagnoses dengan detail
        """
        if history_df.empty:
            return []
        
        diagnosis_counts = history_df['diagnosis'].value_counts().head(top_n)
        
        result = []
        for diagnosis, count in diagnosis_counts.items():
            filtered = history_df[history_df['diagnosis'] == diagnosis]
            result.append({
                "diagnosis": diagnosis,
                "count": int(count),
                "percentage": round((count / len(history_df)) * 100, 1),
                "avg_cf": round(filtered['cf'].mean(), 3)
            })
        
        return result
