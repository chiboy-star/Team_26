import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

class Task:
    def __init__(self, title, desc, priority, deadline, duration):
        self.title = title
        self.desc = desc
        self.priority = int(priority)
        self.deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        self.duration = duration

    def urgency(self):
        return (self.deadline - datetime.now()).total_seconds()

    def __str__(self):
        status = "⚠️ OVERDUE" if self.urgency() < 0 else ""
        return f"{self.title} | Priority: {self.priority} | {self.deadline.strftime('%Y-%m-%d %H:%M')} {status}"

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Task Scheduler")
        self.root.geometry("700x450")
        self.root.configure(bg="#e6f0ff")  # Light blue background
        self.fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.tasks = []

        self.task_listbox = tk.Listbox(root, font=("Poppins", 12), bg="white", fg="black", selectbackground="#cce0ff", height=15)
        self.task_listbox.pack(fill="both", expand=True, padx=15, pady=(15, 5))

        btn_frame = tk.Frame(root, bg="#e6f0ff")
        btn_frame.pack(pady=10)

        # Add normal buttons
        self.make_button(btn_frame, "Add", self.add_task, "#66b3ff")
        self.make_button(btn_frame, "Edit", self.edit_task, "#66b3ff")
        self.make_button(btn_frame, "Sort by Priority", self.sort_priority, "#66b3ff")
        self.make_button(btn_frame, "Sort by Urgency", self.sort_urgency, "#66b3ff")

        # Add red delete button last
        self.make_button(btn_frame, "Delete", self.delete_task, "#ff6666")

    def make_button(self, frame, text, command, color):
        tk.Button(frame, text=text, command=command, bg=color, fg="white", width=15, relief="raised").pack(side="left", padx=6)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    def add_task(self):
        title = simpledialog.askstring("Task Title", "Enter title:")
        if not title:
            return
        desc = simpledialog.askstring("Description", "Optional description:")
        try:
            priority = simpledialog.askinteger("Priority", "1 = High, 2 = Medium, 3 = Low:")
            deadline = simpledialog.askstring("Deadline", "Format: YYYY-MM-DD HH:MM")
            duration = simpledialog.askstring("Duration", "e.g., 2 hours")
            new_task = Task(title, desc, priority, deadline, duration)
            self.tasks.append(new_task)
            self.refresh_list()
        except:
            messagebox.showerror("Error", "Invalid input!")

    def edit_task(self):
        i = self.task_listbox.curselection()
        if not i:
            return
        task = self.tasks[i[0]]
        title = simpledialog.askstring("Edit Title", "Title:", initialvalue=task.title)
        if not title:
            return
        desc = simpledialog.askstring("Edit Description", "Description:", initialvalue=task.desc)
        try:
            priority = simpledialog.askinteger("Edit Priority", "1 = High, 2 = Medium, 3 = Low:", initialvalue=task.priority)
            deadline = simpledialog.askstring("Edit Deadline", "Format: YYYY-MM-DD HH:MM", initialvalue=task.deadline.strftime("%Y-%m-%d %H:%M"))
            duration = simpledialog.askstring("Edit Duration", "e.g., 2 hours", initialvalue=task.duration)
            self.tasks[i[0]] = Task(title, desc, priority, deadline, duration)
            self.refresh_list()
        except:
            messagebox.showerror("Error", "Invalid input!")

    def delete_task(self):
        i = self.task_listbox.curselection()
        if i:
            del self.tasks[i[0]]
            self.refresh_list()

    def sort_priority(self):
        self.tasks.sort(key=lambda t: t.priority)
        self.refresh_list()

    def sort_urgency(self):
        self.tasks.sort(key=lambda t: t.urgency())
        self.refresh_list()

    def refresh_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, str(task))

root = tk.Tk()
app = TaskApp(root)
root.mainloop()
