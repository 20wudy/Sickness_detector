import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
import joblib
from datetime import datetime
import os
import logging


logging.basicConfig(level=logging.INFO)


class HealthMonitor:
    def __init__(self, user_id):
        self.model = None
        self.user_id = user_id
        self.data_file = f"data/{user_id}.csv"
        self.model_file = f"models/{user_id}.joblib"
        self.min_days = 3
        self.window_size = 14

        
        if os.path.isfile(self.data_file):
            self.data = pd.read_csv(self.data_file, parse_dates=['date'])
        else:
            self.data = pd.DataFrame(columns=[
                'date', 'avg_hr', 'min_hr', 'max_hr', 
                'sleep_hours', 'sleep_quality'
            ])

        try:
            self.model = joblib.load(self.model_file) if os.path.exists(self.model_file) else None
        except Exception as e:
            logging.warning(f"Could not load model for user {user_id}: {e}")
            self.model = None


    def add_record(self, input_data):
        now_str = datetime.now().strftime('%Y-%m-%d')
        try:
            new_row = pd.DataFrame([{
                'date': pd.to_datetime(input_data.get('date', datetime.now())),
                'avg_hr': input_data.get('avg_hr'),
                'min_hr': input_data.get('min_hr'),
                'max_hr': input_data.get('max_hr'),
                'sleep_hours': input_data.get('sleep_hours'),
                'sleep_quality': input_data.get('sleep_quality', 80)
            }])

        except TypeError as e:
            logging.error(f"Invalid input data: {input_data}")
            raise e

        self.data = pd.concat([self.data, new_row]).drop_duplicates('date')
        # try:
        self.data.to_csv(self.data_file, index=False)
        # except Exception as e:
        #     logging.error(f"Failed to save data for user {self.user_id}: {e}")

        self._update_model()


    def _update_model(self):
        if len(self.data) < self.min_days:
            logging.info("Not enough data to train model.")
            return

        try:
        
            df = self.data.sort_values('date').tail(self.window_size).copy()
            df['hr_14day_avg'] = df['avg_hr'].rolling(14, min_periods=3).mean()
            df['sleep_14day_avg'] = df['sleep_hours'].rolling(14, min_periods=3).mean()
            df['quality_14day_avg'] = df['sleep_quality'].rolling(14, min_periods=3).mean()
            
            df['rest_hr_14_avg'] = df['min_hr'].rolling(14, min_periods=3).mean()

            features = df[['avg_hr', 'sleep_hours', 'sleep_quality', 'min_hr']].dropna()

            self.model = Pipeline([
                ('scaler', RobustScaler()),
                ('model', IsolationForest(n_estimators=50, contamination='auto',
                                           random_state=42, behavior = 'new')) # TUNE
            ])
            self.model.fit(features)
            joblib.dump(self.model, self.model_file)

        except Exception as e:
            logging.error(f"Model training failed: {e}")


    def get_analysis(self):
        if len(self.data) < self.min_days:
            return {
                'status': 'insufficient_data',
                'required_days': self.min_days,
                'current_days': len(self.data)
            }

        # Fix time formatting issue
        df = self.data.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        df = df.sort_values('date')
        df['hr_14day_avg'] = df['avg_hr'].rolling(14, min_periods=3).mean()
        df['sleep_14day_avg'] = df['sleep_hours'].rolling(14, min_periods=3).mean()
        df['rest_hr_14_avg'] = df['min_hr'].rolling(14, min_periods=3).mean()
        
        # Check time formatting
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

        

        if self.model is not None:
            try:
                features = df[['avg_hr', 'sleep_hours', 'sleep_quality', 'min_hr']].dropna()

                preds = self.model.predict(features)  #0 or -1
                df.loc[features.index, 'is_anomaly'] = (preds == -1).astype(int)

                scores = self.model.decision_function(features)
                df.loc[features.index, 'anomaly_score'] = scores

            except Exception as e:
                logging.error(f"Error during anomaly detection: {e}")
                df['is_anomaly'] = 0
                df['anomaly_score'] = 0.0


        # Sudden spikes not accounted for
        hr_spikes = (df['avg_hr'] > (df['hr_14day_avg'] * 1.5)) | (df['avg_hr'] < (df['hr_14day_avg'] * 0.6))
        df.loc[hr_spikes, 'is_anomaly'] = 1

        min_hr_spikes = (df['min_hr'] > (df['rest_hr_14_avg'] * 1.1)) | (df['min_hr'] < (df['rest_hr_14_avg'] * 0.8))
        df.loc[min_hr_spikes, 'is_anomaly'] = 1

        sleep_spike = (df['sleep_hours'] < (df['sleep_14day_avg'] * 0.5))
        df.loc[sleep_spike, 'is_anomaly'] = 1
        
        return {
            'status': 'success',
            'latest_data': df.iloc[-1].to_dict(),
            'chart_data': df.tail(30).to_dict('records'),
            'anomalies': df[df['is_anomaly'] == 1][['date_str', 'avg_hr', 'anomaly_score']].to_dict('records')
        }

