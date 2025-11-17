from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from polynomial_dsa import solve_expression  # use the wrapper we added

app = Flask(__name__, static_folder='.')
CORS(app)  # allow cross-origin requests

# --- Serve frontend files ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# --- API Endpoint ---
@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.json
        operation = data.get("operation")
        poly1_str = data.get("poly1", "")
        poly2_str = data.get("poly2", "")
        eval_point = data.get("evalPoint", None)

        # --- Use solve_expression wrapper ---
        if operation in ["add", "subtract", "multiply", "divide"]:
            # Binary operations require poly2
            from polynomial_dsa import parse_string_to_poly
            p1 = parse_string_to_poly(poly1_str)
            p2 = parse_string_to_poly(poly2_str)
            if operation == "add":
                result = p1.add(p2).to_string()
            elif operation == "subtract":
                result = p1.subtract(p2).to_string()
            elif operation == "multiply":
                result = p1.multiply(p2).to_string()
            elif operation == "divide":
                q, r = p1.divide(p2)
                result = f"Quotient: {q.to_string()}\nRemainder: {r.to_string()}"
        else:
            # Single polynomial operations
            value = float(eval_point) if eval_point else None
            result = solve_expression(poly1_str, operation=operation, value=value)

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"result": f"Server Error: {e}"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=8080)
