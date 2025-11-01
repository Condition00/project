from flask import Flask, request, jsonify
import joblib
import pandas as pd 

app = Flask(__name__)

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

def mins_to_time(m):
    h = int(m // 60)
    s = int(m % 60)
    return f"{h:02d}:{s:02d}"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Service is healthy"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    time_period = data.get("time_period", "").lower()
    if time_period not in models:
        return jsonify({"error": "Invalid time_period. Use morning, afternoon, or night."}), 400

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

if __name__ == '__main__':
    app.run(debug=True)
