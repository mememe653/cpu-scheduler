// Program Imports
#include <iostream>
#include <fstream>
#include <deque>
#include <vector>
#include <algorithm>

// Program Constants
// std is a namespace: https://www.cplusplus.com/doc/oldtutorial/namespaces/
const int TIME_ALLOWANCE = 8;  // allow to use up to this number of time slots at once
const int PRINT_LOG = 0; // print detailed execution trace
const int HIGH_PRIORITY = 0;
const int LOW_PRIORITY = 1;

// Customer Class
class Customer {
    // Object Variables
    public:
        std::string name;
        int priority;
        int arrival_time;
        int slots_remaining; // how many time slots are still needed
        int playing_since;
    // Customer Constructor
    Customer(std::string par_name, int par_priority, int par_arrival_time, int par_slots_remaining) {
        name = par_name;
        priority = par_priority;
        arrival_time = par_arrival_time;
        slots_remaining = par_slots_remaining;
        playing_since = -1;
    }
};

// Event Class
class Event {
    // Object Variables
    public:
        int event_time;
        int customer_id;  // each event involes exactly one customer
    // Event Constructor
    Event(int par_event_time, int par_customer_id) {
        event_time = par_event_time;
        customer_id = par_customer_id;
    }
};

// Initialize System Method
void initialize_system(std::ifstream& in_file, std::deque<Event>& arrival_events, std::vector<Customer>& customers) {
    // Method Variables
    std::string name;
    int priority, arrival_time, slots_requested;
    // read input file line by line
    // https://stackoverflow.com/questions/7868936/read-file-line-by-line-using-ifstream-in-c
    int customer_id = 0;
    while (in_file >> name >> priority >> arrival_time >> slots_requested) {
        Customer customer_from_file(name, priority, arrival_time, slots_requested);
        customers.push_back(customer_from_file);
        // new customer arrival event
        Event arrival_event(arrival_time, customer_id);
        arrival_events.push_back(arrival_event);
        customer_id++;
    }
}

// Print State (Prints the state of the program) (Outputs to the console)
void print_state(std::ofstream& out_file, int current_time, int current_id, const std::deque<Event>& arrival_events, const std::deque<int>& customer_queue) {
    out_file << current_time << " " << current_id << '\n';
    if (PRINT_LOG == 0)
    {
        return;
    }
    std::cout << current_time << ", " << current_id << '\n';
    for (int i = 0; i < arrival_events.size(); i++)
    {
        std::cout << "\t" << arrival_events[i].event_time << ", " << arrival_events[i].customer_id << ", ";
    }
    std::cout << '\n';
    for (int i = 0; i < customer_queue.size(); i++)
    {
        std::cout << "\t" << customer_queue[i] << ", ";
    }
    std::cout << '\n';
}

// process command line arguments
// https://www.geeksforgeeks.org/command-line-arguments-in-c-cpp/
int main(int argc, char* argv[]) {
    if (argc != 3)
    {
        std::cerr << "Provide input and output file names." << std::endl;
        return -1;
    }
    std::ifstream in_file(argv[1]);
    std::ofstream out_file(argv[2]);
    if ((!in_file) || (!out_file))
    {
        std::cerr << "Cannot open one of the files." << std::endl;
        return -1;
    }
    // Method Variables
    // deque: https://www.geeksforgeeks.org/deque-cpp-stl/
    // vector: https://www.geeksforgeeks.org/vector-in-cpp-stl/
    std::deque<Event> arrival_events; // new customer arrivals
    std::vector<Customer> customers; // information about each customer
    // read information from file, initialize events queue
    initialize_system(in_file, arrival_events, customers);
    std::deque<int> arrival_queue;
    std::deque<int> high_priority_queue;
    std::deque<int> low_priority_queue;
    std::deque<int>* current_queue = &arrival_queue;
    int current_id = -1;
    int time_out = -1;
    bool all_done = false;
    // Loops through until all_done is true
    for (int current_time = 0; !all_done; current_time++) {
        while (!arrival_events.empty() && (current_time == arrival_events[0].event_time)) {
            arrival_queue.push_back(arrival_events[0].customer_id);
            arrival_events.pop_front();
        }
        if (current_id >= 0) {
            if (current_time == time_out) {
                int last_run = current_time - customers[current_id].playing_since;
                customers[current_id].slots_remaining -= last_run;
                //current_queue->pop_front();
                if (customers[current_id].slots_remaining > 0) {
                    if (customers[current_id].priority == HIGH_PRIORITY) {
                        high_priority_queue.push_back(current_id);
                    }
                    else if (customers[current_id].priority == LOW_PRIORITY) {
                        low_priority_queue.push_back(current_id);
                    }
                }
                current_id = -1;
            }
        }
        if (current_id == -1) {
            // If the current_queue is empty
            if (current_queue->empty()) {
                if (current_queue == &arrival_queue) {
                    current_queue = &high_priority_queue;
                }
                else if (current_queue == &high_priority_queue) {
                    current_queue = &arrival_queue;
                }
                else if (current_queue == &low_priority_queue) {
                    current_queue = &arrival_queue;
                    if (current_queue->empty()) {
                        current_queue = &high_priority_queue;
                    }
                }
                if (arrival_queue.empty() && high_priority_queue.empty()) {
                    current_queue = &low_priority_queue;
                    if (low_priority_queue.empty()) {
                        current_queue = &arrival_queue;
                    }
                }
                if (current_queue != &arrival_queue) {
                    std::sort(current_queue->begin(), current_queue->end(), 
                        [&customers](int a, int b) -> bool {
                            return customers[a].slots_remaining < customers[b].slots_remaining;
                        });
                }
            }
            // If the current_queue is NOT empty
            if (!current_queue->empty()) {
                current_id = current_queue->front();
                current_queue->pop_front();
                if (current_queue == &arrival_queue) {
                    if (TIME_ALLOWANCE > customers[current_id].slots_remaining) {
                        time_out = current_time + customers[current_id].slots_remaining;
                    }
                    else {
                        time_out = current_time + TIME_ALLOWANCE;
                    }
                }
                else {
                    time_out = current_time + customers[current_id].slots_remaining;
                }
                customers[current_id].playing_since = current_time;
            }
        }
        // Runs the print_state method
        print_state(out_file, current_time, current_id, arrival_events, *current_queue);
        all_done = (arrival_events.empty() && arrival_queue.empty() && high_priority_queue.empty() && low_priority_queue.empty() && (current_id == -1));
    }
    return 0;
}
