# Example solution: Compare groups and report missingness
# One valid approach; equivalent results are accepted.

clean_students <- read.csv('Data/students_extended.csv')
clean_students$exam_score[clean_students$student == 'Clara'] <- 88
group_summary <- aggregate(exam_score ~ group, data=clean_students, FUN=mean)
group_summary <- group_summary[order(group_summary$group), ]
known_hours <- sum(!is.na(clean_students$study_hours))
missing_hours <- sum(is.na(clean_students$study_hours))
