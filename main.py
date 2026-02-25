import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk


class HospitalQueueSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("MediQueue")
        self.root.geometry("1366x745")
        self.root.configure(bg="#003366")
        self.root.state("zoomed")

        self.conn = sqlite3.connect("hospital_queue.db")
        self.cursor = self.conn.cursor()

        self.widgets = {}
        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        self.header = tk.Frame(self.root, bg="#003366", height=80)
        self.header.place(x=0, y=10, width=1366, height=80)

        title = tk.Label(
            self.header,
            text="MediQueue",
            font=("Arial", 20, "bold"),
            bg="#003366",
            fg="white",
        )
        title.place(width=200, height=30, x=583, y=25)

        img = Image.open("logo.png")
        img = img.resize((100, 100), Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(img)
        self.logo_label = tk.Label(self.header, image=self.logo, background="#003366")
        self.logo_label.place(x=10, y=-10, width=100, height=100)

        notebook_frame = tk.Frame(self.root, bg="#F5F5FF")
        notebook_frame.place(x=20, y=90, width=1326, height=635)

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.place(x=0, y=0, width=1326, height=635)

        # TAB 1: REGISTRATION
        self.reg_frame = tk.Frame(self.notebook, bg="#F5F5FF")
        self.notebook.add(self.reg_frame, text="👤 Patient Registration")
        self.setup_registration_tab()

        # TAB 2: QUEUES
        self.queue_frame = tk.Frame(self.notebook, bg="#F5F5FF")
        self.notebook.add(self.queue_frame, text="📋 Doctor Queues")
        self.setup_queue_tab()

        # TAB 3: SEARCH
        self.search_frame = tk.Frame(self.notebook, bg="#F5F5FF")
        self.notebook.add(self.search_frame, text="🔍 Search")
        self.setup_search_tab()

        # TAB 4: SUMMARY
        self.summary_frame = tk.Frame(self.notebook, bg="#F5F5FF")
        self.notebook.add(self.summary_frame, text="📊 Summary")
        self.setup_summary_tab()

    def setup_registration_tab(self):
        form_frame = tk.LabelFrame(
            self.reg_frame,
            text="Register New Patient",
            font=("Arial", 12, "bold"),
            bg="#F5F5FF",
            fg="#003366",
        )
        form_frame.place(x=20, y=20, width=450, height=300)

        # Name Label & Entry
        tk.Label(
            form_frame, text="Patient Name:", font=("Arial", 12), bg="#F5F5FF"
        ).place(x=20, y=30)
        self.widgets["name_entry"] = tk.Entry(form_frame, font=("Arial", 12), width=25)
        self.widgets["name_entry"].place(x=150, y=30, width=250, height=30)

        # Age Label & Entry
        tk.Label(form_frame, text="Age:", font=("Arial", 12), bg="#F5F5FF").place(
            x=20, y=80
        )
        self.age_var = tk.StringVar()
        self.widgets["age_entry"] = tk.Entry(
            form_frame, textvariable=self.age_var, font=("Arial", 12), width=8
        )
        self.widgets["age_entry"].place(x=150, y=80, width=60, height=30)

        # Doctor Label & Combo
        tk.Label(form_frame, text="Doctor:", font=("Arial", 12), bg="#F5F5FF").place(
            x=20, y=130
        )
        self.widgets["doctor_combo"] = ttk.Combobox(
            form_frame, font=("Arial", 12), width=24, state="readonly"
        )
        self.widgets["doctor_combo"].place(x=150, y=130, width=250, height=30)

        # Register Button
        reg_btn = tk.Button(
            form_frame,
            text="Register & Assign Token",
            command=self.register_patient,
            bg="#32CD32",
            fg="white",
            font=("Arial", 14, "bold"),
        )
        reg_btn.place(x=100, y=180, width=250, height=40)

        status_frame = tk.LabelFrame(
            self.reg_frame,
            text="Registration Status",
            font=("Arial", 12, "bold"),
            bg="#F5F5FF",
            fg="#003366",
        )
        status_frame.place(x=500, y=20, width=800, height=300)
        self.widgets["status_text"] = tk.Text(
            status_frame, font=("Arial", 10), bg="#E8F4F8", state="disabled"
        )
        self.widgets["status_text"].place(x=20, y=10, width=750, height=250)

    def setup_queue_tab(self):
        table_frame = tk.LabelFrame(
            self.queue_frame,
            text="Live Doctor Queues",
            font=("Arial", 12, "bold"),
            bg="#F5F5FF",
            fg="#003366",
        )
        table_frame.place(x=20, y=20, width=1280, height=500)

        columns = ("Doctor", "Token", "Patient", "Age", "Status", "Time")
        self.widgets["queue_tree"] = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=18
        )

        for col in columns:
            self.widgets["queue_tree"].heading(col, text=col)
            self.widgets["queue_tree"].column(col, width=180)

        self.widgets["queue_tree"].place(x=20, y=10, width=1240, height=450)

        btn_frame = tk.Frame(self.queue_frame, bg="#F5F5FF")
        btn_frame.place(x=20, y=520, width=600, height=80)

        tk.Button(
            btn_frame,
            text="Call Next Patient",
            command=self.call_next_patient,
            bg="#FF8C00",
            fg="white",
            font=("Arial", 12, "bold"),
        ).place(x=0, y=20, width=180, height=40)
        tk.Button(
            btn_frame,
            text="Mark Consulted",
            command=self.mark_consulted,
            bg="#32CD32",
            fg="white",
            font=("Arial", 12, "bold"),
        ).place(x=200, y=20, width=180, height=40)
        tk.Button(
            btn_frame,
            text="Refresh Queues",
            command=self.refresh_queues,
            bg="#4682B4",
            fg="white",
            font=("Arial", 12, "bold"),
        ).place(x=400, y=20, width=180, height=40)

    def setup_search_tab(self):
        tk.Label(
            self.search_frame,
            text="Search by Name or Token",
            font=("Arial", 16, "bold"),
            bg="#F5F5FF",
            fg="#003366",
        ).place(x=20, y=20)

        self.widgets["search_entry"] = tk.Entry(
            self.search_frame, font=("Arial", 14), width=50
        )
        self.widgets["search_entry"].place(x=20, y=70, width=600, height=40)

        tk.Button(
            self.search_frame,
            text="Search",
            command=self.search_patient,
            bg="#4682B4",
            fg="white",
            font=("Arial", 14, "bold"),
        ).place(x=640, y=70, width=120, height=40)

        results_frame = tk.LabelFrame(
            self.search_frame,
            text="Search Results",
            font=("Arial", 12, "bold"),
            bg="#F5F5FF",
        )
        results_frame.place(x=20, y=140, width=1280, height=450)
        self.widgets["search_result"] = tk.Text(
            results_frame, font=("Arial", 11), bg="#E8F4F8", state="disabled"
        )
        self.widgets["search_result"].place(x=10, y=10, width=1250, height=400)

    def setup_summary_tab(self):
        summary_frame = tk.LabelFrame(
            self.summary_frame,
            text="Daily Summary & Analytics",
            font=("Arial", 14, "bold"),
            bg="#F5F5FF",
        )
        summary_frame.place(x=20, y=20, width=1280, height=560)
        self.widgets["summary_text"] = tk.Text(
            summary_frame, font=("Arial", 12), bg="#E8F4F8", state="disabled"
        )
        self.widgets["summary_text"].place(x=10, y=10, width=1250, height=500)

    def get_doctors(self):
        self.cursor.execute("SELECT doctor_id,doctor_name FROM doctors")
        doctors = self.cursor.fetchall()
        return [f"{name} (ID:{doc_id})" for doc_id, name in doctors]

    def register_patient(self):
        name = self.widgets["name_entry"].get().strip()
        age = self.widgets["age_entry"].get().strip()

        if not name or not age.isdigit():
            messagebox.showerror("Error", "Please enter valid name and age!")
            return

        doctor_text = self.widgets["doctor_combo"].get()
        if not doctor_text:
            messagebox.showerror("Error", "Please select a doctor!")
            return

        doctor_id = int(doctor_text.split("ID:")[1].strip("()"))

        self.cursor.execute(
            "SELECT next_token FROM doctors WHERE doctor_id=?", (doctor_id,)
        )
        next_token = self.cursor.fetchone()[0]

        reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            """
            INSERT INTO patients (name, age, doctor_id, token_number, registration_time)
            VALUES (?, ?, ?, ?, ?)""",
            (name, int(age), doctor_id, next_token, reg_time),
        )

        self.cursor.execute(
            "UPDATE doctors SET next_token=next_token + 1 WHERE doctor_id=?",
            (doctor_id,),
        )
        self.conn.commit()

        self.update_status(f"'{name}' registered! Token: #{next_token}")
        self.refresh_all()
        self.widgets["name_entry"].delete(0, "end")
        self.widgets["age_entry"].delete(0, "end")

    def update_status(self, message):
        status_text = self.widgets["status_text"]
        status_text.config(state="normal")
        status_text.insert(
            "end", f"{datetime.now().strftime('%H:%M:%S')} - {message}\n"
        )
        status_text.see("end")
        status_text.config(state="disabled")

    def refresh_queues(self):
        tree = self.widgets["queue_tree"]
        for item in tree.get_children():
            tree.delete(item)

        self.cursor.execute("""
            SELECT d.doctor_name, p.token_number, p.name, p.age, p.status, p.registration_time
            FROM patients p JOIN doctors d ON p.doctor_id = d.doctor_id
            WHERE p.status != 'Consulted'
            ORDER BY d.doctor_name, p.token_number
        """)

        for row in self.cursor.fetchall():
            tree.insert("", "end", values=row)

    def refresh_all(self):
        self.widgets["doctor_combo"]["values"] = self.get_doctors()
        self.refresh_queues()
        self.update_summary()

    def call_next_patient(self):
        tree = self.widgets["queue_tree"]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a patient!")
            return

        values = tree.item(selected[0])["values"]
        self.cursor.execute(
            "UPDATE patients SET status='Called' WHERE token_number=? AND name=?",
            (values[1], values[2]),
        )
        self.conn.commit()
        self.refresh_queues()
        messagebox.showinfo("Called", f"Calling {values[2]} (#{values[1]})")

    def mark_consulted(self):
        tree = self.widgets["queue_tree"]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a patient!")
            return

        values = tree.item(selected[0])["values"]
        self.cursor.execute(
            "UPDATE patients SET status='Consulted' WHERE token_number=? AND name=?",
            (values[1], values[2]),
        )
        self.conn.commit()
        self.refresh_queues()
        self.update_summary()
        messagebox.showinfo("Consulted", f"{values[2]} (#{values[1]}) consulted!")

    def search_patient(self):
        query = self.widgets["search_entry"].get().lower()
        result_text = self.widgets["search_result"]
        result_text.config(state="normal")
        result_text.delete(1.0, "end")

        self.cursor.execute(
            """
            SELECT p.name, p.age, d.doctor_name, p.token_number, p.status, p.registration_time
            FROM patients p JOIN doctors d ON p.doctor_id = d.doctor_id
            WHERE LOWER(p.name) LIKE ? OR CAST(p.token_number AS TEXT) LIKE ?
        """,
            (f"%{query}%", f"%{query}%"),
        )

        for row in self.cursor.fetchall():
            result_text.insert(
                "end",
                f"Token #{row[3]} | {row[0]} ({row[1]}y) | {row[2]} | {row[4]} | {row[5]}\n",
            )

        result_text.config(state="disabled")

    def update_summary(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT COUNT(*) FROM patients WHERE status='Consulted'")
        consulted = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM patients WHERE status != 'Consulted'")
        waiting = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT d.doctor_name, COUNT(p.patient_id) 
            FROM doctors d LEFT JOIN patients p ON d.doctor_id = p.doctor_id AND p.status != 'Consulted'
            GROUP BY d.doctor_id
        """)
        stats = self.cursor.fetchall()

        summary = f"SUMMARY - {today}\nWaiting: {waiting} | Consulted: {consulted}\n\nDoctor Queues:\n"
        for doc, count in stats:
            summary += f"• {doc}: {count}\n"

        text_widget = self.widgets["summary_text"]
        text_widget.config(state="normal")
        text_widget.delete(1.0, "end")
        text_widget.insert("end", summary)
        text_widget.config(state="disabled")

    def __del__(self):
        self.conn.close()


def main():
    root = tk.Tk()
    app = HospitalQueueSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
