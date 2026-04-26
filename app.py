from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# ---------------- CALCULATION ----------------

def calculate(age, weight_kg, cm_height, gender, activity, goal):

    m_height = cm_height / 100
    BMI = weight_kg / (m_height ** 2)

    if BMI < 18.5:
        status = "Underweight"
    elif BMI < 25:
        status = "Normal"
    else:
        status = "Overweight"

    if gender == "Male":
        BMR = 10 * weight_kg + 6.25 * cm_height - 5 * age + 5
    else:
        BMR = 10 * weight_kg + 6.25 * cm_height - 5 * age - 161

    if activity == "Lazy":
        factor = 1.2
    elif activity == "Normal":
        factor = 1.375
    else:
        factor = 1.9

    TDEE = BMR * factor

    if goal == "weight_loss":
        Cal = TDEE - 500
        Prot = weight_kg * 2
    elif goal == "weight_gain":
        Cal = TDEE + 300
        Prot = weight_kg * 1.8
    else:
        Cal = TDEE
        Prot = weight_kg * 1.4

    Fat = (Cal * 0.25) / 9
    Carbs = (Cal - (Prot * 4 + (Cal * 0.25))) / 4

    return BMI, status, BMR, TDEE, Cal, Prot, Fat, Carbs


# ---------------- FREE AI (GROQ) ----------------

def generate_ai_plan(BMI, goal, Cal, Prot, Fat, Carbs):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "AI not configured. Please set GROQ_API_KEY."

    prompt = f"""
You are a nutrition expert.

Create a simple Pakistani diet plan.

BMI: {BMI}
Goal: {goal}
Calories: {Cal}
Protein: {Prot}
Fat: {Fat}
Carbs: {Carbs}

Make it practical and short.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    return response.json()["choices"][0]["message"]["content"]


# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        age = int(request.form["age"])
        weight = float(request.form["weight"])
        height = float(request.form["height"])

        weight_unit = request.form["weight_unit"]
        height_unit = request.form["height_unit"]

        gender = request.form["gender"]
        activity = request.form["activity"]
        goal = request.form["goal"]

        if weight_unit == "pounds":
            weight = weight / 2.20462

        if height_unit == "feet":
            height = height * 30.48
        elif height_unit == "m":
            height = height * 100

        BMI, status, BMR, TDEE, Cal, Prot, Fat, Carbs = calculate(
            age, weight, height, gender, activity, goal
        )
def generate_ai_plan(BMI, goal, Cal, Prot, Fat, Carbs):

    import requests
    import os

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "ERROR: Missing API key"

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "user",
                "content": f"""
Create a diet plan:

BMI: {BMI}
Goal: {goal}
Calories: {Cal}
Protein: {Prot}
Fat: {Fat}
Carbs: {Carbs}
"""
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # 🛡️ SAFE CHECK (IMPORTANT)
    if response.status_code != 200:
        return f"AI ERROR: {response.text}"

    result = response.json()

    # extra safety check
    if "choices" not in result:
        return f"Unexpected response: {result}"

    return result["choices"][0]["message"]["content"]
    if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
