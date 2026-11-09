# Example solution: Make a chart understandable
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students_extended.csv')
students$exam_score[students$student == 'Clara'] <- 88
plot_data <- students[complete.cases(students[, c('study_hours','exam_score')]), ]
point_symbols <- ifelse(plot_data$group == 'A', 16, 17)
point_colors <- ifelse(plot_data$group == 'A', '#087E8B', '#A55224')
plotted_count <- nrow(plot_data)
plot(plot_data$study_hours, plot_data$exam_score, col=point_colors, pch=point_symbols, main='Fictional students: hours and scores', xlab='Study hours per week', ylab='Exam score (0-100)', ylim=c(0,100))
legend('topleft', legend=c('Group A','Group B'), col=c('#087E8B','#A55224'), pch=c(16,17), bty='n')
