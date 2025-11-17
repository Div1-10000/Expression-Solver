from flask import Flask, request, jsonify
from flask_cors import CORS
# Import the Polynomial class and parser function
from polynomial_dsa import Polynomial, parse_string_to_poly

# --- 1. Setup the Server ---
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your frontend

# --- 2. API Endpoint ---
@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.json
        operation = data.get("operation")
        
        poly1_str = data.get("poly1", "")
        poly2_str = data.get("poly2", "")
        x_val_str = data.get("evalPoint", "0")

        # --- 3. Parse polynomials ---
        poly1 = parse_string_to_poly(poly1_str)
        poly2 = parse_string_to_poly(poly2_str)
        
        try:
            x_val = float(x_val_str) if x_val_str else 0.0
        except ValueError:
            x_val = 0.0

        result = ""

        # --- 4. Perform the selected operation ---
        if operation == "add":
            result = poly1.add(poly2).to_string()
        elif operation == "subtract":
            result = poly1.subtract(poly2).to_string()
        elif operation == "multiply":
            result = poly1.multiply(poly2).to_string()
        elif operation == "divide":
            q, r = poly1.divide(poly2)
            result = f"Quotient: {q.to_string()}\nRemainder: {r.to_string()}"
        elif operation == "derivativeA":
            result = poly1.differentiate().to_string()
        elif operation == "derivativeB":
            result = poly2.differentiate().to_string()
        elif operation == "integralA":
            result = poly1.integrate().to_string(constant_term=" + C")
        elif operation == "integralB":
            result = poly2.integrate().to_string(constant_term=" + C")
        elif operation == "evaluateA":
            result = f"{poly1.evaluate(x_val):.4f}"
        elif operation == "evaluateB":
            result = f"{poly2.evaluate(x_val):.4f}"
        else:
            result = "Error: Operation not recognized"

        return jsonify({"result": result})

    except Exception as e:
        app.logger.error(f"Error during calculation: {e}")
        if "division by zero" in str(e).lower():
            return jsonify({"result": "Error: Cannot divide by zero."}), 400
        return jsonify({"result": f"Server Error: {str(e)}"}), 400

# --- 5. Run the server ---
if __name__ == "__main__":
    app.run(debug=True, port=8080)
