# Example solution: Build bar charts and histograms
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students.csv')
bar_values <- students$exam_score
bar_labels <- students$student
barplot(bar_values, names.arg=bar_labels, ylim=c(0,100), ylab='Score')
score_hist <- hist(students$exam_score, plot=FALSE)
histogram_count <- sum(score_hist$counts)
hist(students$exam_score, main='Fictional exam scores', xlab='Score')
