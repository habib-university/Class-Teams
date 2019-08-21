# Team Selector

I need to make student teams in my classes for which I ask students to specify some people (up to 3) that they want to pair with and some (up to 2) that they _do not_ want to work with. This program outputs candidate pairings which are the most in accordance with the students' preferences.

## How to Use

You _only_ need to make the following edits in the `init_students` function toward the bottom of the file,  _select.py_.
1. Add the names of _all_ the students in your class who need to be paired to the indicated list. This includes students who did not indicate an preference, e.g. they did not fill the required form by the deadline, but still need to be paired. The names _must be unique_.
1. Enter the preferences using the `add_green` and `add_red` functions. Their syntax is as follows.
```
# specify one or more dst_student that src_student wants to work with.
add_green(students, <src_student>, [<dst_student_1>, <dst_student_2>, ... , <dst_student_n>])
# specify one or more dst_student that src_student does not want to work with.
add_red(students, <src_student>, [<dst_student_1>, <dst_student_2>, ... , <dst_student_n>])
```
`add_green` specifies the `dst_student`s that `src_student` wants to work with and `add_red` specifies the `dst_student`s that `src_student` _does not_ want to work with. All students have to be specified using the _exact_ names used in Step 1 above. Note that the last argument to both functions is a list even if it has only 1 member. If there is no data for a function call, then there is no need to make a call to the correspodning function. For example, some students specify no one under the list of students that they do not want to work with. For these students, `add_red` must not be called.

The program outputs a _goodness score_ between 0 (worst) and 1 (best) of the computed pairings. The best pairing is one where all vertex pairs are as per the students' preferences. As it is usually impossible to meet all preferences, a score of 0.6 or above is good enough.

## Requirements

- To run the program, you need at least python 3.6 becasuse of the use of `f-string`s.
- The program also makes use of the `colorama` package which may not be installed by default. It was not for me. Run `pip install colorama` or `pip3 install colorama` depending on your platform.

## How it Works

The problem is modeled as a directed graph. Every student is a node. If student A wants to work with student B, B is considered A's _friend_ and the graph contains a green edge from A to B. If student X does not want to work with student Y, Y is considered X's _enemy_ and the graph contains a red edge from X to Y. It is not rare to end up with a vertex pair with a green edge one way and a red edge the other way! As the red and green degree of each vertex is typically small, few vertex pairs are connected.

The program tries to partition the vertices into pairs such that no pair contains an enemy. It does so by randomly selecting a vertex as _source_ and selecting as _destination_ a friend for whom _source_ is not an enemy. If _destination_ is already part of another pair, a new _destination_ is selected. If no such selection is possible, _destination_ is selected from the vertices that are not connected to _source_. Once an acceptable _destination_ is found, _source_ and _destination_ are added as a pair to the existing set of pairs. The set of pairs is called a _pairing_. A pairing is scored as the number of friends that are paired in it.

The above process is repeated several times to maximize the likelihood of a high scoring pairing.

## Limitations

I beleive that it is possible, theoretically, for the initial set of preferences to not lead to a solution, i.e. it is impossible to pick a pair that does not include an enemy. However, I have not encountered that in practice.

I have also not considered how this works for an odd number of students. The program could be run for an even number of students, leaving one student out, and that remining student could be inserted manaully into a computed pair.

## Extensions

This is probably a variant of the _vertex cover_ problem. If so, a more efficient and theroteically sound solution may exist.

## Bugs

The program fails or crashes? You have found an error? You want to know more? This odcumentation sucks?

For the above or any other issues, please report
- to <wsaleem@gmail.com> 
- to <waqar.saleem@sse.habib.edu.pk>
- by seeing me in C-103
- by calling me at 5223
- by fixing it yourself and submitting a Pull Request :)
