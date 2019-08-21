# Team Selector

I need to make student teams in my classes for which I ask students to specify some people (up to 3) they want to pair with and some (up to 2) they do not. This program outputs candidate pairings which are the most in accordance with the students' preferences.

## How to Use

You _only_ need to make the following edits in the `init_students` function in _select.py_.
1. Add the names of _all_ the students in your class who need to be paired to the indicated list. This includes students who did not indicate an preference, e.g. they did not fill the required form by the deadline, but still need to be paired. The names _must be unique_.
1. Enter the preferences using the `add_green` and `add_red` functions. Their syntax is as follows.
```
# specify one or more dst_student that src_student wants to work with.
add_green(students, <src_student>, [<dst_student_1>, <dst_student_2>, ... , <dst_student_n>])
# specify one or more dst_student that src_student does not want to work with.
add_red(students, <src_student>, [<dst_student_1>, <dst_student_2>, ... , <dst_student_n>])
```
`add_green` specifies the `dst_student`s that `src_student` wants to work with and `add_red` specifies the `dst_student`s that `src_student` _does not want to work with. Note that the last argument to both functions is a list even if it has only 1 member. If there is no data for a function call, e.g. a `src_student` has not specified any `dst_student` that they want to work with, then there is no need to make a call to the correspodning function.

## How it Works


## Limitations


## Extensions


## Bugs

The program fails or crashes? You have found an error? You want to know more? This odcumentation sucks?

For the above or any other issues, please report
- to <wsaleem@gmail.com> 
- to <waqar.saleem@sse.habib.edu.pk>
- by seeing me in C-103
- by calling me at 5223
- by fixing it yourself and submitting a Pull Request :)
