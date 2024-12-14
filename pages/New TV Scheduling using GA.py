import csv
import random
import streamlit as st
import pandas as pd

st.header("TV Scheduling using Genetic Algorithm")

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path):
    program_ratings = {}
    
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        # Skip the header
        header = next(reader)
        
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings
    
    return program_ratings

# Path to the CSV file
file_path = 'data/program_ratings.csv'
    
# Get the data in the required format
program_ratings_dict = read_csv_to_dict(file_path)

# Genetic Algorithm Parameters
CO_R = st.sidebar.slider("Crossover Rate (CO_R)", min_value=0.0, max_value=0.95, value=0.8, step=0.01)
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R)", min_value=0.01, max_value=0.05, value=0.2, step=0.01)
GEN = st.sidebar.number_input("Number of Generations (GEN)", min_value=10, max_value=500, value=100, step=10)
POP = st.sidebar.number_input("Population Size (POP)", min_value=10, max_value=200, value=50, step=10)
EL_S = st.sidebar.number_input("Elitism Size (EL_S)", min_value=1, max_value=10, value=2, step=1)

ratings = program_ratings_dict
all_programs = list(ratings.keys()) # all programs
all_time_slots = list(range(6, 24)) # time slots

# Fitness function
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
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
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

# Genetic algorithm
def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    population = [initial_schedule]
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for generation in range(generations):
        new_population = []
        population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
        new_population.extend(population[:elitism_size])

        while len(new_population) < population_size:
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

# Run the Genetic Algorithm
st.subheader("Results")
initial_best_schedule = finding_best_schedule(initialize_pop(all_programs, all_time_slots))
rem_t_slots = len(all_time_slots) - len(initial_best_schedule)
genetic_schedule = genetic_algorithm(initial_best_schedule, generations=GEN, population_size=POP, elitism_size=EL_S)
final_schedule = initial_best_schedule + genetic_schedule[:rem_t_slots]

# Display Results in Table Format
schedule_data = {"Time Slot": [f"{hour}:00" for hour in all_time_slots],
                 "Program": final_schedule}
df = pd.DataFrame(schedule_data)
st.table(df)

st.write("Total Ratings:", fitness_function(final_schedule))