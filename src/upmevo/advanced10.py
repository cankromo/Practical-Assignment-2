import random

# Define the RCPSP parameters
tasks_count = 10
resources_count = 6
task_duration = [3, 2, 5, 4, 2, 3, 4, 2, 4, 6]
task_resource = [5, 1, 1, 1, 3, 3, 2, 4, 5, 2]
task_dependencies = [(1, 4), (1, 5), (2, 9), (2, 10), (3, 8), (4, 6),
                     (4, 7), (5, 9), (5, 10), (6, 8), (6, 9), (7, 8)]
num_generations = 100
population_size = 20
mutation_rate = 0.1
crossover_rate = 0.8
elitism_size = 2

# Initialize random seed for reproducibility
random_seed = random.randint(1, 10)
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
        individual = list(range(1, num_tasks + 1))  # Tasks are 1-indexed
        random.shuffle(individual)
        population.append(individual)
    return population

def is_valid_schedule(schedule, precedence_constraints):
    task_position = {task: pos for pos, task in enumerate(schedule)}
    for pre, suc in precedence_constraints:
        if pre not in task_position or suc not in task_position:
            # This means the task `pre` or `suc` is not in the schedule, which should not happen
            return False
        if task_position[pre] >= task_position[suc]:
            # The predecessor task must occur before the successor task
            return False
    return True


def calculate_bound(node, tasks, resource_constraints):
    # Initialize resources and start times
    remaining_resources = [resources_count] * len(resource_constraints)
    start_times = [0] * tasks_count
    for task_index in node.task_order:
        task_id = task_index - 1  # Convert to 0-indexed
        duration = tasks[task_id][0]
        required_resources = tasks[task_id][1]
        # Find the earliest start time for the task
        earliest_start = start_times[task_id]
        for i, res_required in enumerate(required_resources):
            if remaining_resources[i] < res_required:
                # If not enough resources, this is not a valid node
                return float('inf')
        # Allocate resources and calculate start times
        for i, res_required in enumerate(required_resources):
            remaining_resources[i] -= res_required
        # Calculate the finish time
        finish_time = earliest_start + duration
        # Update the start times of dependent tasks
        for i in range(task_id + 1, tasks_count):
            if (task_index, i + 1) in node.task_order:
                start_times[i] = max(start_times[i], finish_time)
        # Release resources after task completion
        for i, res_required in enumerate(required_resources):
            remaining_resources[i] += res_required
    # The makespan is the maximum finish time
    makespan = max(start_times)
    return makespan

def calculate_fitness(individual, tasks, resource_constraints, precedence_constraints):
    if not is_valid_schedule(individual, precedence_constraints):
        return 0
    node = Node(individual, [0] * resources_count, 0, 0)
    makespan = calculate_bound(node, tasks, resource_constraints)
    return 1 / makespan if makespan < float('inf') else 0

def select_parents(population, fitnesses):
    total_fitness = sum(fitnesses)
    if total_fitness == 0:
        return random.sample(population, 2)  # Fallback if all fitnesses are zero
    selection_probs = [fitness / total_fitness for fitness in fitnesses]
    return random.choices(population, weights=selection_probs, k=2)

def crossover(parent1, parent2, rate, precedence_constraints):
    if random.random() < rate:
        point = random.randint(1, len(parent1) - 2)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        if is_valid_schedule(child1, precedence_constraints) and is_valid_schedule(child2, precedence_constraints):
            return child1, child2
    return parent1, parent2

def mutate(individual, rate, precedence_constraints):
    for i in range(len(individual)):
        if random.random() < rate:
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]
            if not is_valid_schedule(individual, precedence_constraints):
                individual[i], individual[j] = individual[j], individual[i]
    return individual

def genetic_algorithm():
    tasks_formatted = [(task_duration[i], [task_resource[i]] * resources_count) for i in range(tasks_count)]
    resource_constraints = [max(task_resource)] * resources_count
    precedence_constraints = [(a-1, b-1) for a, b in task_dependencies]

    population = initialize_population(population_size, tasks_count)
    best_individual = None
    best_fitness = 0

    for generation in range(num_generations):
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

        print(f"Generation {generation}: Best Fitness {best_fitness}")

    return best_individual, 1 / best_fitness if best_fitness > 0 else float('inf')

# Run the genetic algorithm
best_schedule, makespan = genetic_algorithm()
print("Best schedule:", best_schedule)
print("Makespan:", makespan)
print("Random Seed Used:", random_seed)
