import csv
import re
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sympy as sp

from methods.bisection import bisection
from methods.false_position import false_position
from methods.secant import secant
from methods.newton_raphson import newton_raphson
from methods.simple_fixed_point_iteration import simple_fixed_point_iteration

from plot_methods.graph_bisection import plot_bisection_method
from plot_methods.graph_false_position import plot_false_position_method
from plot_methods.graph_newton_raphson import plot_newton_raphson_method
from plot_methods.graph_secant import plot_secant_method
from plot_methods.graph_simple_fixed_point_iteration import plot_simple_fixed_point_iteration

pattern = r'(\d+)[xX]'
number_pattern = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
BRACKET_METHODS = {"Bisection", "False Position", "Secant"}

METHOD_RUNNERS = {
    "Bisection": lambda f, a, b, tolerance, max_iterations: bisection(f, a, b, tolerance, max_iterations),
    "False Position": lambda f, a, b, tolerance, max_iterations: false_position(f, a, b, tolerance, max_iterations),
    "Secant": lambda f, a, b, tolerance, max_iterations: secant(f, a, b, tolerance, max_iterations),
    "Newton-Raphson": lambda f, a, b, tolerance, max_iterations: newton_raphson(f, a, tolerance, max_iterations),
    "Simple Fixed-Point Iteration": lambda f, a, b, tolerance, max_iterations: simple_fixed_point_iteration(f, a, tolerance, max_iterations),
}

def replace(match):
    return match.group(1) + '*x'

def fields_error(result_label, error_label, info_label):
    result_label.config(text="Please fill all the fields", fg="red")
    error_label.config(text="")
    info_label.config(text="")

def is_checked(check_var):
    return check_var.get() == 1

def clear_results(result_label, error_label, info_label):
    result_label.config(text="--", fg="#334155")
    error_label.config(text="Waiting", fg="#64748b")
    info_label.config(text="Enter values and run a method.", fg="#64748b")

def show_steps(steps_text, msg, root, clear_var):
    if is_checked(clear_var) and hasattr(root, 'steps_window'):
        root.steps_window.destroy()

    steps_window = tk.Toplevel(root)
    steps_window.title("Steps of Iteration")
    steps_window.geometry("720x480")
    steps_window.configure(bg="#f8fafc")

    header = tk.Frame(steps_window, bg="#1d4ed8", padx=18, pady=14)
    header.pack(fill="x")

    Label(header, text="Iteration Details", justify=LEFT, bg="#1d4ed8", fg="white",
          font=("Segoe UI", 13, "bold")).pack(anchor="w")
    Label(header, text=msg, justify=LEFT, bg="#1d4ed8", fg="#dbeafe",
          font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))

    body = tk.Frame(steps_window, bg="#f8fafc", padx=18, pady=18)
    body.pack(fill="both", expand=True)

    text = tk.Text(body, wrap="none", bg="#f8fafc", fg="#0f172a", relief="flat", font=("Consolas", 10))
    scrollbar = tk.Scrollbar(body, orient="vertical", command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)
    text.insert("1.0", steps_text)
    text.configure(state="disabled")
    text.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.steps_window = steps_window


def _parse_inputs(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry):
    method = method_var.get()
    user_entry = expression_entry.get().strip()
    if not user_entry:
        raise ValueError("Please enter an equation.")

    tolerance = float(tolerance_entry.get())
    max_iterations = int(max_iterations_entry.get())
    if tolerance <= 0:
        raise ValueError("Tolerance must be positive.")
    if max_iterations <= 0:
        raise ValueError("Max iterations must be greater than 0.")

    a = float(a_entry.get())
    if method in ["Bisection", "False Position", "Secant"]:
        b = float(b_entry.get())
    else:
        b = a

    equation = user_entry.replace("^", "**")
    modified_input = re.sub(pattern, replace, equation)
    x = sp.symbols('x')
    expr = sp.sympify(modified_input, locals={
        'x': x,
        'sin': sp.sin,
        'cos': sp.cos,
        'tan': sp.tan,
        'log': sp.log,
        'exp': sp.exp
    })

    f_lambdified = sp.lambdify(x, expr, "math")

    def f(val):
        return f_lambdified(val)

    return {
        "method": method,
        "tolerance": tolerance,
        "max_iterations": max_iterations,
        "a": a,
        "b": b,
        "f": f,
    }


def _run_method(method, f, a, b, tolerance, max_iterations):
    result, error, msg, steps_text = METHOD_RUNNERS[method](f, a, b, tolerance, max_iterations)
    return result, error, msg, steps_text


def _set_result_state(result_label, error_label, info_label, result, error=None, message=None, success=None):
    if isinstance(result, dict):
        run = result
        result = run.get("result")
        error = run.get("error")
        message = run.get("message")
        success = run.get("success")

    if success:
        result_label.config(text=f"{result:.6f}", fg="#15803d")
        error_label.config(text=f"{error:.6f}", fg="#b45309")
        info_label.config(text=message, fg="#334155")
    else:
        result_label.config(text="No solution", fg="#b91c1c")
        error_label.config(text="Failed", fg="#b91c1c")
        info_label.config(text=message, fg="#7f1d1d")


def show_comparison(root, method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry):
    try:
        data = _parse_inputs(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry)
    except Exception as e:
        popup = tk.Toplevel(root)
        popup.title("Comparison Error")
        popup.geometry("440x180")
        popup.configure(bg="#fff7ed")
        tk.Label(popup, text="Method Comparison", bg="#fff7ed", fg="#9a3412",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(18, 8))
        tk.Label(popup, text=str(e), bg="#fff7ed", fg="#7c2d12",
                 font=("Segoe UI", 10), wraplength=380, justify="left").pack(anchor="w", padx=20)
        return

    runs = []
    for method in METHOD_RUNNERS:
        try:
            run_b = data["b"] if method in ["Bisection", "False Position", "Secant"] else data["a"]
            result, error, msg, _steps_text = _run_method(
                method, data["f"], data["a"], run_b, data["tolerance"], data["max_iterations"]
            )
            runs.append({"method": method, "result": result, "error": error, "message": msg})
        except Exception as e:
            runs.append({"method": method, "result": None, "error": None, "message": f"Execution error: {e}"})

    successful = [item for item in runs if item["result"] is not None and item["error"] is not None]
    successful.sort(key=lambda item: item["error"])
    ordered = successful + [item for item in runs if item not in successful]

    popup = tk.Toplevel(root)
    popup.title("Method Comparison Lab")
    popup.geometry("880x560")
    popup.configure(bg="#f8fafc")

    header = tk.Frame(popup, bg="#0f766e", padx=18, pady=16)
    header.pack(fill="x")
    tk.Label(header, text="Method Comparison Lab", bg="#0f766e", fg="white",
             font=("Segoe UI", 15, "bold")).pack(anchor="w")

    subtitle = "No method converged with the current settings."
    if successful:
        subtitle = f"Best residual: {successful[0]['method']} with error {successful[0]['error']:.6f}"
    tk.Label(header, text=subtitle, bg="#0f766e", fg="#ccfbf1",
             font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))

    body = tk.Frame(popup, bg="#f8fafc", padx=18, pady=18)
    body.pack(fill="both", expand=True)

    canvas = tk.Canvas(body, bg="#f8fafc", highlightthickness=0)
    scroll = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
    list_frame = tk.Frame(canvas, bg="#f8fafc")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    canvas.create_window((0, 0), window=list_frame, anchor="nw")
    list_frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))

    for index, item in enumerate(ordered, start=1):
        bg = "#ecfeff" if item["result"] is not None else "#fef2f2"
        card = tk.Frame(list_frame, bg=bg, padx=16, pady=16)
        card.pack(fill="x", pady=8)
        root_text = f"{item['result']:.6f}" if item["result"] is not None else "--"
        error_text = f"{item['error']:.6f}" if item["error"] is not None else "--"
        status = "Converged" if item["result"] is not None else "Did not converge"
        tk.Label(card, text=f"{index}. {item['method']}", bg=bg, fg="#0f172a",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(card, text=f"Status: {status}    Root: {root_text}    Error: {error_text}",
                 bg=bg, fg="#334155", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 4))
        tk.Label(card, text=item["message"], bg=bg, fg="#475569",
                 font=("Segoe UI", 10), wraplength=760, justify="left").pack(anchor="w")


def calculate_root(root, method_var, expression_entry, tolerance_entry,
                   max_iterations_entry, a_entry, b_entry,
                   result_label, error_label, info_label,
                   check_var, plot_var, clear_var):

    try:
        method = method_var.get()
        user_entry = expression_entry.get()
        tolerance = float(tolerance_entry.get())
        max_iterations = int(max_iterations_entry.get())

        if not user_entry:
            raise Exception("Please enter an equation.")

        if tolerance <= 0:
            raise Exception("Tolerance must be positive.")

        if max_iterations <= 0:
            raise Exception("Max iterations must be greater than 0.")

    except Exception as e:
        result_label.config(text=f"Error: {e}", fg="red")
        return

    # 🔥 Convert input
    equation = user_entry.replace("^", "**")
    modified_input = re.sub(pattern, replace, equation)

    # 🔥 Create function using SymPy
    x = sp.symbols('x')

    try:
        expr = sp.sympify(modified_input, locals={
            'x': x,
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'log': sp.log,
            'exp': sp.exp
        })

        f_lambdified = sp.lambdify(x, expr, "math")

        def f(val):
            return f_lambdified(val)

    except Exception:
        result_label.config(text="Error: Invalid equation", fg="red")
        return

    # 🔥 Get inputs
    try:
        a = float(a_entry.get())
        if method in ["Bisection", "False Position", "Secant"]:
            b = float(b_entry.get())
        else:
            b = a
    except:
        result_label.config(text="Error: Invalid input values", fg="red")
        return

    # 🔥 Solve
    if method == "Bisection":
        result, error, msg, steps_text = bisection(f, a, b, tolerance, max_iterations)
    elif method == "False Position":
        result, error, msg, steps_text = false_position(f, a, b, tolerance, max_iterations)
    elif method == "Secant":
        result, error, msg, steps_text = secant(f, a, b, tolerance, max_iterations)
    elif method == "Newton-Raphson":
        result, error, msg, steps_text = newton_raphson(f, a, tolerance, max_iterations)
    else:
        result, error, msg, steps_text = simple_fixed_point_iteration(f, a, tolerance, max_iterations)

    # 🔥 Display result
    if result is None:
        result_label.config(text="No root found", fg="red")
        error_label.config(text=msg, fg="red")
    else:
        result_label.config(text=f"Root: {result:.6f}", fg="green")
        error_label.config(text=f"Error: {error:.6f}", fg="orange")
        info_label.config(text=msg)

        if is_checked(check_var):
            show_steps(steps_text, msg, root, clear_var)

        if is_checked(plot_var):
            if method == "Bisection":
                plot_bisection_method(f, a, b, max_iterations, tolerance)
            elif method == "False Position":
                plot_false_position_method(f, a, b, max_iterations, tolerance)
            elif method == "Secant":
                plot_secant_method(f, a, b, max_iterations, tolerance)
            elif method == "Newton-Raphson":
                plot_newton_raphson_method(f, a, max_iterations, tolerance)
            else:
                plot_simple_fixed_point_iteration(f, a, max_iterations, tolerance)


def calculate_root(root, method_var, expression_entry, tolerance_entry,
                   max_iterations_entry, a_entry, b_entry,
                   result_label, error_label, info_label,
                   check_var, plot_var, clear_var):
    try:
        data = _parse_inputs(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry)
    except Exception as e:
        _set_result_state(result_label, error_label, info_label, None, None, f"Input error: {e}", False)
        return

    result, error, msg, steps_text = _run_method(
        data["method"], data["f"], data["a"], data["b"], data["tolerance"], data["max_iterations"]
    )

    if result is None:
        _set_result_state(result_label, error_label, info_label, None, None, msg, False)
        return

    _set_result_state(result_label, error_label, info_label, result, error, msg, True)

    if is_checked(check_var):
        show_steps(steps_text, msg, root, clear_var)

    if is_checked(plot_var):
        if data["method"] == "Bisection":
            plot_bisection_method(data["f"], data["a"], data["b"], data["max_iterations"], data["tolerance"])
        elif data["method"] == "False Position":
            plot_false_position_method(data["f"], data["a"], data["b"], data["max_iterations"], data["tolerance"])
        elif data["method"] == "Secant":
            plot_secant_method(data["f"], data["a"], data["b"], data["max_iterations"], data["tolerance"])
        elif data["method"] == "Newton-Raphson":
            plot_newton_raphson_method(data["f"], data["a"], data["max_iterations"], data["tolerance"])
        else:
            plot_simple_fixed_point_iteration(data["f"], data["a"], data["max_iterations"], data["tolerance"])


def _enhanced_parse_inputs(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry):
    method = method_var.get()
    user_entry = expression_entry.get().strip()
    if not user_entry:
        raise ValueError("Please enter an equation.")

    tolerance = float(tolerance_entry.get())
    max_iterations = int(max_iterations_entry.get())
    if tolerance <= 0:
        raise ValueError("Tolerance must be positive.")
    if max_iterations <= 0:
        raise ValueError("Max iterations must be greater than 0.")

    a = float(a_entry.get())
    if method in BRACKET_METHODS:
        b = float(b_entry.get())
    else:
        b = a

    equation = user_entry.replace("^", "**")
    modified_input = re.sub(pattern, replace, equation)
    x = sp.symbols('x')
    expr = sp.sympify(modified_input, locals={
        'x': x,
        'sin': sp.sin,
        'cos': sp.cos,
        'tan': sp.tan,
        'log': sp.log,
        'exp': sp.exp
    })

    derivative_expr = sp.diff(expr, x)
    derivative_func = sp.lambdify(x, derivative_expr, "math")
    f_lambdified = sp.lambdify(x, expr, "math")

    def f(val):
        return f_lambdified(val)

    has_bracket = False
    if method in BRACKET_METHODS:
        try:
            has_bracket = f(a) * f(b) < 0
        except Exception:
            has_bracket = False

    return {
        "method": method,
        "equation": user_entry,
        "expr": expr,
        "derivative": derivative_expr,
        "derivative_func": derivative_func,
        "tolerance": tolerance,
        "max_iterations": max_iterations,
        "a": a,
        "b": b,
        "f": f,
        "has_bracket": has_bracket,
    }


def _extract_convergence_history(steps_text):
    history = []
    for raw_line in steps_text.splitlines():
        line = raw_line.strip()
        if not line or not line[0].isdigit():
            continue
        values = re.findall(number_pattern, line)
        if not values:
            continue
        try:
            history.append(abs(float(values[-1])))
        except ValueError:
            continue
    return history


def _diagnose_failure(method, message, success):
    lowered = message.lower()
    if success:
        return f"{method} converged successfully with the current setup."
    if "bracket" in lowered:
        return "The chosen interval does not bracket a root. Pick bounds where the function changes sign."
    if "derivative is zero" in lowered:
        return "Newton-Raphson stalled because the derivative was too small near the initial guess."
    if "zero division" in lowered:
        return "The update step divided by zero. Try different starting values or a bracket method."
    if "failed after" in lowered:
        return "The method reached the iteration limit before converging. Increase iterations or improve the guesses."
    return "The method did not converge with the current inputs. Adjust the interval, guesses, or tolerance."


def _recommend_method(data):
    scores = {
        "Bisection": 0,
        "False Position": 0,
        "Secant": 0,
        "Newton-Raphson": 0,
        "Simple Fixed-Point Iteration": 0,
    }

    if data["has_bracket"]:
        scores["Bisection"] += 4
        scores["False Position"] += 5
        scores["Secant"] += 2
    else:
        scores["Secant"] += 3
        scores["Newton-Raphson"] += 2

    if data["expr"].is_polynomial():
        scores["Newton-Raphson"] += 3
        scores["Secant"] += 2

    if data["expr"].has(sp.sin, sp.cos, sp.exp, sp.log):
        scores["Newton-Raphson"] += 2
        scores["Secant"] += 1

    try:
        slope = abs(float(data["derivative_func"](data["a"])))
        if slope > 1e-6:
            scores["Newton-Raphson"] += 3
        else:
            scores["Bisection"] += 1
            scores["False Position"] += 1
    except Exception:
        scores["Secant"] += 1

    scores["Simple Fixed-Point Iteration"] -= 1
    best_method = max(scores, key=scores.get)
    if best_method == data["method"]:
        return f"Good fit: {data['method']} matches the current equation profile and starting values."
    return f"Suggested method: {best_method}. It looks more suitable than {data['method']} for this setup."


def preview_recommendation(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry):
    data = _enhanced_parse_inputs(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry)
    return _recommend_method(data)


def show_convergence_dashboard(root):
    run = getattr(root, "last_run", None)
    if not run or not run.get("history"):
        messagebox.showinfo("Convergence Dashboard", "Run a calculation first to generate convergence data.")
        return

    plt.figure(figsize=(7, 4.5))
    plt.plot(range(1, len(run["history"]) + 1), run["history"], marker="o", color="#2563eb")
    plt.title(f"Convergence Dashboard - {run['method']}")
    plt.xlabel("Iteration")
    plt.ylabel("Residual / Error")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def export_results_csv(root):
    run = getattr(root, "last_run", None)
    comparison = getattr(root, "last_comparison", None)
    if not run and not comparison:
        messagebox.showinfo("Export CSV", "Run a calculation or comparison first.")
        return

    path = filedialog.asksaveasfilename(
        title="Export CSV",
        defaultextension=".csv",
        filetypes=[("CSV file", "*.csv")],
    )
    if not path:
        return

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if run:
            writer.writerow(["Current Run"])
            writer.writerow(["Equation", run["equation"]])
            writer.writerow(["Method", run["method"]])
            writer.writerow(["Root", run["result"]])
            writer.writerow(["Error", run["error"]])
            writer.writerow(["Status", "Success" if run["success"] else "Failed"])
            writer.writerow(["Message", run["message"]])
            writer.writerow(["Diagnosis", run["diagnosis"]])
            writer.writerow(["Recommendation", run["recommendation"]])
            writer.writerow([])

        if comparison:
            writer.writerow(["Method Comparison Lab"])
            writer.writerow(["Equation", comparison["equation"]])
            writer.writerow(["Method", "Status", "Root", "Error", "Message"])
            for item in comparison["runs"]:
                writer.writerow([
                    item["method"],
                    "Success" if item["success"] else "Failed",
                    item["result"],
                    item["error"],
                    item["message"],
                ])

    messagebox.showinfo("Export CSV", "CSV export completed successfully.")


def export_results_pdf(root):
    run = getattr(root, "last_run", None)
    comparison = getattr(root, "last_comparison", None)
    if not run and not comparison:
        messagebox.showinfo("Export PDF", "Run a calculation or comparison first.")
        return

    path = filedialog.asksaveasfilename(
        title="Export PDF",
        defaultextension=".pdf",
        filetypes=[("PDF file", "*.pdf")],
    )
    if not path:
        return

    with PdfPages(path) as pdf:
        if run:
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.08, 0.95, "Numerical Methods Calculator Report", fontsize=18, fontweight="bold")
            fig.text(0.08, 0.91, f"Generated: {run['timestamp']}", fontsize=9)
            fig.text(0.08, 0.86, f"Equation: {run['equation']}", fontsize=11)
            fig.text(0.08, 0.82, f"Method: {run['method']}", fontsize=11)
            fig.text(0.08, 0.78, f"Root: {run['result']}", fontsize=11)
            fig.text(0.08, 0.74, f"Error: {run['error']}", fontsize=11)
            fig.text(0.08, 0.70, f"Status: {'Success' if run['success'] else 'Failed'}", fontsize=11)
            fig.text(0.08, 0.64, "Message:", fontsize=11, fontweight="bold")
            fig.text(0.08, 0.60, run["message"], fontsize=10, wrap=True)
            fig.text(0.08, 0.54, "Diagnosis:", fontsize=11, fontweight="bold")
            fig.text(0.08, 0.50, run["diagnosis"], fontsize=10, wrap=True)
            fig.text(0.08, 0.44, "Recommendation:", fontsize=11, fontweight="bold")
            fig.text(0.08, 0.40, run["recommendation"], fontsize=10, wrap=True)
            if run["history"]:
                chart = fig.add_axes([0.1, 0.08, 0.8, 0.24])
                chart.plot(range(1, len(run["history"]) + 1), run["history"], marker="o", color="#2563eb")
                chart.set_title("Convergence History")
                chart.set_xlabel("Iteration")
                chart.set_ylabel("Residual / Error")
                chart.grid(True, alpha=0.3)
            pdf.savefig(fig)
            plt.close(fig)

        if comparison:
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.08, 0.95, "Method Comparison Lab", fontsize=18, fontweight="bold")
            fig.text(0.08, 0.91, f"Equation: {comparison['equation']}", fontsize=11)
            y = 0.86
            for item in comparison["runs"]:
                fig.text(0.08, y, f"{item['method']}: {'Success' if item['success'] else 'Failed'} | Root={item['result']} | Error={item['error']}", fontsize=9)
                y -= 0.035
                fig.text(0.1, y, item["message"], fontsize=8)
                y -= 0.05
                if y < 0.08:
                    pdf.savefig(fig)
                    plt.close(fig)
                    fig = plt.figure(figsize=(8.27, 11.69))
                    y = 0.95
            pdf.savefig(fig)
            plt.close(fig)

    messagebox.showinfo("Export PDF", "PDF export completed successfully.")


def show_comparison(root, method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry):
    try:
        data = _enhanced_parse_inputs(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry)
    except Exception as e:
        messagebox.showerror("Comparison Error", str(e))
        return None

    runs = []
    for method in METHOD_RUNNERS:
        run_b = data["b"] if method in BRACKET_METHODS else data["a"]
        try:
            result, error, msg, steps_text = METHOD_RUNNERS[method](data["f"], data["a"], run_b, data["tolerance"], data["max_iterations"])
            success = result is not None and error is not None
            runs.append({
                "method": method,
                "result": result,
                "error": error,
                "message": msg,
                "success": success,
                "diagnosis": _diagnose_failure(method, msg, success),
                "history": _extract_convergence_history(steps_text),
            })
        except Exception as e:
            runs.append({
                "method": method,
                "result": None,
                "error": None,
                "message": f"Execution error: {e}",
                "success": False,
                "diagnosis": _diagnose_failure(method, f"Execution error: {e}", False),
                "history": [],
            })

    successful = [item for item in runs if item["success"]]
    successful.sort(key=lambda item: item["error"])
    ordered = successful + [item for item in runs if item not in successful]

    root.last_comparison = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "equation": data["equation"],
        "runs": ordered,
    }

    popup = tk.Toplevel(root)
    popup.title("Method Comparison Lab")
    popup.geometry("920x600")
    popup.configure(bg="#f8fafc")

    header = tk.Frame(popup, bg="#0f766e", padx=18, pady=16)
    header.pack(fill="x")
    tk.Label(header, text="Method Comparison Lab", bg="#0f766e", fg="white", font=("Segoe UI", 15, "bold")).pack(anchor="w")
    subtitle = "No method converged with the current settings."
    if successful:
        subtitle = f"Best residual: {successful[0]['method']} with error {successful[0]['error']:.6f}"
    tk.Label(header, text=subtitle, bg="#0f766e", fg="#ccfbf1", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))

    body = tk.Frame(popup, bg="#f8fafc", padx=18, pady=18)
    body.pack(fill="both", expand=True)

    canvas = tk.Canvas(body, bg="#f8fafc", highlightthickness=0)
    scroll = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
    list_frame = tk.Frame(canvas, bg="#f8fafc")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    canvas.create_window((0, 0), window=list_frame, anchor="nw")
    list_frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))

    for index, item in enumerate(ordered, start=1):
        bg = "#ecfeff" if item["success"] else "#fef2f2"
        card = tk.Frame(list_frame, bg=bg, padx=16, pady=16)
        card.pack(fill="x", pady=8)
        root_text = f"{item['result']:.6f}" if item["result"] is not None else "--"
        error_text = f"{item['error']:.6f}" if item["error"] is not None else "--"
        status = "Converged" if item["success"] else "Did not converge"
        tk.Label(card, text=f"{index}. {item['method']}", bg=bg, fg="#0f172a", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(card, text=f"Status: {status}    Root: {root_text}    Error: {error_text}", bg=bg, fg="#334155", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 4))
        tk.Label(card, text=item["message"], bg=bg, fg="#475569", font=("Segoe UI", 10), wraplength=800, justify="left").pack(anchor="w")
        tk.Label(card, text=item["diagnosis"], bg=bg, fg="#0f766e", font=("Segoe UI", 9), wraplength=800, justify="left").pack(anchor="w", pady=(6, 0))

    return ordered


def calculate_root(root, method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry, result_label, error_label, info_label, check_var, plot_var, clear_var):
    try:
        data = _enhanced_parse_inputs(method_var, expression_entry, tolerance_entry, max_iterations_entry, a_entry, b_entry)
    except Exception as e:
        failed_run = {
            "method": method_var.get(),
            "result": None,
            "error": None,
            "message": f"Input error: {e}",
            "success": False,
        }
        _set_result_state(result_label, error_label, info_label, failed_run)
        root.last_run = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "equation": expression_entry.get().strip(),
            "method": method_var.get(),
            "a": a_entry.get(),
            "b": b_entry.get(),
            "tolerance": tolerance_entry.get(),
            "max_iterations": max_iterations_entry.get(),
            "result": None,
            "error": None,
            "message": failed_run["message"],
            "steps_text": "",
            "history": [],
            "success": False,
            "diagnosis": "Please correct the input values before running the method again.",
            "recommendation": "Check the input fields and then try the recommendation tool again.",
        }
        return root.last_run

    run_b = data["b"] if data["method"] in BRACKET_METHODS else data["a"]
    result, error, msg, steps_text = METHOD_RUNNERS[data["method"]](data["f"], data["a"], run_b, data["tolerance"], data["max_iterations"])
    success = result is not None and error is not None

    run = {
        "method": data["method"],
        "result": result,
        "error": error,
        "message": msg,
        "success": success,
    }
    _set_result_state(result_label, error_label, info_label, run)

    root.last_run = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "equation": data["equation"],
        "method": data["method"],
        "a": data["a"],
        "b": data["b"],
        "tolerance": data["tolerance"],
        "max_iterations": data["max_iterations"],
        "result": result,
        "error": error,
        "message": msg,
        "steps_text": steps_text,
        "history": _extract_convergence_history(steps_text),
        "success": success,
        "diagnosis": _diagnose_failure(data["method"], msg, success),
        "recommendation": _recommend_method(data),
    }

    if success and is_checked(check_var):
        show_steps(steps_text, msg, root, clear_var)

    if success and is_checked(plot_var):
        if data["method"] == "Bisection":
            plot_bisection_method(data["f"], data["a"], data["b"], data["max_iterations"], data["tolerance"])
        elif data["method"] == "False Position":
            plot_false_position_method(data["f"], data["a"], data["b"], data["max_iterations"], data["tolerance"])
        elif data["method"] == "Secant":
            plot_secant_method(data["f"], data["a"], data["b"], data["max_iterations"], data["tolerance"])
        elif data["method"] == "Newton-Raphson":
            plot_newton_raphson_method(data["f"], data["a"], data["max_iterations"], data["tolerance"])
        else:
            plot_simple_fixed_point_iteration(data["f"], data["a"], data["max_iterations"], data["tolerance"])

    return root.last_run
