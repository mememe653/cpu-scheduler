#!/usr/bin/env python3

import subprocess as sp


def run_baseline(id):
    sp.run(['./baseline', 'data_' + str(id) + '.txt', 'out_' + str(id) + '_baseline.txt'])


def run_scheduler(id):
    sp.run(['./scheduler', 'data_' + str(id) + '.txt', 'out_' + str(id) + '.txt'])


def compute_baseline_stats(id):
    with open('baseline_stats_' + str(id) + '.txt', 'w') as outfile:
        sp.run(['./compute_stats', 'data_' + str(id) + '.txt', 'out_' + str(id) + '_baseline.txt'], stdout=outfile)


def compute_scheduler_stats(id):
    with open('scheduler_stats_' + str(id) + '.txt', 'w') as outfile:
        sp.run(['./compute_stats', 'data_' + str(id) + '.txt', 'out_' + str(id) + '.txt'], stdout=outfile)


def read_stats(id):
    filenames = ['baseline_stats_' + str(id) + '.txt',
                 'scheduler_stats_' + str(id) + '.txt']
    stats = []
    for idx, filename in enumerate(filenames):
        with open(filename, 'r') as infile:
            infile.readline()
            stats.append(infile.readline().split())
    return (stats[0], stats[1])


def print_stats(id):
    with open('baseline_stats_' + str(id) + '.txt', 'r') as infile:
        print('Baseline Stats')
        print(infile.read())
    with open('scheduler_stats_' + str(id) + '.txt', 'r') as infile:
        print('Scheduler Stats')
        print(infile.read())


def print_grades(baseline_stats, scheduler_stats):
    condition = ' - Your scheduling has a smaller total wait time as compared to the baseline'
    print('Passed' + condition if int(scheduler_stats[2]) < int(baseline_stats[2])
          else 'Failed' + condition)
    condition = ' - Your scheduling has a smaller longest response time as compared to the baseline'
    print('Passed' + condition if int(scheduler_stats[3]) < int(baseline_stats[3])
          else 'Failed' + condition)
    condition = ' - Your scheduling contains fewer switches between customers as compared to the baseline'
    print('Passed' + condition if int(scheduler_stats[4]) < int(baseline_stats[4])
          else 'Failed' + condition)
    condition = ' - Your scheduling has a smaller total wait time for high priority customers as compared to the total wait time for regular customers'
    print('Passed' + condition if int(scheduler_stats[0]) < int(scheduler_stats[1])
          else 'Failed' + condition)


def run(ids):
    for id in ids:
        run_baseline(id)
        run_scheduler(id)
        compute_baseline_stats(id)
        compute_scheduler_stats(id)
        baseline_stats, scheduler_stats = read_stats(id)
        print_stats(id)
        print_grades(baseline_stats, scheduler_stats)
        print()


if __name__ == '__main__':
    ids = [1111, 2222, 3333]
    run(ids)
