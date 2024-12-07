import random
import sqlite3
import tkinter as tk
from tkinter import ttk

# Database Connection and Data Fetching
def load_data():
    conn = sqlite3.connect("mydatabase.db")
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        c.execute("SELECT * FROM lecturers")
        lecturers = c.fetchall()
        c.execute("SELECT * FROM rooms")
        rooms = c.fetchall()
        c.execute("SELECT * FROM timeslots")
        timeslots = c.fetchall()
    except sqlite3.Error as e:
        print("Error loading data:", e)
        return None, None, None, None
    finally:
        conn.close()
    return courses, lecturers, rooms, timeslots


# Genetic Algorithm Parameters
POP_SIZE = 100
GENERATIONS = 50
MUTATION_RATE = 0.05
TOURNAMENT_SIZE = 5


# Initialize Chromosome
def create_chromosome(courses, lecturers, rooms, timeslots):
    return [[course, random.choice(lecturers), random.choice(rooms), random.choice(timeslots)] for course in courses]


# Initialize Population
def create_population(pop_size, courses, lecturers, rooms, timeslots):
    return [create_chromosome(courses, lecturers, rooms, timeslots) for _ in range(pop_size)]


# Fitness Function
def fitness(chromosome):
    hard_violations = 0
    soft_violations = 0

    for i, (course1, lecturer1, room1, timeslot1) in enumerate(chromosome):
        for j, (course2, lecturer2, room2, timeslot2) in enumerate(chromosome):
            if i == j:
                continue

            # Hard Constraints
            if lecturer1 == lecturer2 and timeslot1 == timeslot2:
                hard_violations += 1  # Lecturer conflict
            if room1 == room2 and timeslot1 == timeslot2:
                hard_violations += 1  # Room conflict
            if room1[2] < course1[4]:  # Room capacity constraint
                hard_violations += 1
            if course1[3] == course2[3] and timeslot1 == timeslot2:
                hard_violations += 1  # Student group conflict

            # Soft Constraints
            if timeslot1[1] != timeslot2[1]:
                time1 = timeslot1[2] + (12 if timeslot1[3] == "PM" else 0)
                time2 = timeslot2[2] + (12 if timeslot2[3] == "PM" else 0)
                gap = abs(time1 - time2)
                if gap >= 4:
                    soft_violations += 1

    return 1 / (1 + hard_violations + 0.5 * soft_violations)


# Crossover Function
def crossover(parents, segment_lengths):
    parent1, parent2 = parents
    child = []
    start = 0
    for length in segment_lengths:
        if random.random() < 0.5:
            child.extend(parent1[start : start + length])
        else:
            child.extend(parent2[start : start + length])
        start += length
    return child


# Mutation Function
def mutate(chromosome, timeslots):
    if random.random() < MUTATION_RATE:
        gene_index = random.randint(0, len(chromosome) - 1)
        chromosome[gene_index][3] = random.choice(timeslots)  # Mutate timeslot
    return chromosome


# Genetic Algorithm
def genetic_algorithm(pop_size, generations, courses, lecturers, rooms, timeslots):
    population = create_population(pop_size, courses, lecturers, rooms, timeslots)

    for generation in range(generations):
        # Evaluate Fitness
        population = sorted(population, key=lambda x: fitness(x), reverse=True)

        # Select Top Half of Population
        next_generation = population[:pop_size // 2]

        # Generate Offspring via Crossover and Mutation
        while len(next_generation) < pop_size:
            parents = random.sample(next_generation, 2)
            segment_lengths = [len(courses) // 2, len(courses) - len(courses) // 2]
            child = crossover(parents, segment_lengths)
            next_generation.append(mutate(child, timeslots))

        population = next_generation
        print(f"Generation {generation + 1}: Best Fitness = {fitness(population[0]):.4f}")

    return population[0]  # Return the best chromosome


# Main Program
courses, lecturers, rooms, timeslots = load_data()
if not (courses and lecturers and rooms and timeslots):
    print("Error: Missing or invalid data from the database.")
else:
    best_timetable = genetic_algorithm(POP_SIZE, GENERATIONS, courses, lecturers, rooms, timeslots)
    print("Best Timetable:", best_timetable)
    
def display_timetable(timetable):
    root = tk.Tk()
    root.title("Generated Timetable")
    root.geometry("1200x600")  # Increased width for better display of data
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # Styling the Treeview
    style = ttk.Style(root)
    style.theme_use("clam")  # Use 'clam' theme for better visuals
    style.configure(
        "Treeview",
        background="white",
        foreground="black",
        rowheight=25,
        fieldbackground="white",
        borderwidth=1
    )
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    # Frame for Treeview and Scrollbars
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Treeview to display timetable
    columns = ("Course", "Lecturer", "Room", "Day", "Time")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)

    # Add vertical and horizontal scrollbars
    v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)

    # Place Treeview and scrollbars in the frame
    tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    # Configure frame to expand with window resizing
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    # Set up column headings with customization
    for col in columns:
        tree.heading(col, text=col, anchor="center")  # Center-align headings
        tree.column(col, anchor="center", width=200)  # Adjust width for readability

    # Insert timetable data into Treeview
    for gene in timetable:
        course, lecturer, room, timeslot = gene
        # Debugging print for each inserted row
        print(f"Inserting: Course={course[1]}, Lecturer={lecturer[1]}, Room={room[1]}, Day={timeslot[1]}, Time={timeslot[2]} {timeslot[3]}")
        tree.insert("", "end", values=(
            course[1],  # Course name
            lecturer[1],  # Lecturer name
            room[1],  # Room name
            timeslot[1],  # Day
            f"{timeslot[2]} {timeslot[3]}"  # Time (e.g., 9 AM)
        ))

    # Run the Tkinter loop
    root.mainloop()
display_timetable(best_timetable)
