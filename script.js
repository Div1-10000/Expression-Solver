document.addEventListener("DOMContentLoaded", () => {

  // --- Get DOM Elements ---
  const operationSelect = document.getElementById("operation");

  const poly1Input = document.getElementById("poly1");
  const poly2Input = document.getElementById("poly2");
  const evalPointInput = document.getElementById("evalPoint");

  const poly2Label = document.querySelector("label[for='poly2']");
  const evalPointLabel = document.querySelector("label[for='evalPoint']");

  const computeBtn = document.getElementById("compute-btn");
  const resetBtn = document.getElementById("reset-btn");

  const resultTextarea = document.getElementById("result");

  // --- Updated API URL for Flask ---
  const API_URL = "/calculate"; // relative path; works locally and when deployed

  // --- Dynamic UI Logic ---
  function updateFormUI() {
    const operation = operationSelect.value;

    // Hide poly2 and evalPoint by default
    poly2Input.classList.add("hidden");
    poly2Label.classList.add("hidden");
    evalPointInput.classList.add("hidden");
    evalPointLabel.classList.add("hidden");

    // Show Poly B only for operations that need it
    if (["add", "subtract", "multiply", "divide", "derivativeB", "integralB", "evaluateB"].includes(operation)) {
      poly2Input.classList.remove("hidden");
      poly2Label.classList.remove("hidden");
    }

    // Show Eval Point for evaluate operations
    if (operation === "evaluateA" || operation === "evaluateB") {
      evalPointInput.classList.remove("hidden");
      evalPointLabel.classList.remove("hidden");
    }
  }

  // --- Event Listeners ---
  operationSelect.addEventListener("change", updateFormUI);

  computeBtn.addEventListener("click", async () => {
    const operation = operationSelect.value;

    const payload = { operation, poly1: poly1Input.value.trim() };

    if (!poly2Input.classList.contains("hidden")) payload.poly2 = poly2Input.value.trim();
    if (!evalPointInput.classList.contains("hidden")) payload.evalPoint = evalPointInput.value.trim();

    resultTextarea.value = "Calculating...";

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`Server returned ${response.status}`);

      const data = await response.json();

      resultTextarea.value = data.result || "No result returned from server.";

    } catch (error) {
      console.error("Error:", error);
      resultTextarea.value = "Error: Could not connect to the calculation server.";
    }
  });

  resetBtn.addEventListener("click", () => {
    poly1Input.value = "";
    poly2Input.value = "";
    evalPointInput.value = "";
    resultTextarea.value = "";
    operationSelect.selectedIndex = 0;
    updateFormUI();
  });

  // --- Initial Setup ---
  updateFormUI();
});
