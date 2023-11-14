import heapq

class Node:
    def __init__(self, task_order, resource_usage, cost, estimate):
        self.task_order = task_order
        self.resource_usage = resource_usage
        self.cost = cost  # Actual cost to reach the current node
        self.estimate = estimate  # Estimated cost to reach the goal from the current node
        self.total_cost = cost + estimate  # Total estimated cost

    def __lt__(self, other):
        return self.total_cost < other.total_cost

def heuristic(task_order, tasks, resource_constraints):
    remaining_tasks = set(range(len(tasks))) - set(task_order)
    remaining_resource_demands = [max(tasks[task][1]) for task in remaining_tasks]
    return max(remaining_resource_demands, default=0)

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

def update_resource_usage(resource_usage, task, tasks):
    task_duration, task_resource_req = tasks[task]
    for resource in range(len(resource_usage)):
        resource_usage[resource] += task_resource_req[resource]
    return resource_usage

def is_precedence_satisfied(task_order, precedence_constraints):
    scheduled_tasks_set = set(task_order)
    for pre, suc in precedence_constraints:
        if suc in scheduled_tasks_set and pre not in scheduled_tasks_set:
            return False
    return True

def rcpsp_a_star(tasks, resource_constraints, precedence_constraints):
    num_tasks = len(tasks)
    num_resources = len(resource_constraints)
    best_schedule = None
    open_set = []

    initial_estimate = heuristic([], tasks, resource_constraints)
    initial_node = Node([], [0] * num_resources, 0, initial_estimate)
    heapq.heappush(open_set, initial_node)

    while open_set:
        current_node = heapq.heappop(open_set)

        if len(current_node.task_order) == num_tasks:
            best_schedule = current_node
            break  # Found a solution

        for task in range(num_tasks):
            if task not in current_node.task_order and is_precedence_satisfied(current_node.task_order + [task], precedence_constraints):
                new_task_order = current_node.task_order + [task]
                new_resource_usage = update_resource_usage(list(current_node.resource_usage), task, tasks)
                new_cost = calculate_bound(Node(new_task_order, new_resource_usage, 0, 0), tasks, resource_constraints)
                new_estimate = heuristic(new_task_order, tasks, resource_constraints)
                new_node = Node(new_task_order, new_resource_usage, new_cost, new_estimate)
                heapq.heappush(open_set, new_node)

    return best_schedule

# Adjusting the given parameters for the algorithm
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

tasks = [(task_duration[i], [task_resource[i]] * resources) for i in range(len(task_duration))]
resource_constraints = [max(task_resource)] * resources  # Assuming a default resource capacity
precedence_constraints = [(a-1, b-1) for a, b in task_dependencies]

# Running the A* algorithm with the adjusted parameters
best_schedule = rcpsp_a_star(tasks, resource_constraints, precedence_constraints)
if best_schedule:
    print("Best schedule:", best_schedule.task_order)
    print("Makespan:", best_schedule.cost)
else:
    print("No schedule was found.")