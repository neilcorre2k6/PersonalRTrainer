# Example solution: Select, filter and sort
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students.csv')
score_table <- students[, c('student','exam_score')]
focused <- students[students$study_hours >= 3, ]
ranked <- students[order(students$exam_score, decreasing=TRUE), ]
