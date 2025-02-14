import sys
import os
from datetime import datetime, timedelta
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger_app import get_logs, LogLevel, LogCategory

class LogAnalytics:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutos

    def get_error_frequency(self, timeframe='day'):
        """Analisa frequência de erros por período"""
        logs = get_logs(level=LogLevel.ERROR)
        df = pd.DataFrame(logs)
        
        if timeframe == 'day':
            df['date'] = pd.to_datetime(df['Timestamp']).dt.date
            return df.groupby('date').size()
        elif timeframe == 'hour':
            df['hour'] = pd.to_datetime(df['Timestamp']).dt.hour
            return df.groupby('hour').size()
        
        return df.groupby('Level').size()

    def get_user_activity(self, user=None, days=7):
        """Analisa atividade dos usuários"""
        start_date = (datetime.now() - timedelta(days=7)).strftime('%d/%m/%Y')
        logs = get_logs(
            category=LogCategory.USER_ACTION,
            user=user,
            start_date=start_date
        )
        return pd.DataFrame(logs)

    def get_security_report(self, days=30):
        """Gera relatório de segurança"""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%d/%m/%Y')
        logs = get_logs(
            level=LogLevel.SECURITY,
            start_date=start_date
        )
        return pd.DataFrame(logs)

    def get_system_health(self):
        """Analisa saúde do sistema baseado nos logs"""
        last_day = datetime.now().strftime('%d/%m/%Y')
        logs = get_logs(start_date=last_day)
        df = pd.DataFrame(logs)
        
        return {
            'total_logs': len(df),
            'error_rate': len(df[df['Level'] == 'ERROR']) / len(df) if len(df) > 0 else 0,
            'active_users': df['User'].nunique(),
            'most_common_errors': df[df['Level'] == 'ERROR']['Details'].value_counts().head(5)
        }
