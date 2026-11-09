# Example solution: Export PNG and PDF charts
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students.csv')
dir.create('Outputs', showWarnings=FALSE)
png('Outputs/study_scatter.png', width=1000, height=700)
plot(students$study_hours, students$exam_score, main='Fictional study habits', xlab='Study hours', ylab='Exam score', pch=19, col='#087E8B')
dev.off()
pdf('Outputs/study_scatter.pdf', width=7, height=5)
plot(students$study_hours, students$exam_score, main='Fictional study habits', xlab='Study hours', ylab='Exam score', pch=19, col='#087E8B')
dev.off()
