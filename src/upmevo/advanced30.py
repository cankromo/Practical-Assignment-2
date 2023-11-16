import random

# Define the RCPSP parameters
tasks = 30
resources = 28
task_duration = [5, 3, 1, 1, 5, 2, 2, 8, 9, 1,
                 4, 2, 4, 1, 1, 3, 7, 6, 1, 8,
                 3, 3, 10, 8, 7, 4, 5, 2, 7, 5]
task_resource = [8, 5, 1, 7, 1, 4, 1, 4, 5, 1,
                 7, 11, 1, 6, 1, 1, 10, 9, 8, 1,
                 1, 1, 1, 8, 8, 1, 1, 9, 1, 3]
task_dependencies = [(1, 4), (2, 5), (2, 16), (2, 25), (3, 9), (3, 13),
                     (3, 18), (4, 11), (4, 15), (4, 17), (5, 6), (5, 7),
                     (5, 14), (6, 8), (6, 10), (6, 19), (7, 21), (8, 22),
                     (9, 20), (10, 12), (11, 16), (11, 30), (12, 28), (13, 26),
                     (14, 18), (14, 28), (15, 25), (15, 26), (16, 26), (16,27),
                     (17, 18), (17, 24), (18, 27), (19, 24), (20, 29), (21, 23),
                     (22, 30), (23, 27), (24, 30), (25, 28), (26, 29), (27, 29)]
num_generations = 100
population_size = 20
mutation_rate = 0.1
crossover_rate = 0.8
elitism_size = 2  # Number of top individuals to carry over

# Initialize random seed
random_seed = random.randint(1, 5)
random.seed(random_seed)

class Node:
    def __init__(self, task_order, resource_usage, cost, estimate):
        self.task_order = task_order
        self.resource_usage = resource_usage
        self.cost = cost
        self.estimate = estimate
        self.total_cost = cost + estimate

    def __lt__(self, other):
        return self.total_cost < other.total_cost

def initialize_population(size, num_tasks):
    population = []
    for _ in range(size):
        individual = list(range(num_tasks))
        random.shuffle(individual)
        population.append(individual)
    return population

def calculate_bound(node, tasks, resource_constraints):
    remaining_resources = list(resource_constraints)
    makespan = 0
    start_time = [0] * len(tasks)

    for task in node.task_order:
        task_duration, task_resource_req = tasks[task]
        earliest_start_time = start_time[task]

        resource_available = True
        for resource in range(len(resource_constraints)):
            if remaining_resources[resource] < task_resource_req[resource]:
                resource_available = False
                break

        if resource_available:
            makespan = earliest_start_time + task_duration
            for resource in range(len(resource_constraints)):
                remaining_resources[resource] -= task_resource_req[resource]
        start_time[task] = earliest_start_time

    return makespan

def is_valid_schedule(schedule, precedence_constraints):
    task_position = {task: pos for pos, task in enumerate(schedule)}
    for pre, suc in precedence_constraints:
        if pre not in task_position or suc not in task_position:
            # Handle the missing task case here, e.g., by logging an error or taking corrective action
            return False
        if task_position[pre] >= task_position[suc]:
            return False
    return True


def calculate_fitness(individual, tasks, resource_constraints, precedence_constraints):
    if not is_valid_schedule(individual, precedence_constraints):
        return 0
    node = Node(individual, [0] * resources_count, 0, 0)
    makespan = calculate_bound(node, tasks, resource_constraints)
    return 1 / makespan if makespan > 0 else 0

def select_parents(population, fitnesses):
    total_fitness = sum(fitnesses)
    if total_fitness == 0:
        return random.sample(population, 2) # Fallback if all fitnesses are zero
    selection_probs = [fitness / total_fitness for fitness in fitnesses]
    return random.choices(population, weights=selection_probs, k=2)

def crossover(parent1, parent2, rate, precedence_constraints):
    if random.random() < rate:
        # Select a crossover point
        point = random.randint(1, len(parent1) - 2)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]

        # Ensure valid schedule
        if not is_valid_schedule(child1, precedence_constraints):
            child1 = parent1
        if not is_valid_schedule(child2, precedence_constraints):
            child2 = parent2

        return child1, child2
    else:
        return parent1, parent2

def mutate(individual, rate, precedence_constraints):
    for i in range(len(individual)):
        if random.random() < rate:
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]
            if not is_valid_schedule(individual, precedence_constraints):
                # Revert if invalid
                individual[i], individual[j] = individual[j], individual[i]
    return individual

def genetic_algorithm():
    tasks_formatted = [(task_duration[i], [task_resource[i]] * resources_count) for i in range(tasks_count)]
    resource_constraints = [max(task_resource)] * resources_count
    precedence_constraints = [(a-1, b-1) for a, b in task_dependencies]

    population = initialize_population(population_size, len(task_duration))
    best_individual = None
    best_fitness = 0

    for _ in range(num_generations):
        fitnesses = [calculate_fitness(individual, tasks_formatted, resource_constraints, precedence_constraints) for individual in population]

        elites = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)[:elitism_size]
        elite_individuals = [elite[0] for elite in elites]

        new_population = elite_individuals.copy()
        while len(new_population) < population_size:
            parent1, parent2 = select_parents(population, fitnesses)
            child1, child2 = crossover(parent1, parent2, crossover_rate, precedence_constraints)
            child1 = mutate(child1, mutation_rate, precedence_constraints)
            child2 = mutate(child2, mutation_rate, precedence_constraints)

            new_population.extend([child1, child2])

        population = new_population[:population_size]

        for individual, fitness in zip(population, fitnesses):
            if fitness > best_fitness:
                best_individual = individual
                best_fitness = fitness

    return best_individual, 1 / best_fitness if best_fitness > 0 else float('inf')

# Running the Genetic Algorithm
best_schedule, makespan = genetic_algorithm()
print("Best schedule:", best_schedule)
print("Makespan:", makespan)
print("Random Seed Used:", random_seed)
