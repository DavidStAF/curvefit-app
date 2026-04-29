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

        title = data.get("title", "Curve Fit")
        xlabel = data.get("xlabel", "X")
        ylabel = data.get("ylabel", "Y")
        
        x = np.array(data["x"], dtype=float)
        y = np.array(data["y"], dtype=float)
        expr_string = data["model"]
        expr_string = expr_string.replace("^", "**")
        
        x_sym = sp.symbols('x')
        expr = sp.sympify(expr_string)
        
        params = sorted(
            list(expr.free_symbols - {x_sym}),
            key=lambda s: s.name
        )
        
        param_names = [str(p) for p in params]
        
        func = sp.lambdify((x_sym, *params), expr, "numpy")

            # 👉 SI aucun paramètre trouvé → erreur claire
        if len(params) == 0:
            return jsonify({"error": "No parameters found in model (use a, b, c, ... variables)"}), 400
        
        def wrapper(x, *p):
            return np.array(func(x, *p), dtype=float)
        
        initial_guess = np.ones(len(params))
        
        popt, pcov = curve_fit(wrapper, x, y, p0=initial_guess, maxfev=10000)
        perr = np.sqrt(np.diag(pcov))
        
        x_fit = np.linspace(min(x), max(x), 500)
        y_fit = wrapper(x_fit, *popt)
       
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Data'))
        fig.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines', name='Fit'))
        fig.update_layout(title=title,xaxis_title=xlabel,yaxis_title=ylabel,template="plotly_white")
        
        return jsonify({
            "parameters": [
                {"name": name, "value": float(val), "uncertainty": float(err)}
                for name, val, err in zip(param_names, popt, perr)
            ],
            "graph": fig.to_plotly_json()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
if __name__ == "__main__":
    app.run()
