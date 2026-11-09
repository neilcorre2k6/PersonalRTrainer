# Example solution: Import CSV through the UI and code
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students.csv')
imported_rows <- nrow(students)
imported_names <- names(students)
head(students)
str(students)
