import joblib
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Load model artifacts correctly from model/ folder
model = joblib.load(os.path.join(BASE_DIR, 'model/xgb_churn_model.pkl'))
scaler = joblib.load(os.path.join(BASE_DIR, 'model/scaler.pkl'))
encoder = joblib.load(os.path.join(BASE_DIR, 'model/encoder.pkl'))
imputer = joblib.load(os.path.join(BASE_DIR, 'model/imputer.pkl'))
numeric_features = joblib.load(os.path.join(BASE_DIR, 'model/numeric_features.pkl'))
categorical_features = joblib.load(os.path.join(BASE_DIR, 'model/categorical_features.pkl'))
encoded_cols = joblib.load(os.path.join(BASE_DIR, 'model/encoded_columns.pkl'))

class PredictChurnAPIView(APIView):
    def post(self, request):
        try:
            input_data = request.data
            input_df = pd.DataFrame([input_data])
            
            # Filter categorical features (use the loaded variable directly)
            filtered_categorical_features = [col for col in categorical_features if col not in ['customerID', 'Churn']]

            # Feature Engineering
            input_df['Avg_Monthly_Charge'] = input_df['TotalCharges'] / (input_df['tenure'] + 1)

            # Impute, Scale, Encode
            input_df[numeric_features] = imputer.transform(input_df[numeric_features])
            input_df[numeric_features] = scaler.transform(input_df[numeric_features])
            input_df[encoded_cols] = encoder.transform(input_df[filtered_categorical_features])
            
            x_input = input_df[numeric_features + encoded_cols]
            pred = model.predict(x_input)[0]
            proba = model.predict_proba(x_input)[0][1]
            result = {
                "prediction": "Yes" if pred == 1 else "No",
                "churn_probability": round(proba * 100, 2)
            }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# ---- Usage ----
# Run server:
# python manage.py runserver
# Then POST to http://127.0.0.1:8000/api/predict/ with a JSON body like:
# {
#   "gender": "Female",
#   "SeniorCitizen": 0,
#   "Partner": "Yes",
#   "Dependents": "No",
#   "tenure": 5,
#   "PhoneService": "Yes",
#   "MultipleLines": "No",
#   "InternetService": "Fiber optic",
#   "OnlineSecurity": "No",
#   "OnlineBackup": "Yes",
#   "DeviceProtection": "Yes",
#   "TechSupport": "No",
#   "StreamingTV": "No",
#   "StreamingMovies": "Yes",
#   "Contract": "Month-to-month",
#   "PaperlessBilling": "Yes",
#   "PaymentMethod": "Electronic check",
#   "MonthlyCharges": 80.35,
#   "TotalCharges": 401.75
# }
