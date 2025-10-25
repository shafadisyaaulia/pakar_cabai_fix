import pandas as pd
from pathlib import Path

class ConsultationLogger:
    def __init__(self, log_file="data/consultations.csv"):
        self.log_file = log_file
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Buat file CSV jika belum ada
        if not Path(log_file).exists():
            df = pd.DataFrame(columns=[
                "consultation_id", "timestamp", "symptoms", 
                "fase", "diagnosis", "cf"
            ])
            df.to_csv(log_file, index=False)
    
    def log_consultation(self, consultation_data):
        """Save consultation to CSV"""
        try:
            df = pd.read_csv(self.log_file)
            
            # Extract first diagnosis if available
            conclusions = consultation_data.get("conclusions", [])
            diagnosis = conclusions[0].get("diagnosis", "N/A") if conclusions else "N/A"
            cf = conclusions[0].get("cf", 0.0) if conclusions else 0.0
            
            new_row = {
                "consultation_id": consultation_data.get("consultation_id", "N/A"),
                "timestamp": consultation_data.get("timestamp", ""),
                "symptoms": str(consultation_data.get("symptoms", [])),
                "fase": consultation_data.get("fase", ""),
                "diagnosis": diagnosis,
                "cf": cf
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.log_file, index=False)
        except Exception as e:
            print(f"[ERROR] Failed to log consultation: {e}")
    
    def load_history(self):
        """Load consultation history from CSV"""
        try:
            if Path(self.log_file).exists():
                df = pd.read_csv(self.log_file)
                
                # ⬇️ CONVERT NaN ke string atau default value
                df = df.fillna({
                    "consultation_id": "unknown",
                    "timestamp": "",
                    "symptoms": "[]",
                    "fase": "",
                    "diagnosis": "No diagnosis",
                    "cf": 0.0
                })
                
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"[ERROR] Failed to load history: {e}")
            return pd.DataFrame()
