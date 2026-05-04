import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data/weather.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Weather Diary — Дневник погоды")
        self.root.geometry("800x550")
        self.root.resizable(False, False)

        self.records = []
        self.load_data()

        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.temp_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.precipitation_var = tk.StringVar(value="Нет")
        self.filter_date_var = tk.StringVar()
        self.filter_temp_var = tk.StringVar()
        self.filter_temp_operator = tk.StringVar(value=">")

        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        input_frame = ttk.LabelFrame(self.root, text="➕ Добавить запись о погоде", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, textvariable=self.temp_var, width=8)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Описание:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, textvariable=self.description_var, width=20)
        self.desc_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(input_frame, text="Осадки:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.precip_combo = ttk.Combobox(input_frame, textvariable=self.precipitation_var, values=["Нет", "Дождь", "Снег", "Град", "Морось"], width=8)
        self.precip_combo.grid(row=0, column=7, padx=5, pady=5)

        add_btn = ttk.Button(input_frame, text="🌤️ Добавить", command=self.add_record)
        add_btn.grid(row=0, column=8, padx=10, pady=5)

        filter_frame = ttk.LabelFrame(self.root, text="🔍 Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").pack(side="left", padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=12)
        self.filter_date_entry.pack(side="left", padx=5)

        ttk.Label(filter_frame, text="Температура:").pack(side="left", padx=5)
        self.filter_temp_op = ttk.Combobox(filter_frame, textvariable=self.filter_temp_operator, values=[">", ">=", "=", "<=", "<"], width=3)
        self.filter_temp_op.pack(side="left", padx=2)
        self.filter_temp_entry = ttk.Entry(filter_frame, textvariable=self.filter_temp_var, width=6)
        self.filter_temp_entry.pack(side="left", padx=2)

        filter_btn = ttk.Button(filter_frame, text="🔍 Применить", command=self.apply_filter)
        filter_btn.pack(side="left", padx=5)

        reset_btn = ttk.Button(filter_frame, text="❌ Сбросить", command=self.reset_filter)
        reset_btn.pack(side="left", padx=5)

        columns = ("id", "date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=18)
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("id", width=40)
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=80)
        self.tree.column("description", width=250)
        self.tree.column("precipitation", width=80)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        delete_btn = ttk.Button(btn_frame, text="🗑️ Удалить выбранное", command=self.delete_record)
        delete_btn.pack(side="left", padx=5)

        stats_btn = ttk.Button(btn_frame, text="📊 Статистика", command=self.show_stats)
        stats_btn.pack(side="left", padx=5)

        avg_btn = ttk.Button(btn_frame, text="🌡️ Средняя температура", command=self.show_avg_temp)
        avg_btn.pack(side="left", padx=5)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return False

    def validate_temperature(self, temp_str):
        try:
            temp = float(temp_str)
            if temp < -90 or temp > 60:
                raise ValueError("Температура должна быть от -90°C до +60°C")
            return temp
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректная температура: {e}")
            return None

    def add_record(self):
        date_str = self.date_var.get().strip()
        temp_str = self.temp_var.get().strip()
        description = self.description_var.get().strip()
        precipitation = self.precipitation_var.get()

        if not self.validate_date(date_str):
            return

        temp = self.validate_temperature(temp_str)
        if temp is None:
            return

        if not description:
            messagebox.showerror("Ошибка", "Введите описание погоды")
            return

        new_id = max([r["id"] for r in self.records], default=0) + 1
        record = {
            "id": new_id,
            "date": date_str,
            "temperature": temp,
            "description": description,
            "precipitation": precipitation
        }
        self.records.append(record)
        self.save_data()
        self.refresh_table()
        self.temp_var.set("")
        self.description_var.set("")
        self.precipitation_var.set("Нет")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        messagebox.showinfo("Успех", "Запись о погоде добавлена")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]
        record_date = item["values"][1]

        if messagebox.askyesno("Подтверждение", f"Удалить запись от {record_date}?"):
            self.records = [r for r in self.records if r["id"] != record_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Запись удалена")

    def apply_filter(self):
        filter_date = self.filter_date_var.get().strip()
        filter_temp_str = self.filter_temp_var.get().strip()
        filter_op = self.filter_temp_operator.get()

        filtered = self.records.copy()

        if filter_date:
            if self.validate_date(filter_date):
                filtered = [r for r in filtered if r["date"] == filter_date]
            else:
                return

        if filter_temp_str:
            try:
                filter_temp = float(filter_temp_str)
                if filter_op == ">":
                    filtered = [r for r in filtered if r["temperature"] > filter_temp]
                elif filter_op == ">=":
                    filtered = [r for r in filtered if r["temperature"] >= filter_temp]
                elif filter_op == "=":
                    filtered = [r for r in filtered if r["temperature"] == filter_temp]
                elif filter_op == "<=":
                    filtered = [r for r in filtered if r["temperature"] <= filter_temp]
                elif filter_op == "<":
                    filtered = [r for r in filtered if r["temperature"] < filter_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура для фильтрации должна быть числом")
                return

        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_date_var.set("")
        self.filter_temp_var.set("")
        self.filter_temp_operator.set(">")
        self.refresh_table()

    def refresh_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if data is None:
            data = self.records

        for record in data:
            temp_icon = "🔥" if record["temperature"] > 25 else "☀️" if record["temperature"] > 15 else "🌤️" if record["temperature"] > 5 else "❄️" if record["temperature"] < 0 else "🌡️"
            precip_icon = "☔" if record["precipitation"] in ["Дождь", "Морось"] else "❄️" if record["precipitation"] == "Снег" else "💧" if record["precipitation"] == "Град" else "☀️"
            
            self.tree.insert("", "end", values=(
                record["id"],
                record["date"],
                f"{temp_icon} {record['temperature']:.1f}°C",
                record["description"],
                f"{precip_icon} {record['precipitation']}"
            ))

    def show_stats(self):
        if not self.records:
            messagebox.showinfo("Статистика", "Нет записей в дневнике")
            return

        total = len(self.records)
        rainy_days = len([r for r in self.records if r["precipitation"] in ["Дождь", "Морось"]])
        snowy_days = len([r for r in self.records if r["precipitation"] == "Снег"])
        sunny_days = len([r for r in self.records if r["precipitation"] == "Нет"])
        max_temp = max(self.records, key=lambda x: x["temperature"])
        min_temp = min(self.records, key=lambda x: x["temperature"])

        stats = f"""📊 Статистика дневника погоды:

📅 Всего записей: {total}
☀️ Солнечных дней: {sunny_days}
☔ Дождливых дней: {rainy_days}
❄️ Снежных дней: {snowy_days}

🌡️ Самая высокая температура: {max_temp['temperature']:.1f}°C ({max_temp['date']})
🥶 Самая низкая температура: {min_temp['temperature']:.1f}°C ({min_temp['date']})"""

        messagebox.showinfo("Статистика", stats)

    def show_avg_temp(self):
        if not self.records:
            messagebox.showinfo("Средняя температура", "Нет записей")
            return

        avg_temp = sum(r["temperature"] for r in self.records) / len(self.records)
        messagebox.showinfo("Средняя температура", f"🌡️ Средняя температура за все время: {avg_temp:.1f}°C")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.records = []
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.records = []

    def save_data(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)