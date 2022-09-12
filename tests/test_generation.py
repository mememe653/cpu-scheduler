"""Contains the test harness and random test generator for performance
benchmarking between scheduler.cpp and baseline.cpp."""

import random
from typing import Union
import subprocess as sp
import pathlib
import pandas as pd
import argparse


def create_random_test(seed: int,
                       output_path: Union[str, pathlib.Path],
                       num_customers=50):
    """Creates a randomised input file for Assignment 2.

    Args:
        seed: the seed for the RNG.
        output_file: the output directory as a string or pathlib.Path object.

    Returns:
        None. Creates a randomly generated input file under the output_path.
    """
    random.seed(seed)
    arrival_times = sorted([random.randint(0, 200) for i in range(num_customers)])
    priorities = [random.randint(0, 1) for i in range(num_customers)]

    burst_times = []
    for i in range(num_customers):
        # 80% chance to choose lower values, 20% chance to choose higher values
        if random.random() < 0.8:
            burst_times.append(random.randint(2, 30))
        else:
            burst_times.append(random.randint(50, 100))

    with open(output_path, 'w') as f:
        for i in range(num_customers):
            customer_id = 'c' + str(i).zfill(2)
            f.write(f"{customer_id} {priorities[i]} {arrival_times[i]} {burst_times[i]}\n")


def perform_random_tests(output_path: str = "/tmp",
                         num_random_tests: int = 10000,
                         num_customers: int = 50,
                         scheduler_path: str = "scheduler",
                         baseline_path: str = "baseline",
                         compute_stats_path: str = "compute_stats",
                         log: bool = True) -> dict:
    """Perform a number of random tests, returning the testing results in
    a dictionary.

    Perform a number of random tests using the compiled `baseline`,
    `scheduler` and `compile_stats` programs. These programs should be present
    in the current directory for this function to work. The first
    num_random_tests integers are used as the seeds to the random test
    generator.

    Args:
        output_path: the directory used for temporarily storing the generated
            test case, baseline results and scheduler results.
        num_random_tests: the number of random tests to generate.
        num_customers: the number of customers present in each test case.
        scheduler_path: relative path to the `scheduler` executable
        baseline_path: relative path to the `baseline` executable
        log: if True, then logs failure output to console.

    Returns:
        a dictionary with the following key-value pairs:
        - "num_customers": the value of the num_customers parameter
        - "num_random_tests": the value of the num_random_tests parameter
        - "num_successes": the number of test cases that were successful
        - "num_failures": the number of test cases that failed
        - "num_0_wait_time_fails": the number of test cases that failed due to
                                   not smaller high priority wait time
        - "num_wait_time_fails": the number of test cases that failed due to
                                 not smaller wait time
        - "num_response_time_fails": the number of test cases that failed due
                                     to not smaller response time
        - "num_switch_fails": the number of test cases that filed due to not
                              smaller number of switches
    """
    num_failures = 0
    num_0_wait_time_fails = 0
    num_wait_time_fails = 0
    num_response_time_fails = 0
    num_switch_fails = 0

    for current_seed in range(num_random_tests):
        already_failed = False

        create_random_test(current_seed,
                           f"{output_path}/data.txt",
                           num_customers=num_customers)

        # Run baseline and scheduler.
        sp.run(f"./{baseline_path} {output_path}/data.txt {output_path}/out_baseline.txt".split(' '))
        sp.run(f"./{scheduler_path} {output_path}/data.txt {output_path}/out_scheduler.txt".split(' '))

        # Get baseline and scheduler statistics
        baseline_res = sp.run(f"./{compute_stats_path} {output_path}/data.txt {output_path}/out_baseline.txt".split(' '),
                              capture_output=True)
        scheduler_res = sp.run(f"./{compute_stats_path} {output_path}/data.txt {output_path}/out_scheduler.txt".split(' '),
                               capture_output=True)

        # Extract statistics output.
        baseline_res = baseline_res.stdout.decode()
        scheduler_res = scheduler_res.stdout.decode()

        # Select the numerical output.
        baseline_res = baseline_res.split('\n')[1].split(' ')
        scheduler_res = scheduler_res.split('\n')[1].split(' ')

        # Convert all string entries to integers
        baseline_res = [int(i) for i in baseline_res]
        scheduler_res = [int(i) for i in scheduler_res]

        if scheduler_res[0] >= baseline_res[0]:
            if log:
                print(baseline_res)
                print(scheduler_res)
                print(f"Total high priority wait time of scheduler is equal or greater to baseline (generated test seed {current_seed}).")
            if not already_failed:
                num_failures += 1
                already_failed = True
            num_0_wait_time_fails += 1
        if scheduler_res[2] >= baseline_res[2]:
            if log:
                print(baseline_res)
                print(scheduler_res)
                print(f"Total wait time of scheduler is equal or greater to baseline (generated test seed {current_seed}).")
            if not already_failed:
                num_failures += 1
                already_failed = True
            num_wait_time_fails += 1
        if scheduler_res[3] >= baseline_res[3]:
            if log:
                print(baseline_res)
                print(scheduler_res)
                print(f"Longest response of scheduler is equal or greater to baseline (generated test seed {current_seed}).")
            if not already_failed:
                num_failures += 1
                already_failed = True
            num_response_time_fails += 1
        if scheduler_res[4] >= baseline_res[4]:
            if log:
                print(baseline_res)
                print(scheduler_res)
                print(f"Number of switches of scheduler is equal or greater to baseline (generated test seed {current_seed}).")
            if not already_failed:
                num_failures += 1
                already_failed = True
            num_switch_fails += 1

    return {
        "num_customers": num_customers,
        "num_random_tests": num_random_tests,
        "num_failures": num_failures,
        "num_successes": num_random_tests - num_failures,
        "num_0_wait_time_fails": num_0_wait_time_fails,
        "num_wait_time_fails": num_wait_time_fails,
        "num_response_time_fails": num_response_time_fails,
        "num_switch_fails": num_switch_fails,
    }


def run_tests(num_random_tests: int = 100,
              min_num_customers: int = 0,
              max_num_customers: int = 99,
              output_file: Union[str, pathlib.Path] = "results.csv"):
    """Performs `num_random_tests` random tests, for random test cases of various
    sizes (specifically all sizes between `min_num_customers` and
    `max_num_customers`).

    Args:
        num_random_tests: the number of random tests to create.
        min_num_customers: the lower bound for test case size.
        max_num_customers: the upper bound for test case size.
        output_file: the file to output.

    Returns:
        None. This function outputs a CSV file of testing results to the
    `output_file`.
    """
    header = "num_customers,num_random_tests,num_failures,num_successes,num_0_wait_time_fails,num_wait_time_fails,num_response_time_fails,num_switch_fails"

    with open(output_file, 'w') as f:
        f.write(header + '\n')

    with open(output_file, 'a') as f:
        print(f"performing random tests for num_customers = ", end='', flush=True)
        for num_customers in range(min_num_customers, max_num_customers+1):
            print(f"{num_customers}, ", end='', flush=True)
            results = perform_random_tests(num_customers=num_customers, 
                                           num_random_tests=num_random_tests,
                                           log=False)

            # consolidate numerical results into a line, separated by comma
            res_txt = [str(results[k]) for k in results.keys()]
            res_txt = ','.join(res_txt)
            res_txt += '\n'

            f.write(res_txt)
        print()


if __name__ == "__main__":
    run_tests()
