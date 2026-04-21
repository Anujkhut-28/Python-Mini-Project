import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math

# LOAD & CLEAN DATA 
df = pd.read_csv("CO2_Emissions_Canada.csv")

df["Make"] = df["Make"].astype(str).str.strip().str.upper()
df["Model"] = df["Model"].astype(str).str.strip()
df = df.dropna()

# DATA 
industries = {
    "cement": 0.9,
    "steel": 1.85,
    "textile": 0.6,
    "paper": 1.3
}

history = []

# FUNCTIONS

def trees_required(co2):
    return math.floor(co2 / 21)

def carbon_score(co2):
    if co2 < 5:
        return 90
    elif co2 < 20:
        return 70
    elif co2 < 50:
        return 50
    else:
        return 30

def rating_text(score):
    if score >= 80:
        return "🌱 Excellent"
    elif score >= 60:
        return "🙂 Good"
    elif score >= 40:
        return "⚠️ Moderate"
    else:
        return "🔥 Poor"

def suggestions(co2):
    if co2 > 50:
        return "Use renewable energy"
    elif co2 > 20:
        return "Reduce consumption"
    else:
        return "Eco-friendly 👍"

def real_world_impact(co2):
    km = co2 / 0.12
    return f"Equivalent to driving {round(km,2)} km"

# DASHBOARD GRAPH 
def show_graph(title, co2):
    trees = trees_required(co2)
    score = carbon_score(co2)

    labels = ["CO2 (kg)", "Trees", "Score"]
    values = [co2, trees, score]

    plt.figure()
    bars = plt.bar(labels, values)

    for bar in bars:
        y = bar.get_height()
        plt.text(bar.get_x()+bar.get_width()/2, y, int(y), ha='center')

    plt.title(f"{title} Dashboard View")
    plt.ylabel("Values")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.show()

# MODEL UPDATE
def update_models(event=None):
    company = company_var.get()
    filtered = df[df["Make"] == company]

    models = filtered["Model"].dropna().unique().tolist()
    models = [m for m in models if m != "0"]

    model_dropdown["values"] = models

    if models:
        model_dropdown.current(0)

# SAVE
def save_result(name, co2):
    history.append((name, co2))
    with open("history.txt", "a") as f:
        f.write(f"{datetime.now()} - {name}: {co2} kg\n")

# TREE ICON DISPLAY 
def tree_visual(trees):
    if trees == 0:
        return "No trees needed 🌱"
    elif trees > 20:
        return "🌳 x " + str(trees)
    else:
        return "🌳" * trees

# RESULT
def show_result(name, co2):
    trees = trees_required(co2)
    score = carbon_score(co2)

    text = f"""
{name} CO2: {round(co2,2)} kg
Trees Required: {trees}

{tree_visual(trees)}

Score: {score} ({rating_text(score)})
{real_world_impact(co2)}
Suggestion: {suggestions(co2)}
"""
    result_label.config(text=text)

    if co2 > 50:
        messagebox.showwarning("High Emission", "This is harmful!")

# CALCULATIONS

def calculate_vehicle():
    try:
        vehicle = df[(df["Make"] == company_var.get()) &
                     (df["Model"] == model_var.get())].iloc[0]

        distance = float(distance_entry.get())
        co2 = (vehicle["CO2 Emissions(g/km)"] * distance) / 1000

        show_result("Vehicle", co2)
        show_graph("Vehicle", co2)
        save_result("Vehicle", co2)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def calculate_industry():
    try:
        co2 = float(production_entry.get()) * industries[industry_var.get()]
        show_result("Industry", co2)
        show_graph("Industry", co2)
        save_result("Industry", co2)
    except:
        messagebox.showerror("Error", "Invalid input")


def calculate_data_center():
    try:
        co2 = float(power_entry.get()) * 0.7
        show_result("Data Center", co2)
        show_graph("Data Center", co2)
        save_result("Data Center", co2)
    except:
        messagebox.showerror("Error", "Invalid input")


def calculate_company():
    try:
        co2 = int(employee_entry.get()) * 50
        show_result("Company", co2)
        show_graph("Company", co2)
        save_result("Company", co2)
    except:
        messagebox.showerror("Error", "Invalid input")

# TOP CARS
def show_top_cars():
    grouped = df.groupby(["Make", "Model"])["CO2 Emissions(g/km)"].min().reset_index()
    top = grouped.sort_values(by="CO2 Emissions(g/km)").head(5)

    text = "Top 5 Low Emission Cars:\n\n"
    for i, row in top.iterrows():
        text += f"{i+1}. {row['Make']} {row['Model']} - {row['CO2 Emissions(g/km)']} g/km\n"

    messagebox.showinfo("Top Cars", text)

# HISTORY
def show_history():
    if not history:
        messagebox.showinfo("History", "No data yet")
        return

    text = ""
    for item in history:
        text += f"{item[0]}: {round(item[1],2)} kg\n"

    messagebox.showinfo("History", text)

# COMPARISON
def comparison_graph():
    if len(history) < 2:
        messagebox.showinfo("Info", "Need 2 results")
        return

    history.sort(key=lambda x: x[1])
    labels = [x[0] for x in history]
    values = [x[1] for x in history]

    plt.figure()
    plt.bar(labels, values)
    plt.title("Emission Comparison")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.show()

#  RESET 
def reset_fields():
    company_var.set("")
    model_var.set("")
    distance_entry.delete(0, tk.END)

# GUI 

root = tk.Tk()
root.title("Carbon Dashboard")
root.geometry("620x720")
root.configure(bg="#eef6fb")

tk.Label(root, text="🌍 Carbon Emission Calculator",
         font=("Arial", 16, "bold"), bg="#eef6fb").pack(pady=10)

# VEHICLE 
frame1 = tk.LabelFrame(root, text="Vehicle")
frame1.pack(fill="x", padx=10, pady=5)

tk.Label(frame1, text="Company").pack()
company_var = tk.StringVar()
company_dropdown = ttk.Combobox(frame1, textvariable=company_var)
company_dropdown["values"] = sorted(df["Make"].unique())
company_dropdown.bind("<<ComboboxSelected>>", update_models)
company_dropdown.pack()

tk.Label(frame1, text="Model").pack()
model_var = tk.StringVar()
model_dropdown = ttk.Combobox(frame1, textvariable=model_var)
model_dropdown.pack()

tk.Label(frame1, text="Distance (km)").pack()
distance_entry = tk.Entry(frame1)
distance_entry.pack()

tk.Button(frame1, text="Calculate Vehicle 🚗", bg="#4CAF50", fg="white",
          command=calculate_vehicle).pack(pady=5)

# INDUSTRY 
frame2 = tk.LabelFrame(root, text="Industry")
frame2.pack(fill="x", padx=10, pady=5)

tk.Label(frame2, text="Industry Type").pack()
industry_var = tk.StringVar()
industry_dropdown = ttk.Combobox(frame2, textvariable=industry_var)
industry_dropdown["values"] = list(industries.keys())
industry_dropdown.pack()

tk.Label(frame2, text="Production (kg)").pack()
production_entry = tk.Entry(frame2)
production_entry.pack()

tk.Button(frame2, text="Calculate Industry", command=calculate_industry).pack(pady=5)

# DATA CENTER 
frame3 = tk.LabelFrame(root, text="Data Center")
frame3.pack(fill="x", padx=10, pady=5)

tk.Label(frame3, text="Electricity Used (kWh)").pack()
power_entry = tk.Entry(frame3)
power_entry.pack()

tk.Button(frame3, text="Calculate Data Center", command=calculate_data_center).pack(pady=5)

# COMPANY 
frame4 = tk.LabelFrame(root, text="Company")
frame4.pack(fill="x", padx=10, pady=5)

tk.Label(frame4, text="Number of Employees").pack()
employee_entry = tk.Entry(frame4)
employee_entry.pack()

tk.Button(frame4, text="Calculate Company", command=calculate_company).pack(pady=5)

# RESULT
result_label = tk.Label(root, text="", bg="#eef6fb", justify="left")
result_label.pack(pady=10)

# EXTRA 
tk.Button(root, text="⭐ Top Low Emission Cars", command=show_top_cars).pack(pady=5)
tk.Button(root, text="📜 Show History", command=show_history).pack(pady=5)
tk.Button(root, text="📊 Comparison Graph", command=comparison_graph).pack(pady=5)
tk.Button(root, text="🔄 Reset", command=reset_fields).pack(pady=5)
tk.Button(root, text="❌ Exit", command=root.quit).pack(pady=5)

root.mainloop()