from ..upmproblems.rcpsp06 import get_tasks, get_resources, get_task_duration, get_task_resource, get_task_dependencies

tasks = get_tasks()
resources = get_resources()
task_duration = get_task_duration()
task_resource = get_task_resource()
task_dependencies = get_task_dependencies()

class ProblemState:
    def __init__(self, tasks, resources, task_durations, task_resources, task_dependencies, current_schedule=None):
        self.tasks = tasks
        self.resources = resources
        self.task_durations = task_durations
        self.task_resources = task_resources
        self.task_dependencies = task_dependencies
        self.current_schedule = current_schedule if current_schedule else {task: None for task in tasks}

    def is_promising(self, best_solution_value):
        for time in range(best_solution_value):
            resource_usage = {resource: 0 for resource in self.resources}
            for task, start_time in self.current_schedule.items():
                if start_time is not None and start_time <= time < start_time + self.task_durations[task]:
                    for resource, amount in self.task_resources[task].items():
                        resource_usage[resource] += amount
                        if resource_usage[resource] > self.resources[resource]:
                            return False
        estimated_completion_time = self.estimate_completion_time()
        return estimated_completion_time < best_solution_value

    def is_solution(self):
        for task, dependencies in self.task_dependencies.items():
            for dependency in dependencies:
                if self.current_schedule[task] is None or self.current_schedule[dependency] is None:
                    return False
                if self.current_schedule[task] < self.current_schedule[dependency] + self.task_durations[dependency]:
                    return False
        return all(start_time is not None for start_time in self.current_schedule.values())

    def value(self):
        if not self.is_solution():
            return float('inf')
        return max(start_time + self.task_durations[task] for task, start_time in self.current_schedule.items())

    def possible_moves(self):
        moves = []
        for task in self.tasks:
            if self.current_schedule[task] is None:
                dependencies_met = all(
                    self.current_schedule[dependency] is not None and
                    self.current_schedule[dependency] + self.task_durations[dependency] <= self.current_schedule[task]
                    for dependency in self.task_dependencies[task]
                )
                if dependencies_met:
                    earliest_start_time = self.find_earliest_start_time(task)
                    moves.append((task, earliest_start_time))
        return moves

    def apply_move(self, move):
        task, start_time = move
        new_schedule = self.current_schedule.copy()
        new_schedule[task] = start_time
        return ProblemState(self.tasks, self.resources, self.task_durations, self.task_resources, self.task_dependencies, new_schedule)

    def estimate_completion_time(self):
        latest_end_time = max(
            (start_time + self.task_durations[task] for task, start_time in self.current_schedule.items() if start_time is not None),
            default=0
        )
        for task in self.tasks:
            if self.current_schedule[task] is None:
                latest_end_time = max(latest_end_time, latest_end_time + self.task_durations[task])
        return latest_end_time

    def find_earliest_start_time(self, task):
        # The earliest start time is at least after all dependencies have been completed.
        dependency_completion_times = [self.current_schedule[d] + self.task_durations[d] for d in self.task_dependencies[task] if self.current_schedule[d] is not None]
        earliest_start_time = max(dependency_completion_times, default=0)

        # Check resource availability from the earliest start time onwards.
        while True:
            resource_feasible = True
            for time in range(earliest_start_time, earliest_start_time + self.task_durations[task]):
                for resource, required_amount in self.task_resources[task].items():
                    if required_amount > 0:  # If the task requires this resource
                        # Calculate the total resource usage including the proposed task
                        resource_usage = sum(
                            self.task_resources[other_task][resource]
                            for other_task, start_time in self.current_schedule.items()
                            if start_time is not None and start_time <= time < start_time + self.task_durations[other_task]
                        ) + required_amount

                        # If the total usage exceeds the resource limit, this start time is not feasible
                        if resource_usage > self.resources[resource]:
                            resource_feasible = False
                            break

                if not resource_feasible:
                    break

            # If resources are available for the entire duration of the task, this start time is feasible
            if resource_feasible:
                return earliest_start_time

            # If not, increment the earliest start time and check again
            earliest_start_time += 1


def branch_and_bound(initial_state):
    best_solution = None
    best_solution_value = float('inf')
    queue = [initial_state]

    while queue:
        state = queue.pop(0)
        if not state.is_promising(best_solution_value):
            continue
        if state.is_solution() and state.value() < best_solution_value:
            best_solution = state
            best_solution_value = state.value()
        for move in state.possible_moves():
            child_state = state.apply_move(move)
            queue.append(child_state)

    return best_solution

def exercise1(tasks, resources, task_durations, task_resources, task_dependencies):
    initial_state = ProblemState(tasks, resources, task_durations, task_resources, task_dependencies)
    best_solution_state = branch_and_bound(initial_state)
    if best_solution_state:
        return [best_solution_state.current_schedule[task] for task in tasks]
    else:
        return []






def exercise2(tasks=0, resources=0, task_duration=[], task_resource=[], task_dependencies=[]):
    """
    Returns the best solution found by the A* algorithm of exercise 2
    :param tasks: number of tasks in the task planning problem with resources
    :param resources: number of resources in the task planning problem with resources
    :param task_duration: list of durations of the tasks
    :param task_resource: list of resources required by each task
    :param task_dependencies: list of dependencies (expressed as binary tuples) between tasks
    :return: list with the start time of each task in the best solution found, or empty list if no solution was found
    """
    return []
