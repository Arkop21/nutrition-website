from flask import Flask, render_template, request
import ollama

app = Flask(__name__)

# ---------------- CALCULATIONS ----------------

def calculate(age, w, w_unit, h, h_unit, gender, activity, goal):

    # weight
    if w_unit == "kg":
        weight_kg = w
    else:
        weight_kg = w / 2.20462

    # height
    if h_unit == "cm":
        cm_height = h
    elif h_unit == "f":
        cm_height = h * 30.48
    else:
        cm_height = h * 100

    m_height = cm_height / 100

    # BMI
    bmi = weight_kg / (m_height ** 2)

    if bmi < 18.5:
        r_bmi = "Underweight"
    elif bmi < 25:
        r_bmi = "Normal"
    else:
        r_bmi = "Overweight"

    # BMR
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * cm_height - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * cm_height - 5 * age - 161

    # activity
    if activity == "lazy":
        factor = 1.2
    elif activity == "normal":
        factor = 1.375
    else:
        factor = 1.9

    tdee = bmr * factor

    # goal
    if goal == "loss":
        cal = tdee - 500
        prot = weight_kg * 2
    elif goal == "gain":
        cal = tdee + 300
        prot = weight_kg * 1.8
    else:
        cal = tdee
        prot = weight_kg * 1.4

    fat = (cal * 0.25) / 9
    carbs = (cal - (prot * 4 + cal * 0.25)) / 4

    return bmi, r_bmi, bmr, tdee, cal, prot, fat, carbs


# ---------------- AI DIET ----------------

def diet_plan(bmi, goal, cal, prot, fat, carbs):

    prompt = f"""
Create diet plan:

BMI: {bmi}
Goal: {goal}
Calories: {cal}
Protein: {prot}
Fat: {fat}
Carbs: {carbs}
"""

    response = ollama.chat(
        model="llama3:latest",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/result", methods=["POST"])
def result():

    age = int(request.form["age"])
    w = float(request.form["weight"])
    w_unit = request.form["w_unit"]
    h = float(request.form["height"])
    h_unit = request.form["h_unit"]
    gender = request.form["gender"]
    activity = request.form["activity"]
    goal = request.form["goal"]

    bmi, r_bmi, bmr, tdee, cal, prot, fat, carbs = calculate(
        age, w, w_unit, h, h_unit, gender, activity, goal
    )

    diet = diet_plan(bmi, goal, cal, prot, fat, carbs)

    return render_template(
        "result.html",
        bmi=bmi,
        r_bmi=r_bmi,
        bmr=bmr,
        tdee=tdee,
        cal=cal,
        prot=prot,
        fat=fat,
        carbs=carbs,
        diet=diet
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
