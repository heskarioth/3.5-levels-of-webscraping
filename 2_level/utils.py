import time
import argparse
import psutil


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Properties for running script')

    # Add an argument for n_runs with a default value of 5
    parser.add_argument('--n_runs', type=int, default=5,
                        help='Number of runs (default: 5)')
                        
    # Add an argument for print_df with a boolean type and default value of False
    parser.add_argument('--print_df', type=bool, default=False,
                        help='Print DataFrame (default: False)')

    args = parser.parse_args()
    return args


def timeit(func):
    """
    A timeit utility function to measure the execution time of a function when used as a decorator.

    Args:
        func (function): The function to measure.

    Returns:
        function: A wrapped function that measures the execution time of the original function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        elapsed_time_seconds = int(elapsed_time)
        elapsed_time_milliseconds = int((elapsed_time - elapsed_time_seconds) * 1000)
        print(f"Execution time: {elapsed_time_seconds} seconds {elapsed_time_milliseconds} milliseconds")
        return result
    return wrapper


# Define the decorator function
def resource_usage_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time() # Get the current time before function execution
        cpu_start = psutil.cpu_percent()
        memory_start = psutil.virtual_memory().percent
        result = func(*args, **kwargs) # Call the original function
        end_time = time.time() # Get the current time after function execution
        duration = end_time - start_time # Calculate the duration in seconds
        cpu_end = psutil.cpu_percent()
        memory_end = psutil.virtual_memory().percent
        cpu_usage = cpu_end - cpu_start
        memory_usage = memory_end - memory_start
        print(f"Function '{func.__name__}' took {duration:.6f} seconds to execute.")
        print(f"CPU usage: {cpu_usage:.2f}%")
        print(f"Memory usage: {memory_usage:.2f}%")
        return result
    return wrapper