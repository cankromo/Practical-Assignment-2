import heapq

class Node:
    def __init__(self, task_order, task_start_times, task_end_times, max_resources):
        self.task_order = task_order
        self.task_start_times = task_start_times
        self.task_end_times = task_end_times
        self.max_resources = max_resources

    def __lt__(self, other):
        return self.get_makespan() < other.get_makespan()

    def get_makespan(self):
        return max(self.task_end_times.values()) if self.task_end_times else 0

def can_start(task_id, start_time, task_durations, task_dependencies, task_resources, task_start_times, max_resources):
    # Check if dependencies are met
    for pre, succ in task_dependencies:
        if succ == task_id and pre in task_start_times:
            if task_start_times[pre] + task_durations[pre] > start_time:
                print(f"Task {task_id} cannot start at {start_time} because task {pre} ends at {task_start_times[pre] + task_durations[pre]}")
                return False
    # Check resource availability
    ongoing_tasks = [t for t in task_start_times if task_start_times[t] <= start_time < task_start_times[t] + task_durations[t]]
    if sum(task_resources[t] for t in ongoing_tasks) + task_resources[task_id] > max_resources:
        return False
    return True


def schedule_task(task_id, task_durations, task_resources, task_dependencies, max_resources, current_time, task_start_times):
    while not can_start(task_id, current_time, task_durations, task_dependencies, task_resources, task_start_times, max_resources):
        current_time += 1
    # Schedule the task
    task_start_times[task_id] = current_time
    return current_time + task_durations[task_id]

def rcpsp(tasks, task_durations, task_resources, task_dependencies, max_resources):
    # Initialization
    task_start_times = {}
    task_end_times = {}
    tasks_heap = []
    
    # Start with an empty schedule
    heapq.heappush(tasks_heap, Node([], {}, {}, max_resources))

    while tasks_heap:
        current_node = heapq.heappop(tasks_heap)
        print(f"Exploring schedule with order {current_node.task_order} and makespan {current_node.get_makespan()}")

        if set(current_node.task_order) == set(tasks):
            return current_node

        for task in tasks:
            if task not in current_node.task_order:
                new_task_order = current_node.task_order + [task]
                new_task_start_times = current_node.task_start_times.copy()
                new_task_end_times = current_node.task_end_times.copy()
                end_time = schedule_task(task, task_durations, task_resources, task_dependencies, max_resources, current_node.get_makespan(), new_task_start_times)
                new_task_end_times[task] = end_time
                heapq.heappush(tasks_heap, Node(new_task_order, new_task_start_times, new_task_end_times, max_resources))
                print(f"Task {task} scheduled to start at {new_task_start_times[task]}")  # More detailed tracking

    return None  # If no schedule is found

# Define your tasks and constraints
tasks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
task_durations = {0: 5, 1: 3, 2: 1, 3: 1, 4: 5, 5: 2, 6: 2, 7: 8, 8: 9, 9: 1,
                 10: 4, 11: 2, 12: 4, 13: 1, 14: 1, 15: 3, 16: 7, 17: 6, 18: 1, 19: 8,
                 20: 3, 21: 3, 22: 10, 23: 8, 24: 7, 25: 4, 26: 5, 27: 2, 28: 7, 29: 5}

task_resources = {0: 8, 1: 5, 2: 1, 3: 7, 4: 1, 5: 4, 6: 1, 7: 4, 8: 5, 9: 1,
                 10: 7, 11: 11, 12: 1, 13: 6, 14: 1, 15: 1, 16: 10, 17: 9, 18: 8, 19: 1,
                 20: 1, 21: 1, 22: 1, 23: 8, 24: 8, 25: 1, 26: 1, 27: 9, 28: 1, 29: 3}

task_dependencies = [(1, 4), (2, 5), (2, 16), (2, 25), (3, 9), (3, 13),
                     (3, 18), (4, 11), (4, 15), (4, 17), (5, 6), (5, 7),
                     (5, 14), (6, 8), (6, 10), (6, 19), (7, 21), (8, 22),
                     (9, 20), (10, 12), (11, 16), (11, 30), (12, 28), (13, 26),
                     (14, 18), (14, 28), (15, 25), (15, 26), (16, 26), (16,27),
                     (17, 18), (17, 24), (18, 27), (19, 24), (20, 29), (21, 23),
                     (22, 30), (23, 27), (24, 30), (25, 28), (26, 29), (27, 29)]
max_resources = 28

best_schedule = rcpsp(tasks, task_durations, task_resources, task_dependencies, max_resources)
if best_schedule:
    print(f"Best schedule: {best_schedule.task_order}")
    print(f"Task start times: {best_schedule.task_start_times}")
    print(f"Makespan: {best_schedule.get_makespan()}")
else:
    print("No schedule was found.")
