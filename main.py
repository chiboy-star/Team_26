import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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

    def toDict(self):
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "deadline": self.deadline.isoformat(),
            "duration": self.duration
        }

    @staticmethod
    def fromDict(data):
        return Task(
            data["title"],
            data.get("description", ""),
            data["priority"],
            datetime.datetime.fromisoformat(data["deadline"]),
            data["duration"]
        )

    def getUrgency(self):
        return (self.deadline - datetime.datetime.now()).total_seconds()

    def isOverdue(self):
        return datetime.datetime.now() > self.deadline


class SmartTaskScheduler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pan-Atlantic University - Smart Task Scheduler")
        self.geometry("1000x700")
        self.configure(bg="#FFFFFF")

        self.tasks = []
        self.data_file = "tasks.json"

        self.createWidgets()
        self.loadTasks()
        self.refreshTaskList()

    def createWidgets(self):
        inputFrame = tk.LabelFrame(self, text="Input/Edit task", padx=15, pady=15, bg="#7FE40D", fg="#FFFFFF")
        inputFrame.pack(pady=15, padx=20, fill="x", expand=False)
        inputFrame.config(font=("Inter", 15, "bold"))

        listFrame = tk.LabelFrame(self, text="Current Tasks List", padx=15, pady=15, bg="#7FE40D", fg="#FFFFFF")
        listFrame.pack(padx=10, pady=20, expand=True, fill="both")
        listFrame.config(font=("Inter", 15, "bold"))

        self.statusLabel = tk.Label(self, text="", fg="green", font=("Inter", 10))
        self.statusLabel.pack(pady=5)

        labels = ["Title:", "Description (Optional):", "Priority (1-3):", "Deadline Date (YYYY-MM-DD):", "Deadline Time (HH:MM):", "Estimated Duration (hours):"]
        self.entries = {}
        for i, labelText in enumerate(labels):
            label = tk.Label(inputFrame,text=labelText,bg="#7FE40D",fg="#FFFFFF")
            label.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            entryWidget = ttk.Entry(inputFrame, width=40, font=("Inter", 10,"bold"))
            entryWidget.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            self.entries[labelText.split(" (")[0].replace(":", "").strip().lower()] = entryWidget

        self.priorityVar = tk.StringVar(self)
        self.priorityVar.set("1")
        priorityOptions = ["1", "2", "3"]
        priorityMenu = ttk.Combobox(inputFrame, textvariable=self.priorityVar, values=priorityOptions, state="readonly", font=("Inter", 10))
        priorityMenu.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        self.entries['priority'] = priorityMenu

        self.durationVar = tk.DoubleVar(self)
        self.durationVar.set(1.0)
        durationSpinbox = tk.Spinbox(inputFrame, from_=0.1, to=999.0, increment=0.5, format="%.1f", textvariable=self.durationVar, font=("Inter", 10))
        durationSpinbox.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        self.entries['estimated duration'] = durationSpinbox

        addButton = tk.Button(inputFrame, text="Add Task", command=self.addTask)
        addButton.grid(row=len(labels), column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        columns = ("title", "priority", "deadline", "duration", "urgency")
        self.tree = ttk.Treeview(listFrame, columns=columns, show="headings", height=12)
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

        self.tree.tag_configure("overdue", background="#FFCCCC")
        self.tree.tag_configure("urgent", background="#FFF3CD")

        actionButtonsFrame = tk.Frame(listFrame, bg="#7FE40D")
        actionButtonsFrame.pack(pady=10, fill="x", expand=False)

        editButton = tk.Button(actionButtonsFrame, text="Edit Task", command=self.editTask)
        editButton.pack(side="left", padx=5, expand=True, fill="x")

        deleteButton = tk.Button(actionButtonsFrame, text="Delete Task", command=self.deleteTask)
        deleteButton.pack(side="left", padx=5, expand=True, fill="x")

        sortPriorityButton = tk.Button(actionButtonsFrame, text="Sort by Priority", command=lambda: self.sortTasks("priority"))
        sortPriorityButton.pack(side="left", padx=5, expand=True, fill="x")

        sortUrgencyButton = tk.Button(actionButtonsFrame, text="Sort by Urgency", command=lambda: self.sortTasks("urgency"))
        sortUrgencyButton.pack(side="left", padx=5, expand=True, fill="x")

        scrollbar = ttk.Scrollbar(listFrame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def validate_input(self, title, description, priority_str, date_str, time_str, duration_str):
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

    def addTask(self):
        title = self.entries['title'].get().strip()
        description = self.entries['description'].get().strip()
        priorityStr = self.priorityVar.get()
        dateStr = self.entries['deadline date'].get().strip()
        timeStr = self.entries['deadline time'].get().strip()
        durationVal = self.durationVar.get()

        isValid, validatedData = self.validate_input(title, description, priorityStr, dateStr, timeStr, str(durationVal))

        if isValid:
            new_task = Task(**validatedData)
            self.tasks.append(new_task)
            self.saveTasks()
            self.refreshTaskList()
            self.clearInputFields()
            self.statusLabel.config(text="Task added successfully!", fg="green")
        else:
            self.statusLabel.config(text="Failed to add task. Please check input.", fg="red")

    def editTask(self):
        selectedItem = self.tree.selection()
        if not selectedItem:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return

        itemId = self.tree.item(selectedItem, 'text')
        try:
            taskIndex = int(itemId) - 1 
            selectedTask = self.tasks[taskIndex]
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Could not retrieve task for editing. Please try again.")
            return

        newTitle = simpledialog.askstring("Edit Task", "New Title:", initialvalue=selectedTask.title)
        if newTitle is None: return

        newDescription = simpledialog.askstring("Edit Task", "New Description:", initialvalue=selectedTask.description)
        if newDescription is None: return

        newPriorityStr = simpledialog.askstring("Edit Task", "New Priority (1-3):", initialvalue=str(selectedTask.priority))
        if newPriorityStr is None: return

        newDateStr = simpledialog.askstring("Edit Task", "New Deadline Date (YYYY-MM-DD):", initialvalue=selectedTask.deadline.strftime("%Y-%m-%d"))
        if newDateStr is None: return

        newTimeStr = simpledialog.askstring("Edit Task", "New Deadline Time (HH:MM):", initialvalue=selectedTask.deadline.strftime("%H:%M"))
        if newTimeStr is None: return

        newDurationStr = simpledialog.askstring("Edit Task", "New Duration (hours):", initialvalue=str(selectedTask.duration))
        if newDurationStr is None: return

        isValid, validatedData = self.validate_input(newTitle, newDescription, newPriorityStr, newDateStr, newTimeStr, newDurationStr)

        if isValid:
            selectedTask.title = validatedData['title']
            selectedTask.description = validatedData['description']
            selectedTask.priority = validatedData['priority']
            selectedTask.deadline = validatedData['deadline']
            selectedTask.duration = validatedData['duration']

            self.saveTasks()
            self.refreshTaskList()
            self.statusLabel.config(text="Task updated successfully!")
        else:
            self.statusLabel.config(text="Failed to update task. Invalid input.", foreground="red")

    def deleteTask(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected task?")
        if confirm:
            item_id = self.tree.item(selected_item, 'text')
            try:
                task_index = int(item_id) - 1
                del self.tasks[task_index]
                self.saveTasks()
                self.refreshTaskList()
                self.statusLabel.config(text="Task deleted successfully!")
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Could not delete task. Please try again.")
                self.statusLabel.config(text="Error deleting task.", foreground="red")

    def refreshTaskList(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, task in enumerate(self.tasks):
            status_text = "Pending"
            tags = ("normal",)
            if task.isOverdue():
                status_text = "Overdue!"
                tags = ("overdue",)
            elif task.getUrgency() < 24 * 3600:
                status_text = "Urgent!"
                tags = ("urgent",)

            self.tree.insert("", "end", text=str(i + 1),
                             values=(
                                 task.title,
                                 task.priority,
                                 task.deadline.strftime("%Y-%m-%d %H:%M"),
                                 f"{task.duration:.1f}",
                                 status_text
                             ), tags=tags)

    def sortTasks(self, sort_by):
        if sort_by == "priority":
            self.tasks.sort(key=lambda task: task.priority)
            self.statusLabel.config(text="Tasks sorted by Priority.")
        elif sort_by == "urgency":
            self.tasks.sort(key=lambda task: task.getUrgency())
            self.statusLabel.config(text="Tasks sorted by Urgency.")
        self.refreshTaskList()

    def clearInputFields(self):
        self.entries['title'].delete(0, tk.END)
        self.entries['description'].delete(0, tk.END)
        self.priorityVar.set("1")
        self.entries['deadline date'].delete(0, tk.END)
        self.entries['deadline date'].insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.entries['deadline time'].delete(0, tk.END)
        self.entries['deadline time'].insert(0, (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M"))
        self.durationVar.set(1.0)

    def loadTasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.fromDict(d) for d in data]
                self.statusLabel.config(text=f"Loaded {len(self.tasks)} tasks from {self.data_file}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load tasks: {e}")
                self.statusLabel.config(text="Error loading tasks.", foreground="red")
        else:
            self.statusLabel.config(text="No existing tasks file found. Starting fresh.")

    def saveTasks(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump([task.toDict() for task in self.tasks], f, indent=4)
            self.statusLabel.config(text=f"Tasks saved to {self.data_file}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save tasks: {e}")
            self.statusLabel.config(text="Error saving tasks.", foreground="red")


if __name__ == "__main__":
    def startMainApp():
        welcome_window.destroy()  
        app = SmartTaskScheduler()  
        app.mainloop()

    
    welcome_window = tk.Tk()
    welcome_window.title("Welcome")
    welcome_window.geometry("400x200")
    welcome_window.configure(bg="#2B2D30")

    tk.Label(welcome_window, text="Welcome Task Master",
             font=("Helvetica", 20,"bold"),bg="#2B2D30", fg="white").pack(pady=40)

    tk.Button( welcome_window,
    text="Continue",
    font=("Helvetica", 14, "bold"),
    bg="#4CAF50",
    fg="white",
    activebackground="#45A049",
    padx=20,
    pady=10,
    bd=0,
    relief="flat",
    command=startMainApp).pack(pady=10)

    welcome_window.mainloop()