from openai import OpenAI
client=
OpenAI(api_key="YOUR_API_KEY")


from flask import Flask, render_template, request

app = Flask(__name__)

# ---------------- CALCULATION LOGIC ----------------

def calculate_all(age, weight_kg, cm_height, gender, activity_level, goal):

    m_height = cm_height / 100

    # BMI
    BMI = weight_kg / (m_height ** 2)

    if BMI < 18.5:
        r_BMI = "Underweight"
    elif BMI < 25:
        r_BMI = "Normal"
    else:
        r_BMI = "Overweight"

    # BMR
    if gender == "Male":
        r_BMR = 10 * weight_kg + 6.25 * cm_height - 5 * age + 5
    else:
        r_BMR = 10 * weight_kg + 6.25 * cm_height - 5 * age - 161

    # Activity factor
    if activity_level == "Lazy":
        f_activity = 1.2
    elif activity_level == "Normal":
        f_activity = 1.375
    else:
        f_activity = 1.9

    TDEE = r_BMR * f_activity

    # Goal calories
    if goal == "weight_loss":
        Cal = TDEE - 500
        Prot = weight_kg * 2
    elif goal == "weight_gain":
        Cal = TDEE + 300
        Prot = weight_kg * 1.8
    else:
        Cal = TDEE
        Prot = weight_kg * 1.4

    Fat_Cal = Cal * 0.25
    Fat = Fat_Cal / 9
    Carbs = (Cal - (Prot * 4 + Fat_Cal)) / 4

    return BMI, r_BMI, r_BMR, TDEE, Cal, Prot, Fat, Carbs


# ---------------- DIET PLAN (SIMPLE TEXT) ----------------

def generate_diet_plan(Cal, Prot, Fat, Carbs, goal):

    return f"""
DAILY DIET PLAN

Calories: {Cal:.0f} kcal
Protein: {Prot:.0f} g
Fat: {Fat:.0f} g
Carbs: {Carbs:.0f} g

Goal: {goal}

Food Suggestions:
- Breakfast: Eggs, milk, oats, banana
- Lunch: Rice, chicken/daal, vegetables
- Snack: Fruits, yogurt
- Dinner: Roti, protein source, salad

Drink 2–3 liters of water daily.
Sleep 7–8 hours.
"""


# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        age = int(request.form["age"])
        weight = float(request.form["weight"])
        weight_unit = request.form["weight_unit"]
        height = float(request.form["height"])
        height_unit = request.form["height_unit"]
        gender = request.form["gender"]
        activity = request.form["activity"]
        goal = request.form["goal"]

        # convert weight
        if weight_unit == "pounds":
            weight_kg = weight / 2.20462
        else:
            weight_kg = weight

        # convert height
        if height_unit == "cm":
            cm_height = height
        elif height_unit == "feet":
            cm_height = height * 30.48
        else:
            cm_height = height * 100

        BMI, r_BMI, r_BMR, TDEE, Cal, Prot, Fat, Carbs = calculate_all(
            age, weight_kg, cm_height, gender, activity, goal
        )

       def generate_diet_plan(BMI, goal, Cal, Prot, Fat, Carbs):

    prompt = f"""
You are a professional nutritionist.

Create a simple diet plan:

BMI: {BMI}
Goal: {goal}
Calories: {Cal}
Protein: {Prot}
Fat: {Fat}
Carbs: {Carbs}

Make it simple and practical for Pakistan food.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a nutrition expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
