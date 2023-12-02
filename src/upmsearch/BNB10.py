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
tasks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
task_durations = {0: 3, 1: 2, 2: 5, 3: 4, 4: 2, 5: 3, 6: 4, 7: 2, 8: 4, 9: 6}
task_resources = {0: 5, 1: 1, 2: 1, 3: 1, 4: 3, 5: 3, 6: 2, 7: 4, 8: 5, 9: 2}
task_dependencies = [(1, 4), (1, 5), (2, 9), (2, 10), (3, 8), (4, 6),
                     (4, 7), (5, 9), (5, 10), (6, 8), (6, 9), (7, 8)]
max_resources = 6

best_schedule = rcpsp(tasks, task_durations, task_resources, task_dependencies, max_resources)
if best_schedule:
    print(f"Best schedule: {best_schedule.task_order}")
    print(f"Task start times: {best_schedule.task_start_times}")
    print(f"Makespan: {best_schedule.get_makespan()}")
else:
    print("No schedule was found.")
