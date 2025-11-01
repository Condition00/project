from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os 

app = Flask(__name__)

# Load models with error handling
models = {}
try:
    models = {
        "morning": {
            "clf": joblib.load("./model/model_clf_morning.pkl"),
            "reg": joblib.load("./model/model_reg_morning.pkl")
        },
        "afternoon": {
            "clf": joblib.load("./model/model_clf_afternoon.pkl"),
            "reg": joblib.load("./model/model_reg_afternoon.pkl")
        },
        "night": {
            "clf": joblib.load("./model/model_clf_evening.pkl"),
            "reg": joblib.load("./model/model_reg_evening.pkl")
        }
    }
    print("Models loaded successfully")
except Exception as e:
    print(f"Error loading models: {e}")
    models = {}

def mins_to_time(m):
    h = int(m // 60)
    s = int(m % 60)
    return f"{h:02d}:{s:02d}"

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Smart Medicine Box AI API", 
        "status": "running",
        "models_loaded": len(models) > 0,
        "available_endpoints": ["/health", "/predict", "/routes"]
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "message": "Service is operational",
        "models_status": "loaded" if len(models) > 0 else "failed_to_load",
        "available_time_periods": list(models.keys()) if models else []
    }), 200

@app.route('/routes', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "route": str(rule)
        })
    return jsonify({"routes": routes}), 200

@app.route('/predict', methods=['POST'])
def predict():
    # Check if models are loaded
    if not models:
        return jsonify({"error": "Models not loaded. Check server logs."}), 500
    
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        time_period = data.get("time_period", "").lower()
        if time_period not in models:
            return jsonify({
                "error": f"Invalid time_period '{time_period}'. Use: {', '.join(models.keys())}"
            }), 400

        try:
            features = pd.DataFrame([{
                "morning_time": data["morning_time"],
                "afternoon_time": data["afternoon_time"],
                "evening_time": data["evening_time"],
                "takenMorning": data["takenMorning"],
                "takenAfternoon": data["takenAfternoon"],
                "takenEvening": data["takenEvening"],
                "day_of_week": data["day_of_week"]
            }])
        except KeyError as e:
            return jsonify({"error": f"Missing field: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Data processing error: {str(e)}"}), 400

        try:
            clf = models[time_period]["clf"]
            reg = models[time_period]["reg"]

            will_take = int(clf.predict(features)[0])
            predicted_time = float(reg.predict(features)[0])

            return jsonify({
                "time_period": time_period,
                "will_take_medicine": bool(will_take),
                "predicted_time_minutes": predicted_time,
                "predicted_time_formatted": mins_to_time(predicted_time)
            })
        except Exception as e:
            return jsonify({"error": f"Prediction error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Request processing error: {str(e)}"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
