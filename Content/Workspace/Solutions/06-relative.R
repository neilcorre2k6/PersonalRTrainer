# Example solution: Use dot, parent folders and source
# One valid approach; equivalent results are accepted.

same_file <- file.exists('./Data/students.csv')
via_parent <- file.exists('Scripts/../Data/students.csv')
source('Scripts/helpers.R', local = TRUE)
print(course_label)
