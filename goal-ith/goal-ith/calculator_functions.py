import pandas as pd
import helper_functions as hf


def bmr(gender: str, weight: float, height: float, age: int) -> int:
    """
    Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.

    Parameters:
        gender (str): The gender of the individual ('m' for male, 'f' for female).
        weight (float): The weight of the individual in kilograms.
        height (float): The height of the individual in centimeters.
        age (int): The age of the individual in years.

    Returns:
        int: The estimated Basal Metabolic Rate in calories per day.

    Raises:
        ValueError: If the gender is not 'm' or 'f'.
    """
    if gender.lower() == "m":
        return int(10 * weight + 6.25 * height - 5 * age + 5)
    elif gender.lower() == "f":
        return int(10 * weight + 6.25 * height - 5 * age - 161)
    else:
        raise ValueError("Gender must be 'm' or 'f'.")


def tdee(bmr: int, activity_multiplier: float) -> int:
    """
    Calculate Total Daily Energy Expenditure (TDEE).

    Parameters:
        bmr (int): Basal Metabolic Rate calculated using the bmr function.
        activity_multiplier (float): A multiplier based on the individual's activity level.

    Returns:
        int: The estimated Total Daily Energy Expenditure in calories per day.
    """
    return int(bmr * activity_multiplier)


def macros(daily_caloric_intake: float, goal: str) -> tuple[int, int, int, int, int]:
    """
    Calculate daily intake of protein, carbohydrates, and fats based on the goal.

    Parameters:
        daily_caloric_intake (float): The total daily caloric intake in calories.
        goal (str): The dietary goal ('cutting', 'bulking', or 'maintaining').

    Returns:
        tuple[int, int, int, int, int]: A tuple containing:
            - Protein intake in grams
            - Carbohydrate intake in grams
            - Fat intake in grams
            - Fiber intake in grams
            - Saturated fat intake in grams
    """
    if goal == "cutting":
        protein = int(0.40 * daily_caloric_intake / 4)
        carbohydrates = int(0.40 * daily_caloric_intake / 4)
        fats = int(0.20 * daily_caloric_intake / 9)
    elif goal == "bulking":
        protein = int(0.25 * daily_caloric_intake / 4)
        carbohydrates = int(0.55 * daily_caloric_intake / 4)
        fats = int(0.20 * daily_caloric_intake / 9)
    elif goal == "maintaining":
        protein = int(0.30 * daily_caloric_intake / 4)
        carbohydrates = int(0.45 * daily_caloric_intake / 4)
        fats = int(0.25 * daily_caloric_intake / 9)
    else:
        raise ValueError("Goal must be 'cutting', 'bulking', or 'maintaining'.")

    fibre = int(0.014 * daily_caloric_intake)
    saturated_fats = int(0.10 * daily_caloric_intake / 9)

    return protein, carbohydrates, fats, fibre, saturated_fats


def nutrient_bounds(age: int, gender: str) -> pd.Series:
    """
    Get the Recommended Dietary Allowance (RDA) and Tolerable Upper Intake Level (UL)
    for each nutrient based on age and gender.

    Parameters:
        age (int): The age of the individual in years.
        gender (str): The gender of the individual ('m' for male, 'f' for female).

    Returns:
        pd.Series: A Series containing the RDA and UL values for each nutrient
        for the specified age group and gender.

    Raises:
        ValueError: If no nutrient data is found for the specified age group.
    """
    nutrients_data = hf.create_nutrients_df()

    if gender.lower() == "m":
        gender_prefix = "Males"
    else:
        gender_prefix = "Females"

    if age <= 3:
        age_group = "Children 1-3 y"
    elif 4 <= age <= 8:
        age_group = "Children 4-8 y"
    elif 9 <= age <= 13:
        age_group = f"{gender_prefix} 9-13 y"
    elif 14 <= age <= 18:
        age_group = f"{gender_prefix} 14-18 y"
    elif 19 <= age <= 30:
        age_group = f"{gender_prefix} 19-30 y"
    elif 31 <= age <= 50:
        age_group = f"{gender_prefix} 31-50 y"
    elif 51 <= age <= 70:
        age_group = f"{gender_prefix} 51-70 y"
    else:
        age_group = f"{gender_prefix} > 70 y"

    nutrient_bounds = nutrients_data[nutrients_data["Life-Stage Group"] == age_group]

    if nutrient_bounds.empty:
        raise ValueError(f"No nutrient data found for age group: {age_group}")

    return nutrient_bounds.iloc[0]
