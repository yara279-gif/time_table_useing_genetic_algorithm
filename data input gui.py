
from tkinter import *
import sqlite3

def create_table():
    """Create the selected table in the database."""
    selected_option = selected.get()

    conn = sqlite3.connect("mydatabase.db")
    c = conn.cursor()

    if selected_option == "Courses":
        c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT,
            time_per_week INTEGER,
            level INTEGER,
            no_student INTEGER
        )
        """)
        message_label.config(text="Courses table created!")
    elif selected_option == "Lecturers":
        c.execute("""
        CREATE TABLE IF NOT EXISTS lecturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lec_name TEXT
        )
        """)
        message_label.config(text="Lecturers table created!")
    elif selected_option == "Rooms":
        c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT,
            capacity INTEGER
        )
        """)
        message_label.config(text="Rooms table created!")
    elif selected_option == "Timeslots":
        c.execute("""
        CREATE TABLE IF NOT EXISTS timeslots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            hour INTEGER,
            typee TEXT
        )
        """)
        message_label.config(text="Timeslots table created!")
    else:
        message_label.config(text="Please select a valid option!")

    conn.commit()
    conn.close()

def open_input_window():
    """Open a new window to input data for the selected table."""
    selected_option = selected.get()
    if selected_option == "Select one option":
        message_label.config(text="Please select an option first!")
        return

    input_window = Toplevel(home_win)
    input_window.title(f"Add Data to {selected_option}")
    input_window.geometry("400x300")

    entries = []  # To store input widgets dynamically

    # Dynamically generate input fields based on the selected table
    if selected_option == "Courses":
        fields = ["Course Name", "Time Per Week", "Level", "No. of Students"]
    elif selected_option == "Lecturers":
        fields = ["Lecturer Name"]
    elif selected_option == "Rooms":
        fields = ["Room Name","capacity"]
    elif selected_option == "Timeslots":
        fields = ["Day", "Hour", "Type"]
    else:
        fields = []

    # Create input fields
    for field in fields:
        label = Label(input_window, text=field)
        label.pack(pady=5)
        entry = Entry(input_window)
        entry.pack(pady=5)
        entries.append(entry)

    def save_data():
        """Save the entered data into the selected table."""
        conn = sqlite3.connect("mydatabase.db")
        c = conn.cursor()

        # Collect input values
        values = [entry.get() for entry in entries]

        # Insert into the appropriate table
        if selected_option == "Courses":
            c.execute("""
            INSERT INTO courses (course_name, time_per_week, level, no_student)
            VALUES (?, ?, ?, ?)
            """, values)
        elif selected_option == "Lecturers":
            c.execute("INSERT INTO lecturers (lec_name) VALUES (?)", values)
        elif selected_option == "Rooms":
            c.execute("INSERT INTO rooms (room_name,capacity) VALUES (?,?)", values)
        elif selected_option == "Timeslots":
            c.execute("INSERT INTO timeslots (day, hour, typee) VALUES (?, ?, ?)", values)

        conn.commit()
        conn.close()
        input_window.destroy()
        message_label.config(text=f"Data added to {selected_option}!")

    # Save Button
    save_button = Button(input_window, text="Save", command=save_data)
    save_button.pack(pady=20)

# Main Window
home_win = Tk()
home_win.title("Home Selection")
home_win.geometry("300x200")

# Dropdown Menu for selecting an option
options = ["Courses", "Lecturers", "Rooms", "Timeslots"]
selected = StringVar(home_win)
selected.set("Select one option")
dropdown = OptionMenu(home_win, selected, *options)
dropdown.pack(pady=10)

# Buttons for table creation and data entry
create_button = Button(home_win, text="Create Table", command=create_table)
create_button.pack(pady=10)

input_button = Button(home_win, text="Add Data", command=open_input_window)
input_button.pack(pady=10)

# Message Label for feedback
message_label = Label(home_win, text="")
message_label.pack(pady=10)

# Start the GUI event loop
home_win.mainloop()
