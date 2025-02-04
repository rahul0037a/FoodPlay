from flask import Flask, request, jsonify, render_template
from whitenoise import WhiteNoise
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import calculator_functions as cf
import helper_functions as hf
import os

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root="static/", prefix="static/")

food_items = pd.read_csv("food_items.csv")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/food_options")
def food_options():
    return jsonify(food_items["Food"].tolist())

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.json
        print("Received data:", data)
        gender = data["gender"]
        weight = int(data["weight"])
        height = int(data["height"])
        age = int(data["age"])

        if age < 19:
            return jsonify({"error": "Age must be 19 or older"}), 400
        if age > 100:
            return jsonify({"error": "Age must be 100 or younger"}), 400

        activity_multiplier = float(data.get("activity", 1.2))  # Derived from sport
        goal = data["goal"]

        bmr = cf.bmr(gender, weight, height, age)
        tdee = cf.tdee(bmr, activity_multiplier)
        daily_caloric_intake = {
            "cutting": 0.75 * tdee,
            "bulking": 1.10 * tdee,
            "maintaining": tdee,
        }.get(goal, tdee)

        protein, carbohydrates, fats, fibre, saturated_fats = cf.macros(
            int(daily_caloric_intake), goal
        )

        result = {
            "bmr": bmr,
            "tdee": tdee,
            "daily_caloric_intake": int(daily_caloric_intake),
            "protein": protein,
            "carbohydrates": carbohydrates,
            "fats": fats,
            "fibre": fibre,
            "saturated_fats": saturated_fats,
        }
        print("Calculated result:", result)
        return jsonify(result)
    except Exception as e:
        app.logger.error("Error occurred: %s", str(e))
        return jsonify({"error": "An internal error has occurred."}), 400

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.json
    selected_foods = data["selected_foods"]
    nutrient_goals = data["nutrient_goals"]

    age = int(data["age"])
    if age < 19:
        return jsonify({"error": "Age must be 19 or older"}), 400
    if age > 100:
        return jsonify({"error": "Age must be 100 or younger"}), 400
    gender = data["gender"]

    selected_food_items = food_items[food_items["Food"].isin(selected_foods)]

    c = selected_food_items["Price"].values

    A_ub = []
    b_ub = []

    nutrients = ["Protein", "Carbohydrates", "Fats", "Fibre", "Saturated Fats"]
    for nutrient in nutrients:
        column_name = f"{nutrient} (g)"
        if column_name in selected_food_items.columns:
            nutrient_key = nutrient.lower().replace(" ", "_")
            if nutrient_key in nutrient_goals:
                A_ub.extend(
                    [
                        -selected_food_items[column_name].values,
                        selected_food_items[column_name].values,
                    ]
                )
                b_ub.extend(
                    [-nutrient_goals[nutrient_key], nutrient_goals[nutrient_key] * 1.01]
                )

    nutrients_data = hf.create_nutrients_df()
    nutrient_bounds = cf.nutrient_bounds(age, gender)

    for nutrient in nutrients_data.columns[1:]:
        if nutrient.endswith("_RDA"):
            base_nutrient = nutrient[:-4]
            if base_nutrient in selected_food_items.columns:
                A_ub.append(-selected_food_items[base_nutrient].values)
                b_ub.append(-nutrient_bounds[nutrient])
        elif nutrient.endswith("_UL"):
            base_nutrient = nutrient[:-3]
            if base_nutrient in selected_food_items.columns:
                A_ub.append(selected_food_items[base_nutrient].values)
                b_ub.append(nutrient_bounds[nutrient])

    A_ub = np.array(A_ub)
    b_ub = np.array(b_ub)

    bounds = [(0, None) for _ in range(len(selected_food_items))]

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    if result.success:
        servings = np.round(result.x, 1)
        quantity = np.round(servings * selected_food_items["Serving (g)"], 1)
        total_cost_per_item = np.round(servings * selected_food_items["Price"], 2)

        nutrient_totals = {}
        for nutrient in selected_food_items.columns[3:]:
            nutrient_totals[nutrient] = np.round(
                np.sum(servings * selected_food_items[nutrient]), 1
            )

        result_data = {
            "food_items": selected_food_items["Food"].tolist(),
            "servings": servings.tolist(),
            "quantity": quantity.tolist(),
            "total_cost": total_cost_per_item.tolist(),
            "nutrient_totals": nutrient_totals,
            "total_cost_sum": np.sum(total_cost_per_item),
        }

        return jsonify({"success": True, "result": result_data})
    else:
        return jsonify(
            {
                "success": False,
                "message": "Optimization failed! No feasible solution found.",
            }
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
