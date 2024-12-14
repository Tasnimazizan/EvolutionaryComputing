iimport csv
import random
import streamlit as st
import pandas as pd

st.header("TV Scheduling using Genetic Algorithm")

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path, rating_column):
    program_ratings = {}
    
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header row
        
        rating_index = header.index(rating_column)  # Find the column index for the selected ratings column
        
        for row in reader:
            program = row[0]
            rating = float(row[rating_index])  # Read the selected rating column
            program_ratings[program] = rating
    
    return program_ratings

# Path to the CSV file
file_path = 'data/program_ratings.csv'

# File reading section
st.sidebar.header("Input Settings")
file_uploaded = st.sidebar.file_uploader("Upload CSV File", type=['csv'])
if file_uploaded:
    # Display available columns to select
    temp_reader = csv.reader(file_uploaded)
    temp_header = next(temp_reader)  # Extract the header row
    selected_column = st.sidebar.selectbox("Select the Rating Column", options=temp_header[1:])
    
    if selected_column:
        program_ratings_dict = read_csv_to_dict(file_uploaded, selected_column)
else:
    st.warning("Please upload a CSV file to proceed.")

# Genetic Algorithm Parameters
CO_R = st.sidebar.slider("Crossover Rate (CO_R)", min_value=0.0, max_value=0.95, value=0.8, step=0.01)
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R)", min_value=0.01, max_value=0.05, value=0.02, step=0.01)

ratings = program_ratings_dict if file_uploaded else {}

# Fitness function
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program]
    return total_rating

# Initialize population
def initialize_pop(programs, time_slots):
    if not programs:
        return [[]]

    all_schedules = []
    for i in range(len(programs)):
        for schedule in initialize_pop(programs[:i] + programs[i + 1:], time_slots):
            all_schedules.append([programs[i]] + schedule)

    return all_schedules

# Selection
def finding_best_schedule(all_schedules):
    best_schedule = []
    max_ratings = 0

    for schedule in all_schedules:
        total_ratings = fitness_function(schedule)
        if total_ratings > max_ratings:
            max_ratings = total_ratings
            best_schedule = schedule

    return best_schedule

# Crossover
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

# Mutation
def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(list(ratings.keys()))
    schedule[mutation_point] = new_program
    return schedule

# Genetic algorithm
def genetic_algorithm(initial_schedule, crossover_rate=CO_R, mutation_rate=MUT_R):
    population = [initial_schedule]
    for _ in range(49):  # Assume fixed population size of 50
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for _ in range(99):  # Assume fixed 100 generations
        new_population = []
        population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
        new_population.extend(population[:2])  # Assume elitism size of 2

        while len(new_population) < 50:  # Keep the population size at 50
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = new_population

    return population[0]

# Run the Genetic Algorithm if a file is uploaded
if file_uploaded:
    st.subheader("Results")
    all_programs = list(ratings.keys())
    all_time_slots = list(range(6, 24))  # Time slots

    initial_best_schedule = finding_best_schedule(initialize_pop(all_programs, all_time_slots))
    rem_t_slots = len(all_time_slots) - len(initial_best_schedule)
    genetic_schedule = genetic_algorithm(initial_best_schedule)
    final_schedule = initial_best_schedule + genetic_schedule[:rem_t_slots]

    # Display Results in Table Format
    schedule_data = {"Time Slot": [f"{hour}:00" for hour in all_time_slots],
                     "Program": final_schedule}
    df = pd.DataFrame(schedule_data)
    st.table(df)

    st.write("Total Ratings:", fitness_function(final_schedule))
else:
    st.info("Upload a file and select the rating column to generate a schedule.")
