import random

# Define problem parameters
tasks = 10
resources = 6
task_duration = [3, 2, 5, 4, 2, 3, 4, 2, 4, 6]
task_resource = [5, 1, 1, 1, 3, 3, 2, 4, 5, 2]
task_dependencies = [(1, 4), (1, 5), (2, 9), (2, 10), (3, 8), (4, 6),
                     (4, 7), (5, 9), (5, 10), (6, 8), (6, 9), (7, 8)]
population_size = 50
generations = 100
mutation_rate = 0.2
max_no_improvement = 10  # Termination condition: Stop if no improvement for this many generations

# Generate a random seed from 0 to 10
seed = random.randint(0, 10)
random.seed(seed)

# Initialize a population of schedules
def initialize_population(population_size):
    population = []
    for _ in range(population_size):
        schedule = random.sample(range(1, tasks + 1), tasks)
        population.append(schedule)
    return population

# Calculate makespan for a schedule
def calculate_makespan(schedule):
    task_finish_time = [0] * tasks
    for task in schedule:
        dependencies = [dependency for dependency in task_dependencies if dependency[1] == task]
        if dependencies:
            start_time = max(task_finish_time[dependency[0] - 1] for dependency in dependencies)
        else:
            start_time = 0
        end_time = start_time + task_duration[task - 1]
        
        # Check for resource availability and non-overlapping tasks
        resource = task_resource[task - 1]
        if all(task_finish_time[i] <= start_time or task_resource[i] != resource for i in range(task)):
            task_finish_time[task - 1] = end_time
        else:
            # If there's an overlap, adjust the start time
            start_time = max(task_finish_time[i] for i in range(task))
            end_time = start_time + task_duration[task - 1]
            task_finish_time[task - 1] = end_time
    return max(task_finish_time)

# Selection: Tournament selection
def tournament_selection(population, k=5):
    selected = random.sample(population, k)
    return min(selected, key=calculate_makespan)

# Crossover: Two-point crossover with non-overlapping constraint
def crossover(parent1, parent2):
    point1, point2 = random.sample(range(1, tasks), 2)
    if point1 > point2:
        point1, point2 = point2, point1
    
    # Ensure non-overlapping tasks
    child1 = [task for task in parent1 if task not in parent2[point1:point2]]
    child2 = [task for task in parent2 if task not in parent1[point1:point2]]
    
    return child1[:point1] + parent2[point1:point2] + child1[point1:], child2[:point1] + parent1[point1:point2] + child2[point1:]

# Mutation: Swap mutation with non-overlapping constraint
def mutate(schedule):
    if random.random() < mutation_rate:
        point1, point2 = random.sample(range(tasks), 2)
        
        # Ensure non-overlapping tasks
        while schedule[point1] in schedule[point2:point2 + 2] or schedule[point2] in schedule[point1:point1 + 2]:
            point1, point2 = random.sample(range(tasks), 2)
        
        schedule[point1], schedule[point2] = schedule[point2], schedule[point1]
    return schedule

# Define a function to select the best population
def select_best_population(population, size):
    return sorted(population, key=calculate_makespan)[:size]

# Genetic Algorithm
def advanced_genetic_algorithm():
    global mutation_rate  # Declare mutation_rate as global
    
    population = initialize_population(population_size)
    best_schedule = population[0]
    best_makespan = calculate_makespan(best_schedule)
    no_improvement_count = 0
    elite_size = int(0.1 * population_size)  # Percentage of elite individuals

    for generation in range(generations):
        new_population = []
        
        # Apply genetic operators to create a new population
        for _ in range(population_size - elite_size):
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            new_population.extend([child1, child2])
        
        # Keep the elite individuals from the previous population
        elite = select_best_population(population, elite_size)
        new_population.extend(elite)

        # Select the best solutions for the next generation
        population = select_best_population(new_population, population_size)
        
        # Check for improvement in best makespan
        new_makespan = calculate_makespan(population[0])
        if new_makespan < best_makespan:
            best_schedule = population[0]
            best_makespan = new_makespan
            no_improvement_count = 0
        else:
            no_improvement_count += 1

        # Decrease mutation rate over time
        mutation_rate = max(0.05, mutation_rate * 0.95)

        # Termination condition: Stop if no improvement for a certain number of generations
        if no_improvement_count >= max_no_improvement:
            break

    return best_schedule, best_makespan

best_schedule, makespan = advanced_genetic_algorithm()
print("Best Schedule:", best_schedule)
print("Makespan:", makespan)
print("Random Seed:", seed)
