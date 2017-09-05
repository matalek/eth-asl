# Advanced Systems Lab, ETH, Autumn 2016

## Overview

This project was created as a part of Advanced Systems Lab course. From the project description:

> The project consists of the design and development of a middleware platform for key-value stores as well as the evaluation 
> and analysis of its performance, and development of an analytical model of the system, and an analysis of how the model 
> predictions compare to the actual system behavior. The middleware will have to perform load balancing operations by steering
> traffic to different servers depending on the request content, and will also perform primary-secondary replication.

At the end of the first milestone, the system had to:
- be stable,
- be able to forward requests to servers,
- collect results. 

Its performance had to measured in a 1 hour trace that shows throughput and response time plotted over time.

The aim of the second milestone was to conduct a detailed experimental evaluation of the system.

The goal of the final milestone was to develop an analytical queuing model for each component of the system and for the
system as a whole.

The full description of the project and detailed descriptions of milestones can be found [here](https://github.com/matalek/eth-asl/blob/master/docs).

The quality of the scripts used to perform the experiments is questionable.
This is due to a limited time and constantly chaging requirements regarding the experiments.
I spent most time working on the quality of the [Java source code](https://github.com/matalek/eth-asl/tree/master/src/pl/matal)
and reports submitted for every milestone
([milestone 1](https://github.com/matalek/eth-asl/blob/master/matusiaa-milestone1.pdf),
[milestone 2](https://github.com/matalek/eth-asl/blob/master/matusiaa-milestone2.pdf) and
[milestone 3](https://github.com/matalek/eth-asl/blob/master/matusiaa-milestone3.pdf)).

## Grading

Each milestone was graded on a scale of 0 to 200 points. I have scored the following results:

| Milestone | Points |
| ------------- |-------------|
| Milestone 1 | 190 |
| Milestone 2 | 170 |
| Milestone 3 | 180 |

My final grade from the course was 5.75 (with 4 being the lowest passing grade and 6 being the best grade).
