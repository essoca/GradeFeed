# GradeFeed
Web app written in Python (using [web.py](http://webpy.org/)) to grade problem sets based on rubrics that the user defines. This can be run, for instance, in [cloud9](https://aws.amazon.com/cloud9/). 

The workflow is pretty simple:

- The user uploads the class roster.
- For each assigment, the total number of problems to grade and maximum grade are defined.
- The app then prompts to complete a table where each problem is defined (labels for each problem, the number of items or subquestions, what it evaluates, etc).
- The app then determines how to distribute the maximum grade among the problems (based on user preference).
- A rubric is then defined by the user, stating reasons for deducting points and the corresponding percent deduction.
- The class roster then appears with buttons to grade each student and each problem. During execution, the rubric defined by the user is then applied. Input on how each student answered may be collected at this stage to do data analysis later.
- After everybody is graded, a table appears with the final grades and some statistics.

This is the first version, and does minimal things. Improvement is needed.