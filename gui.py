import tkinter as tk
from tkinter import ttk

from calculations import (
    calculate_root,
    clear_results,
    export_results_csv,
    export_results_pdf,
    preview_recommendation,
    show_comparison,
    show_convergence_dashboard,
)


METHODS = [
    "Bisection",
    "False Position",
    "Secant",
    "Newton-Raphson",
    "Simple Fixed-Point Iteration",
]

PRESETS = {
    "Classic cubic": {
        "method": "Bisection",
        "equation": "x**3 - x - 2",
        "a": "1",
        "b": "2",
        "tolerance": "0.001",
        "max_iterations": "25",
    },
    "Cosine crossing": {
        "method": "Newton-Raphson",
        "equation": "cos(x) - x",
        "a": "0.7",
        "b": "",
        "tolerance": "0.00001",
        "max_iterations": "20",
    },
    "Exponential balance": {
        "method": "False Position",
        "equation": "exp(-x) - x",
        "a": "0",
        "b": "1",
        "tolerance": "0.0001",
        "max_iterations": "30",
    },
    "Secant demo": {
        "method": "Secant",
        "equation": "x**3 - 4*x - 9",
        "a": "2",
        "b": "3",
        "tolerance": "0.0001",
        "max_iterations": "20",
    },
}

METHOD_CONFIG = {
    "Bisection": {
        "accent": "#2E8B57",
        "description": "Bracket the root by repeatedly halving an interval where the sign changes.",
        "primary_label": "Lower bound (a)",
        "secondary_label": "Upper bound (b)",
        "primary_default": "1",
        "secondary_default": "5",
        "secondary_required": True,
    },
    "False Position": {
        "accent": "#E67E22",
        "description": "Refine the interval with a secant-style estimate while preserving the bracket.",
        "primary_label": "Lower bound (a)",
        "secondary_label": "Upper bound (b)",
        "primary_default": "1",
        "secondary_default": "5",
        "secondary_required": True,
    },
    "Secant": {
        "accent": "#1F7A8C",
        "description": "Use two starting guesses and secant lines to converge toward the root.",
        "primary_label": "First guess (x0)",
        "secondary_label": "Second guess (x1)",
        "primary_default": "1",
        "secondary_default": "2",
        "secondary_required": True,
    },
    "Newton-Raphson": {
        "accent": "#8E5CF1",
        "description": "Start from one estimate and iteratively improve it using the derivative.",
        "primary_label": "Initial guess (x0)",
        "secondary_label": "Not required for this method",
        "primary_default": "1.5",
        "secondary_default": "",
        "secondary_required": False,
    },
    "Simple Fixed-Point Iteration": {
        "accent": "#C8553D",
        "description": "Iteratively evaluate the transformed function until the result stabilizes.",
        "primary_label": "Initial guess (x0)",
        "secondary_label": "Not required for this method",
        "primary_default": "1.5",
        "secondary_default": "",
        "secondary_required": False,
    },
}


def create_gui(root):
    root.title("Numerical Methods Calculator")
    root.geometry("1080x720")
    root.minsize(960, 640)
    root.configure(bg="#0b1020")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("App.TCombobox", fieldbackground="#eef2ff", background="#eef2ff")

    method_var = tk.StringVar(value=METHODS[0])
    check_var = tk.IntVar(value=1)
    plot_var = tk.IntVar(value=0)
    clear_var = tk.IntVar(value=1)

    outer = tk.Frame(root, bg="#0b1020")
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer, bg="#0b1020", highlightthickness=0, bd=0)
    scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content = tk.Frame(canvas, bg="#0b1020", padx=24, pady=24)
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")

    def sync_canvas_width(_event):
        canvas.itemconfigure(canvas_window, width=canvas.winfo_width())

    def update_scroll_region(_event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def handle_mousewheel(event):
        if canvas.winfo_height() < content.winfo_reqheight():
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<Configure>", sync_canvas_width)
    content.bind("<Configure>", update_scroll_region)
    canvas.bind_all("<MouseWheel>", handle_mousewheel)

    state = {"current_screen": None}

    def destroy_steps_window():
        if hasattr(root, "steps_window") and root.steps_window.winfo_exists():
            root.steps_window.destroy()

    def switch_screen(builder):
        destroy_steps_window()
        if state["current_screen"] is not None:
            state["current_screen"].destroy()
        state["current_screen"] = builder()
        state["current_screen"].pack(fill="both", expand=True)

    def make_primary_button(parent, text, command, bg="#2563eb", fg="white", width=18):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=18,
            pady=12,
            width=width,
            cursor="hand2",
        )

    def make_secondary_button(parent, text, command, width=16):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg="#e5e7eb",
            fg="#111827",
            activebackground="#d1d5db",
            activeforeground="#111827",
            relief="flat",
            bd=0,
            padx=16,
            pady=11,
            width=width,
            cursor="hand2",
        )

    def build_shell(parent, title_text, subtitle_text, accent):
        page = tk.Frame(parent, bg="#0b1020")

        hero = tk.Frame(page, bg=accent, padx=28, pady=26)
        hero.pack(fill="x")

        tk.Label(
            hero,
            text=title_text,
            font=("Segoe UI", 24, "bold"),
            bg=accent,
            fg="white",
        ).pack(anchor="w")
        tk.Label(
            hero,
            text=subtitle_text,
            font=("Segoe UI", 11),
            bg=accent,
            fg="#eef2ff",
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        card = tk.Frame(page, bg="#f8fafc", padx=28, pady=28)
        card.pack(fill="both", expand=True, pady=(18, 0))
        return page, card

    def show_welcome():
        def builder():
            page = tk.Frame(content, bg="#0b1020")

            left = tk.Frame(page, bg="#111936", padx=36, pady=36)
            left.pack(side="left", fill="both", expand=True, padx=(0, 12))

            right = tk.Frame(page, bg="#f8fafc", padx=36, pady=36)
            right.pack(side="left", fill="both", expand=True, padx=(12, 0))

            tk.Label(
                left,
                text="Numerical\nMethods\nCalculator",
                font=("Segoe UI", 30, "bold"),
                bg="#111936",
                fg="white",
                justify="left",
            ).pack(anchor="w")

            tk.Label(
                left,
                text="A focused workspace for root-finding methods with step inspection and graph support.",
                font=("Segoe UI", 12),
                bg="#111936",
                fg="#dbeafe",
                justify="left",
                wraplength=360,
            ).pack(anchor="w", pady=(18, 26))

            highlights = [
                "Choose the method that fits your problem.",
                "Enter your function and starting values in a dedicated input page.",
                "Review the result, estimated error, iteration steps, and graphs.",
            ]
            for item in highlights:
                row = tk.Frame(left, bg="#111936")
                row.pack(anchor="w", pady=6, fill="x")
                tk.Label(row, text="*", font=("Segoe UI", 16, "bold"), bg="#111936", fg="#60a5fa").pack(side="left")
                tk.Label(
                    row,
                    text=item,
                    font=("Segoe UI", 11),
                    bg="#111936",
                    fg="#e5eefc",
                    justify="left",
                    wraplength=330,
                ).pack(side="left", padx=(10, 0))

            make_primary_button(left, "Start", show_method_selection, bg="#38bdf8", fg="#082f49", width=16).pack(
                anchor="w", pady=(34, 0)
            )

            tk.Label(
                right,
                text="Flow",
                font=("Segoe UI", 14, "bold"),
                bg="#f8fafc",
                fg="#0f172a",
            ).pack(anchor="w")

            stages = [
                ("1", "Welcome", "Begin from a clean overview of the application."),
                ("2", "Choose Method", "Select the numerical technique you want to use."),
                ("3", "Calculate", "Fill the method-specific form and compute the solution."),
            ]
            for number, heading, description in stages:
                block = tk.Frame(right, bg="#e2e8f0", padx=18, pady=18)
                block.pack(fill="x", pady=10)
                tk.Label(block, text=number, font=("Segoe UI", 18, "bold"), bg="#e2e8f0", fg="#2563eb").pack(anchor="w")
                tk.Label(block, text=heading, font=("Segoe UI", 13, "bold"), bg="#e2e8f0", fg="#111827").pack(anchor="w")
                tk.Label(
                    block,
                    text=description,
                    font=("Segoe UI", 10),
                    bg="#e2e8f0",
                    fg="#475569",
                    wraplength=320,
                    justify="left",
                ).pack(anchor="w", pady=(6, 0))

            return page

        switch_screen(builder)

    def show_method_selection():
        def builder():
            page, card = build_shell(
                content,
                "Choose a Numerical Method",
                "Pick the algorithm first. The next screen will tailor the inputs to that method.",
                "#1d4ed8",
            )

            tk.Label(
                card,
                text="Available Methods",
                font=("Segoe UI", 16, "bold"),
                bg="#f8fafc",
                fg="#0f172a",
            ).pack(anchor="w")

            methods_grid = tk.Frame(card, bg="#f8fafc")
            methods_grid.pack(fill="both", expand=True, pady=(18, 24))
            methods_grid.grid_columnconfigure(0, weight=1)
            methods_grid.grid_columnconfigure(1, weight=1)

            def build_method_card(parent, method_name, row, column):
                cfg = METHOD_CONFIG[method_name]
                selected = method_var.get() == method_name
                card_bg = "#dbeafe" if selected else "white"
                border_color = cfg["accent"] if selected else "#cbd5e1"

                card_frame = tk.Frame(parent, bg=border_color, padx=2, pady=2)
                card_frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)
                card_body = tk.Frame(card_frame, bg=card_bg, padx=18, pady=18, cursor="hand2")
                card_body.pack(fill="both", expand=True)

                def select_and_continue(_event, name=method_name):
                    method_var.set(name)
                    show_calculation_page()

                for widget in (card_frame, card_body):
                    widget.bind("<Button-1>", select_and_continue)

                title_label = tk.Label(
                    card_body,
                    text=method_name,
                    font=("Segoe UI", 13, "bold"),
                    bg=card_bg,
                    fg="#0f172a",
                )
                title_label.pack(anchor="w")
                description_label = tk.Label(
                    card_body,
                    text=cfg["description"],
                    font=("Segoe UI", 10),
                    bg=card_bg,
                    fg="#475569",
                    justify="left",
                    wraplength=320,
                )
                description_label.pack(anchor="w", pady=(10, 0))

                for widget in (title_label, description_label):
                    widget.bind("<Button-1>", select_and_continue)

            for index, method_name in enumerate(METHODS):
                build_method_card(methods_grid, method_name, index // 2, index % 2)

            actions = tk.Frame(card, bg="#f8fafc")
            actions.pack(fill="x")
            make_secondary_button(actions, "Back", show_welcome).pack(side="left")
            make_primary_button(actions, "Continue", show_calculation_page, bg="#2563eb").pack(side="right")

            return page

        switch_screen(builder)

    def show_calculation_page():
        def builder():
            method_name = method_var.get()
            cfg = METHOD_CONFIG[method_name]
            page, card = build_shell(content, method_name, cfg["description"], cfg["accent"])

            content_area = tk.Frame(card, bg="#f8fafc")
            content_area.pack(fill="both", expand=True)

            form_card = tk.Frame(content_area, bg="white", padx=24, pady=24)
            form_card.pack(side="left", fill="both", expand=True, padx=(0, 12))

            side_card = tk.Frame(content_area, bg="#e2e8f0", padx=24, pady=24, width=280)
            side_card.pack(side="left", fill="y", padx=(12, 0))
            side_card.pack_propagate(False)

            tk.Label(form_card, text="Calculation Inputs", font=("Segoe UI", 16, "bold"), bg="white", fg="#0f172a").pack(anchor="w")
            tk.Label(
                form_card,
                text="Enter your function and starting values. Use x as the variable and ^ or ** for powers.",
                font=("Segoe UI", 10),
                bg="white",
                fg="#64748b",
                justify="left",
                wraplength=560,
            ).pack(anchor="w", pady=(6, 18))

            preset_row = tk.Frame(form_card, bg="white")
            preset_row.pack(fill="x", pady=(0, 12))
            tk.Label(preset_row, text="Equation Presets", font=("Segoe UI", 10, "bold"), bg="white", fg="#334155").pack(side="left")
            preset_var = tk.StringVar(value="Choose preset")
            preset_menu = ttk.Combobox(
                preset_row,
                textvariable=preset_var,
                values=list(PRESETS.keys()),
                state="readonly",
                width=24,
            )
            preset_menu.pack(side="left", padx=12)

            fields = tk.Frame(form_card, bg="white")
            fields.pack(fill="x")
            fields.grid_columnconfigure(0, weight=1)
            fields.grid_columnconfigure(1, weight=1)

            def labeled_entry(parent, label_text, default_value, row, column, width=26):
                wrapper = tk.Frame(parent, bg="white")
                wrapper.grid(row=row, column=column, sticky="ew", padx=8, pady=8)
                tk.Label(wrapper, text=label_text, font=("Segoe UI", 10, "bold"), bg="white", fg="#334155").pack(anchor="w")
                entry = tk.Entry(
                    wrapper,
                    font=("Segoe UI", 11),
                    bg="#f8fafc",
                    fg="#0f172a",
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground="#cbd5e1",
                    highlightcolor=cfg["accent"],
                    insertbackground="#0f172a",
                    width=width,
                )
                entry.insert(0, default_value)
                entry.pack(fill="x", pady=(8, 0), ipady=8)
                return entry

            expression_entry = labeled_entry(fields, "Function f(x)", "x**3 - x - 2", 0, 0, width=58)
            expression_entry.master.grid(columnspan=2)

            a_entry = labeled_entry(fields, cfg["primary_label"], cfg["primary_default"], 1, 0)
            b_entry = labeled_entry(fields, cfg["secondary_label"], cfg["secondary_default"], 1, 1)
            tolerance_entry = labeled_entry(fields, "Tolerance", "0.01", 2, 0)
            max_iterations_entry = labeled_entry(fields, "Max iterations", "10", 2, 1)

            def apply_entry_value(entry, value, disabled=False):
                entry.configure(state="normal")
                entry.delete(0, "end")
                entry.insert(0, value)
                if disabled:
                    entry.configure(state="disabled", disabledbackground="#e5e7eb", disabledforeground="#94a3b8")

            pending_preset = getattr(root, "pending_preset", None)
            if pending_preset and pending_preset["method"] == method_name:
                apply_entry_value(expression_entry, pending_preset["equation"])
                apply_entry_value(a_entry, pending_preset["a"])
                apply_entry_value(b_entry, pending_preset["b"] or "", disabled=not cfg["secondary_required"])
                apply_entry_value(tolerance_entry, pending_preset["tolerance"])
                apply_entry_value(max_iterations_entry, pending_preset["max_iterations"])
                root.pending_preset = None

            if not cfg["secondary_required"]:
                b_entry.configure(state="disabled", disabledbackground="#e5e7eb", disabledforeground="#94a3b8")

            def apply_selected_preset():
                preset_name = preset_var.get()
                if preset_name not in PRESETS:
                    return
                preset = PRESETS[preset_name]
                root.pending_preset = preset
                method_var.set(preset["method"])
                show_calculation_page()

            make_secondary_button(preset_row, "Apply Preset", apply_selected_preset, width=14).pack(side="left")

            tk.Label(side_card, text="Method Snapshot", font=("Segoe UI", 15, "bold"), bg="#e2e8f0", fg="#0f172a").pack(anchor="w")
            tk.Label(
                side_card,
                text=cfg["description"],
                font=("Segoe UI", 10),
                bg="#e2e8f0",
                fg="#475569",
                justify="left",
                wraplength=220,
            ).pack(anchor="w", pady=(10, 18))

            tk.Label(side_card, text="Options", font=("Segoe UI", 12, "bold"), bg="#e2e8f0", fg="#0f172a").pack(anchor="w")

            check_style = {
                "bg": "#e2e8f0",
                "fg": "#0f172a",
                "selectcolor": "#ffffff",
                "activebackground": "#e2e8f0",
                "activeforeground": "#0f172a",
                "font": ("Segoe UI", 10),
            }

            tk.Checkbutton(side_card, text="Show iteration steps", variable=check_var, **check_style).pack(anchor="w", pady=(10, 4))
            tk.Checkbutton(side_card, text="Plot graph", variable=plot_var, **check_style).pack(anchor="w", pady=4)
            tk.Checkbutton(side_card, text="Clear old result windows", variable=clear_var, **check_style).pack(anchor="w", pady=4)

            hint_text = (
                f"Use {cfg['primary_label'].lower()} and {cfg['secondary_label'].lower()}."
                if cfg["secondary_required"]
                else f"Only {cfg['primary_label'].lower()} is needed here."
            )
            tk.Label(
                side_card,
                text=hint_text,
                font=("Segoe UI", 10),
                bg="#e2e8f0",
                fg="#475569",
                justify="left",
                wraplength=220,
            ).pack(anchor="w", pady=(18, 0))

            tk.Label(side_card, text="Method Advice", font=("Segoe UI", 12, "bold"), bg="#e2e8f0", fg="#0f172a").pack(anchor="w", pady=(22, 6))
            recommendation_label = tk.Label(
                side_card,
                text="Use Suggest Best Method for a tailored recommendation.",
                font=("Segoe UI", 10),
                bg="#e2e8f0",
                fg="#475569",
                justify="left",
                wraplength=220,
            )
            recommendation_label.pack(anchor="w")

            tk.Label(side_card, text="Failure Diagnosis", font=("Segoe UI", 12, "bold"), bg="#e2e8f0", fg="#0f172a").pack(anchor="w", pady=(18, 6))
            diagnosis_label = tk.Label(
                side_card,
                text="Run a method to get convergence or failure guidance.",
                font=("Segoe UI", 10),
                bg="#e2e8f0",
                fg="#475569",
                justify="left",
                wraplength=220,
            )
            diagnosis_label.pack(anchor="w")

            summary_label = tk.Label(
                form_card,
                text="Summary updates after each calculation.",
                font=("Segoe UI", 10),
                bg="white",
                fg="#64748b",
                justify="left",
                wraplength=620,
            )
            summary_label.pack(anchor="w", pady=(18, 0))

            def refresh_analysis_panels():
                run = getattr(root, "last_run", None)
                if not run:
                    summary_label.config(text="Summary updates after each calculation.", fg="#64748b")
                    recommendation_label.config(text="Use Suggest Best Method for a tailored recommendation.", fg="#475569")
                    diagnosis_label.config(text="Run a method to get convergence or failure guidance.", fg="#475569")
                    return
                status_text = "Converged" if run["success"] else "Not converged"
                summary_label.config(
                    text=f"{run['method']} | {status_text} | Root: {run['result']} | Error: {run['error']}",
                    fg="#334155",
                )
                recommendation_label.config(text=run["recommendation"], fg="#0f766e")
                diagnosis_label.config(text=run["diagnosis"], fg="#7c2d12" if not run["success"] else "#475569")

            def suggest_best_method():
                try:
                    recommendation_label.config(
                        text=preview_recommendation(
                            method_var,
                            expression_entry,
                            tolerance_entry,
                            max_iterations_entry,
                            a_entry,
                            b_entry,
                        ),
                        fg="#0f766e",
                    )
                except Exception as exc:
                    recommendation_label.config(text=f"Recommendation unavailable: {exc}", fg="#b91c1c")

            def reset_everything():
                destroy_steps_window()
                clear_results(result_label, error_label, info_label)
                root.last_run = None
                refresh_analysis_panels()

            def run_calculation():
                clear_results(result_label, error_label, info_label)
                calculate_root(
                    root,
                    method_var,
                    expression_entry,
                    tolerance_entry,
                    max_iterations_entry,
                    a_entry,
                    b_entry,
                    result_label,
                    error_label,
                    info_label,
                    check_var,
                    plot_var,
                    clear_var,
                )
                refresh_analysis_panels()

            actions = tk.Frame(form_card, bg="white")
            actions.pack(fill="x", pady=(24, 8))

            make_secondary_button(actions, "Back", show_method_selection).pack(side="left")
            make_secondary_button(actions, "Reset Result", reset_everything, width=14).pack(side="left", padx=10)
            make_secondary_button(actions, "Suggest Best Method", suggest_best_method, width=18).pack(side="left")
            make_primary_button(actions, "Calculate", run_calculation, bg=cfg["accent"], width=16).pack(side="right")

            tools_row = tk.Frame(form_card, bg="white")
            tools_row.pack(fill="x", pady=(0, 16))
            make_secondary_button(
                tools_row,
                "Compare Methods",
                lambda: show_comparison(
                    root,
                    method_var,
                    expression_entry,
                    tolerance_entry,
                    max_iterations_entry,
                    a_entry,
                    b_entry,
                ),
                width=16,
            ).pack(side="left")
            make_secondary_button(tools_row, "Convergence Chart", lambda: show_convergence_dashboard(root), width=16).pack(side="left", padx=10)
            make_secondary_button(tools_row, "Export CSV", lambda: export_results_csv(root), width=12).pack(side="left")
            make_secondary_button(tools_row, "Export PDF", lambda: export_results_pdf(root), width=12).pack(side="left", padx=10)

            tk.Label(form_card, text="Results", font=("Segoe UI", 15, "bold"), bg="white", fg="#0f172a").pack(anchor="w", pady=(10, 10))

            result_panel = tk.Frame(form_card, bg="#eff6ff", padx=18, pady=18)
            result_panel.pack(fill="x")

            tk.Label(
                result_panel,
                text="Structured result summary",
                fg="#475569",
                bg="#eff6ff",
                font=("Segoe UI", 10),
                justify="left",
            ).pack(anchor="w")

            stat_grid = tk.Frame(result_panel, bg="#eff6ff")
            stat_grid.pack(fill="x", pady=(14, 12))
            stat_grid.grid_columnconfigure(0, weight=1)
            stat_grid.grid_columnconfigure(1, weight=1)
            stat_grid.grid_columnconfigure(2, weight=1)

            def build_stat_card(parent, title, value, column, accent_color):
                card = tk.Frame(parent, bg="white", padx=14, pady=14)
                card.grid(row=0, column=column, sticky="ew", padx=6)
                tk.Label(card, text=title, bg="white", fg="#64748b", font=("Segoe UI", 9, "bold")).pack(anchor="w")
                value_label = tk.Label(
                    card,
                    text=value,
                    bg="white",
                    fg=accent_color,
                    font=("Segoe UI", 14, "bold"),
                    justify="left",
                    wraplength=150,
                )
                value_label.pack(anchor="w", pady=(8, 0))
                return value_label

            result_label = build_stat_card(stat_grid, "Approximate Root", "--", 0, cfg["accent"])
            error_label = build_stat_card(stat_grid, "Residual / Error", "Waiting", 1, "#b45309")
            info_label = build_stat_card(stat_grid, "Run Status", "Enter values and run a method.", 2, "#334155")

            insight_box = tk.Frame(result_panel, bg="white", padx=14, pady=14)
            insight_box.pack(fill="x", pady=(4, 0))
            tk.Label(
                insight_box,
                text="Unique feature: Method Comparison Lab lets you compare all supported methods for the same equation in one view.",
                bg="white",
                fg="#475569",
                font=("Segoe UI", 10),
                justify="left",
                wraplength=620,
            ).pack(anchor="w")

            refresh_analysis_panels()

            return page

        switch_screen(builder)

    show_welcome()
    root.mainloop()
