import random

# Define the RCPSP parameters
tasks = 6
task_duration = [3, 4, 2, 2, 1, 4]
task_resource = [2, 3, 4, 4, 3, 2]
task_dependencies = [(1, 3), (2, 3), (2, 4), (3, 5), (4, 6)]
resources = 4
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
        self.cost = cost  # Actual cost to reach the current node
        self.estimate = estimate  # Estimated cost to reach the goal from the current node
        self.total_cost = cost + estimate  # Total estimated cost

    def __lt__(self, other):
        return self.total_cost < other.total_cost

# Genetic Algorithm Functions
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
        earliest_start_time = max(start_time[task], makespan)
        
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
    
    lower_bound = makespan
    return lower_bound

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
    node = Node(individual, [0] * resources, 0, 0)
    makespan = calculate_bound(node, tasks, resource_constraints)
    return 1 / makespan if makespan > 0 else 0

def select_parents(population, fitnesses):
    total_fitness = sum(fitnesses)
    selection_probs = [fitness / total_fitness for fitness in fitnesses]
    return random.choices(population, weights=selection_probs, k=2)

def crossover(parent1, parent2, rate, precedence_constraints):
    if random.random() < rate:
        child1 = parent1.copy()
        child2 = parent2.copy()
        for i in range(len(parent1)):
            if random.random() < 0.5:
                swap_tasks(child1, child2, i, precedence_constraints)
        return child1, child2
    else:
        return parent1, parent2

def swap_tasks(child1, child2, index, precedence_constraints):
    task1 = child1[index]
    task2 = child2[index]
    if can_swap(task1, task2, child1, child2, precedence_constraints):
        child1[index], child2[index] = child2[index], child1[index]

def can_swap(task1, task2, child1, child2, precedence_constraints):
    temp_child1 = child1.copy()
    temp_child1[temp_child1.index(task2)] = task1
    temp_child2 = child2.copy()
    temp_child2[temp_child2.index(task1)] = task2
    return is_valid_schedule(temp_child1, precedence_constraints) and is_valid_schedule(temp_child2, precedence_constraints)

def mutate(individual, rate, precedence_constraints):
    for i in range(len(individual)):
        if random.random() < rate:
            j = random.randint(0, len(individual) - 1)
            if can_swap(individual[i], individual[j], individual, individual, precedence_constraints):
                individual[i], individual[j] = individual[j], individual[i]
    return individual

def genetic_algorithm():
    population = initialize_population(population_size, len(task_duration))
    best_individual = None
    best_fitness = 0

    for _ in range(num_generations):
        fitnesses = [calculate_fitness(individual, tasks, resource_constraints, precedence_constraints) for individual in population]
        
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

# Adjusting the given parameters for the algorithm
tasks = [(task_duration[i], [task_resource[i]] * resources) for i in range(len(task_duration))]
resource_constraints = [max(task_resource)] * resources
precedence_constraints = [(a-1, b-1) for a, b in task_dependencies]

# Running the Genetic Algorithm
best_schedule, makespan = genetic_algorithm()
print("Best schedule:", best_schedule)
print("Makespan:", makespan)
print("Random Seed Used:", random_seed)
