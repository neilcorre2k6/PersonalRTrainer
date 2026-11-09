# Example solution: Build scatter and line plots
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students.csv')
x_hours <- students$study_hours
y_scores <- students$exam_score
plot(x_hours, y_scores, xlab='Study hours', ylab='Exam score', pch=19)
days <- 1:7
daily_hours <- c(1,2,1,3,2,4,3)
plot(days, daily_hours, type='b', xlab='Day', ylab='Study hours')
