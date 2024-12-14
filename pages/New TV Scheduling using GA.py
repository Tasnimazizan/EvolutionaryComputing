import csv
import random
import streamlit as st

st.header("TV Scheduling using Genetic Algorithm")

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path):
    program_ratings = {}
    
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header
        
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]  # Convert ratings to floats
            program_ratings[program] = ratings
    
    return program_ratings

# Path to the CSV file
file_path = 'data/program_ratings.csv'
program_ratings_dict = read_csv_to_dict(file_path)

# Extract all programs and time slots
all_programs = list(program_ratings_dict.keys())
all_time_slots = list(range(6, 24))  # Time slots: 6 AM to 11 PM
ratings = program_ratings_dict

# Genetic Algorithm Functions
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

def genetic_algorithm(initial_schedule, generations, population_size, crossover_rate, mutation_rate, elitism_size):
    population = [initial_schedule]
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)
    
    for _ in range(generations):
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

# Streamlit Interface for Parameter Input
st.sidebar.header("Genetic Algorithm Parameters")
CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.2, 0.01)
GEN = st.sidebar.number_input("Generations", 10, 500, 100, 10)
POP = st.sidebar.number_input("Population Size", 10, 100, 50, 5)
EL_S = st.sidebar.number_input("Elitism Size", 1, 10, 2, 1)

# Running Multiple Trials
st.sidebar.header("Experiment Settings")
trial_params = []
for i in range(1, 4):
    st.sidebar.subheader(f"Trial {i}")
    co_r = st.sidebar.slider(f"Crossover Rate (Trial {i})", 0.0, 0.95, 0.8, 0.01)
    mut_r = st.sidebar.slider(f"Mutation Rate (Trial {i})", 0.01, 0.05, 0.2, 0.01)
    trial_params.append((co_r, mut_r))

# Initial Schedule and Results
st.subheader("Results")
for i, (co_r, mut_r) in enumerate(trial_params):
    st.write(f"### Trial {i+1}:")
    initial_schedule = random.sample(all_programs, len(all_programs))
    genetic_schedule = genetic_algorithm(initial_schedule, GEN, POP, co_r, mut_r, EL_S)
    final_schedule = genetic_schedule[:len(all_time_slots)]
    
    # Display schedule as table
    schedule_table = [{"Time Slot": f"{all_time_slots[i]}:00", "Program": program} for i, program in enumerate(final_schedule)]
    st.table(schedule_table)
    
    # Display fitness
    st.write(f"**Crossover Rate:** {co_r}, **Mutation Rate:** {mut_r}")
    st.write(f"**Total Ratings:** {fitness_function(final_schedule)}")
