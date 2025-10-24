class FormatHelper:
    def __init__(self):
        pass
    
    def format_date(self, date_obj):
        return date_obj.strftime("%Y-%m-%d %H:%M:%S") if date_obj else ""
    
    def shorten_text(self, text, max_length=50):
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def format_float(self, value, decimals=2):
        try:
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return "0.00"
