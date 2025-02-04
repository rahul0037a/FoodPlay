// 1️⃣ Add sport-to-multiplier mapping
const sportActivityMultipliers = {
  "Cricket - Batsman": 1.88,
  "Cricket - Bowler (Fast)": 2.1,
  "Cricket - Bowler (Spin)": 1.9,
  "Cricket - Wicketkeeper": 2.1,
  "Cricket - Fielder": 1.75,
  "Football - Goalkeeper": 1.7,
  "Football - Defender": 2.1,
  "Football - Midfielder": 2.45,
  "Football - Forward/Striker": 2.35,
  "Field Hockey - Goalkeeper": 1.8,
  "Field Hockey - Defender": 2.15,
  "Field Hockey - Midfielder": 2.45,
  "Field Hockey - Forward": 2.35,
  "Kabaddi - Raider": 2.55,
  "Kabaddi - Defender": 2.35,
  "Badminton - Singles": 2.45,
  "Badminton - Doubles": 2.15,
  "Kho-Kho - Attacker (Chaser)": 2.55,
  "Kho-Kho - Defender (Dodger)": 2.4,
  "Tennis - Singles": 2.35,
  "Tennis - Doubles": 2.15,
  "Athletics - Sprinter": 2.6,
  "Athletics - Middle-Distance": 2.45,
  "Athletics - Long-Distance": 2.7,
  "Athletics - Field Events": 2.15
};
function displayResults(result) {
  if (result.error) {
    alert(result.error);
    return;
  }

  document.getElementById("bmr-result").textContent = `${result.bmr} kcal`;
  document.getElementById("tdee-result").textContent = `${result.tdee} kcal`;
  document.getElementById("calorie-result").textContent = `${result.daily_caloric_intake} kcal`;

  // Add these new fields dynamically
  const resultsContainer = document.getElementById("results");

  // Clear previous nutrient data if any
  const existingNutrients = document.querySelector("#nutrients-info");
  if (existingNutrients) {
    existingNutrients.remove();
  }

  const nutrientDiv = document.createElement("div");
  nutrientDiv.id = "nutrients-info";
  nutrientDiv.className = "grid grid-cols-1 md:grid-cols-3 gap-4 mt-4";

  const nutrients = [
    { label: "Protein", value: result.protein, unit: "g" },
    { label: "Carbohydrates", value: result.carbohydrates, unit: "g" },
    { label: "Fats", value: result.fats, unit: "g" },
    { label: "Fibre", value: result.fibre, unit: "g" },
    { label: "Saturated Fats", value: result.saturated_fats, unit: "g" }
  ];

  nutrients.forEach(nutrient => {
    const card = document.createElement("div");
    card.className = "bg-gray-100 p-4 rounded-md";
    card.innerHTML = `
      <h3 class="font-semibold text-gray-700">${nutrient.label}</h3>
      <p class="text-2xl font-bold text-green-600">${nutrient.value} ${nutrient.unit}</p>
    `;
    nutrientDiv.appendChild(card);
  });

  resultsContainer.appendChild(nutrientDiv);
  resultsContainer.classList.remove("hidden");
}

function loadFoodOptions() {
  fetch("/food_options")
    .then(response => response.json())
    .then(foods => {
      console.log("Available Food Options:", foods);
      // You can add code here to dynamically display the food options in the UI
    })
    .catch(error => console.error("Error loading food options:", error));
}

// 2️⃣ Replace activity level dropdown with sport selection
document.addEventListener("DOMContentLoaded", () => {
  const personalInfoForm = document.getElementById("personal-info-form");
  const sportSelect = document.getElementById("sport"); // Use the existing select

  // Populate the existing sport select dropdown
  for (const sport in sportActivityMultipliers) {
    const option = document.createElement("option");
    option.value = sport;
    option.textContent = sport;
    sportSelect.appendChild(option);
  }

  // Adjust form submission to include derived multiplier
  personalInfoForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(personalInfoForm);
    const data = Object.fromEntries(formData.entries());

    const selectedSport = data.sport;
    data.activity = sportActivityMultipliers[selectedSport] || 1.2; // Fallback to 1.2

    fetch("/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
      .then((response) => response.json())
      .then((result) => {
        displayResults(result);
        loadFoodOptions();
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while processing your request. Check the console for details.");
      });
  });
});
