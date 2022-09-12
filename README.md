Arriving customers are placed FCFS into an arrival queue.
They are partially executed before being moved to either a high-priority queue or low-priority queue. This ensures low response time.
Customers in the high-priority and low-priority queues are executed according to SRTF. This ensures low total wait time.
Each queue will process all its customers until none remain, without being pre-empted by another queue. This ensures low number of switches.
The low-priority queue will only be selected for processing if there are no customers queued in the other queues. This ensures the wait time for the high-priority customers is less than for low-priority customers.

To automatically grade assignment:
1. g++ baseline.cpp -o baseline
2. g++ scheduler.cpp -o scheduler
3. g++ compute_stats.cpp -o compute_stats
4. ./grade_assignment.py