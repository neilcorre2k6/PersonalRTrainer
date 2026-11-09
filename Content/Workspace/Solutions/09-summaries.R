# Example solution: Describe a group of values
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students.csv')
mean_score <- mean(students$exam_score)
median_score <- median(students$exam_score)
sample_size <- nrow(students)
high_count <- sum(students$exam_score >= 75)
