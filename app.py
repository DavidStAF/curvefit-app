from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.optimize import curve_fit
import plotly.graph_objs as go
import plotly.io as pio
import sympy as sp

app = Flask(__name__)

def parse_function(expr):
    x = sp.symbols('x')
    params = sorted(list(sp.sympify(expr).free_symbols - {x}), key=lambda s: s.name)
    func = sp.lambdify((x, *params), expr, "numpy")
    return func, [str(p) for p in params]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fit", methods=["POST"])
def fit():
    try:
        data = request.json

        x = np.array(data["x"], dtype=float)
        y = np.array(data["y"], dtype=float)

        if len(x) != len(y):
            return jsonify({"error": "x and y must have same length"}), 400

        expr_string = data["model"]

        func, param_names = parse_function(expr_string)

        def wrapper(x, *params):
            return func(x, *params)

        popt, pcov = curve_fit(wrapper, x, y, maxfev=10000)
        perr = np.sqrt(np.diag(pcov))

        x_fit = np.linspace(min(x), max(x), 500)
        y_fit = wrapper(x_fit, *popt)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Data'))
        fig.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines', name='Fit'))

        graphJSON = pio.to_json(fig)

        return jsonify({
            "parameters": [
                {"name": name, "value": float(val), "uncertainty": float(err)}
                for name, val, err in zip(param_names, popt, perr)
            ],
            "graph": graphJSON
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()