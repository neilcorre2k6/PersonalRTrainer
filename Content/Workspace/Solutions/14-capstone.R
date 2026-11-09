# Example solution: Tell a careful data story
# One valid approach; equivalent results are accepted.

raw_students <- read.csv('Data/students_extended.csv', na.strings=c('', 'NA'))
clean_students <- raw_students
clean_students$exam_score[clean_students$student == 'Clara'] <- 88
clean_students$study_minutes <- clean_students$study_hours * 60
missing_hours <- sum(is.na(clean_students$study_hours))
group_summary <- aggregate(exam_score ~ group, data=clean_students, FUN=mean)
group_summary <- group_summary[order(group_summary$group), ]
plot_data <- clean_students[complete.cases(clean_students[, c('study_hours','exam_score')]), ]
draw_chart <- function() {
  colors <- ifelse(plot_data$group == 'A', '#087E8B', '#A55224')
  symbols <- ifelse(plot_data$group == 'A', 16, 17)
  plot(plot_data$study_hours, plot_data$exam_score, col=colors, pch=symbols, main='Fictional student study', xlab='Study hours per week', ylab='Exam score (0-100)', ylim=c(0,100))
  legend('topleft', legend=c('Group A','Group B'), col=c('#087E8B','#A55224'), pch=c(16,17), bty='n')
}
draw_chart()
dir.create('Outputs', showWarnings=FALSE)
write.csv(clean_students, 'Outputs/final_clean.csv', row.names=FALSE)
write.csv(group_summary, 'Outputs/final_summary.csv', row.names=FALSE)
png('Outputs/final_chart.png', width=1000, height=700)
draw_chart()
dev.off()
pdf('Outputs/final_chart.pdf', width=7, height=5)
draw_chart()
dev.off()
stopifnot(nrow(read.csv('Outputs/final_clean.csv')) == 12)
stopifnot(nrow(read.csv('Outputs/final_summary.csv')) == 2)
