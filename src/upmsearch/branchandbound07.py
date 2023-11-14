import heapq

class Node:
    def __init__(self, task_order, resource_usage, bound):
        self.task_order = task_order
        self.resource_usage = resource_usage
        self.bound = bound

    def __lt__(self, other):
        return self.bound < other.bound

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

def rcpsp_branch_and_bound(tasks, resource_constraints, precedence_constraints):
    num_tasks = len(tasks)
    num_resources = len(resource_constraints)
    best_schedule = None
    priority_queue = []

    initial_node = Node([], [0] * num_resources, calculate_bound(Node([], [0] * num_resources, 0), tasks, resource_constraints))
    heapq.heappush(priority_queue, initial_node)

    while priority_queue:
        node = heapq.heappop(priority_queue)

        if len(node.task_order) == num_tasks:
            if best_schedule is None or node.bound < best_schedule.bound:
                best_schedule = node
                continue

        if best_schedule and node.bound >= best_schedule.bound:
            continue

        for task in range(num_tasks):
            if task not in node.task_order and is_precedence_satisfied(node.task_order + [task], precedence_constraints):
                new_task_order = node.task_order + [task]
                new_resource_usage = update_resource_usage(list(node.resource_usage), task, tasks)
                new_bound = calculate_bound(Node(new_task_order, new_resource_usage, 0), tasks, resource_constraints)
                new_node = Node(new_task_order, new_resource_usage, new_bound)
                heapq.heappush(priority_queue, new_node)

    return best_schedule

# Example usage
tasks = 7
resources = 5
task_duration = [2, 1, 1, 1, 3, 2, 1]
task_resource = [4, 1, 2, 2, 2, 1, 2]
task_dependencies = [(1, 3), (1, 5), (3, 6), (4, 6), (5, 7), (6, 7)]

tasks_list = [(duration, [req] * resources) for duration, req in zip(task_duration, task_resource)]
resource_constraints = [max(task_resource)] * resources
precedence_constraints = [(a-1, b-1) for a, b in task_dependencies]

best_schedule = rcpsp_branch_and_bound(tasks_list, resource_constraints, precedence_constraints)
if best_schedule:
    print("Best schedule:", best_schedule.task_order)
    print("Makespan:", best_schedule.bound)
else:
    print("No schedule was found.")
