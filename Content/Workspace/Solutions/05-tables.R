# Example solution: Meet a data frame
# One valid approach; equivalent results are accepted.

students <- data.frame(student=c('Anna','Ben','Clara'), study_hours=c(2,4,5), exam_score=c(65,78,88))
scores <- students$exam_score
first_student <- students[1, ]
head(students)
str(students)
