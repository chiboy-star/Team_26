import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os

class Task:
    def __init__(self, title, description, priority, deadline, duration):
        self.title = title
        self.description = description
        self.priority = int(priority)
        self.deadline = deadline
        self.duration = float(duration)

class SmartTaskScheduler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pan-Atlantic University - Smart Task Scheduler")
        self.geometry("1000x700")
        self.configure(bg="#F0F2F5")

        self.tasks = []
        self.data_file = "tasks.json"

        self._create_widgets()
        self._load_tasks()
        self._refresh_task_list()

    def _create_widgets(self):
        input_frame = tk.LabelFrame(self, text="Input/Edit task", padx=15, pady=15, bg="#FFFFFF", fg="#333333")
        input_frame.pack(pady=15, padx=20, fill="x", expand=False)

        list_frame = tk.LabelFrame(self, text="Current Tasks List", padx=15, pady=15, bg="#FFFFFF", fg="#333333")
        list_frame.pack(padx=10, pady=20, expand=True, fill="both")

        self.status_label = tk.Label(self, text="", fg="green", font=("Inter", 10))
        self.status_label.pack(pady=5)

        labels = ["Title:", "Description (Optional):", "Priority (1-3):", "Deadline Date (YYYY-MM-DD):", "Deadline Time (HH:MM):", "Estimated Duration (hours):"]
        self.entries = {}
        for i, label_text in enumerate(labels):
            label = ttk.Label(input_frame, text=label_text, background="#FFFFFF", font=("Inter", 10))
            label.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            entry_widget = ttk.Entry(input_frame, width=40, font=("Inter", 10))
            entry_widget.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            self.entries[label_text.split(" (")[0].replace(":", "").strip().lower()] = entry_widget

        self.priority_var = tk.StringVar(self)
        self.priority_var.set("1")
        priority_options = ["1", "2", "3"]
        priority_menu = ttk.Combobox(input_frame, textvariable=self.priority_var, values=priority_options, state="readonly", font=("Inter", 10))
        priority_menu.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        self.entries['priority'] = priority_menu

        self.duration_var = tk.DoubleVar(self)
        self.duration_var.set(1.0)
        duration_spinbox = tk.Spinbox(input_frame, from_=0.1, to=999.0, increment=0.5, format="%.1f", textvariable=self.duration_var, font=("Inter", 10))
        duration_spinbox.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        self.entries['estimated duration'] = duration_spinbox

        add_button = tk.Button(input_frame, text="Add Task", command=self._add_task)
        add_button.grid(row=len(labels), column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        columns = ("title", "priority", "deadline", "duration", "urgency")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.tree.heading("title", text="Title")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("deadline", text="Deadline")
        self.tree.heading("duration", text="Duration (hrs)")
        self.tree.heading("urgency", text="Urgency Level")

        self.tree.column("title", width=150, anchor="center")
        self.tree.column("priority", width=80, anchor="center")
        self.tree.column("deadline", width=130, anchor="center")
        self.tree.column("duration", width=110, anchor="center")
        self.tree.column("urgency", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _validate_input(self, title, description, priority_str, date_str, time_str, duration_str):
        if not title:
            messagebox.showerror("Input Error", "Task Title cannot be empty.")
            return False, None

        try:
            priority = int(priority_str)
            if not (1 <= priority <= 3):
                messagebox.showerror("Input Error", "Priority must be 1 (High), 2 (Medium), or 3 (Low).")
                return False, None
        except ValueError:
            messagebox.showerror("Input Error", "Priority must be a number.")
            return False, None

        try:
            deadline_str = f"{date_str} {time_str}"
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid Date or Time format. Use YYYY-MM-DD and HH:MM.")
            return False, None

        try:
            duration = float(duration_str)
            if duration <= 0:
                messagebox.showerror("Input Error", "Estimated Duration must be a positive number.")
                return False, None
        except ValueError:
            messagebox.showerror("Input Error", "Estimated Duration must be a number.")
            return False, None

        return True, {
            "title": title,
            "description": description,
            "priority": priority,
            "deadline": deadline,
            "duration": duration
        }

    def _add_task(self):
        title = self.entries['title'].get().strip()
        description = self.entries['description'].get().strip()
        priority_str = self.priority_var.get()
        date_str = self.entries['deadline date'].get().strip()
        time_str = self.entries['deadline time'].get().strip()
        duration_str = self.duration_var.get()

        is_valid, validated_data = self._validate_input(title, description, priority_str, date_str, time_str, duration_str)

        if is_valid:
            new_task = Task(**validated_data)
            self.tasks.append(new_task)
            self._save_tasks()
            self._refresh_task_list()
            self._clear_input_fields()
            self.status_label.config(text="Task added successfully!", fg="green")
        else:
            self.status_label.config(text="Failed to add task. Please check input.", fg="red")

    def _calculate_urgency(self, task):
        now = datetime.datetime.now()
        time_left_hours = (task.deadline - now).total_seconds() / 3600

        if time_left_hours <= 0:
            return "Overdue"
        elif task.priority == 1 and time_left_hours < 24:
            return "Critical"
        elif task.priority == 2 and time_left_hours < 48:
            return "High"
        else:
            return "Normal"

    def _refresh_task_list(self):
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            urgency = self._calculate_urgency(task)
            self.tree.insert("", "end", values=(
                task.title,
                task.priority,
                task.deadline.strftime("%Y-%m-%d %H:%M"),
                f"{task.duration:.1f}",
                urgency
            ))

    def _clear_input_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.priority_var.set("1")
        self.duration_var.set(1.0)

    def _save_tasks(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump([{
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "deadline": t.deadline.isoformat(),
                    "duration": t.duration
                } for t in self.tasks], f)
        except Exception as e:
            print("Failed to save tasks:", e)

    def _load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    tasks_data = json.load(f)
                    for t in tasks_data:
                        deadline = datetime.datetime.fromisoformat(t["deadline"])
                        task = Task(t["title"], t["description"], t["priority"], deadline, t["duration"])
                        self.tasks.append(task)
            except Exception as e:
                print("Failed to load tasks:", e)


app = SmartTaskScheduler()
app.mainloop()
