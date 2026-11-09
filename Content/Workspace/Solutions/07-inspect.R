# Example solution: Inspect a larger, imperfect dataset
# One valid approach; equivalent results are accepted.

raw_students <- read.csv('Data/students_extended.csv', na.strings=c('', 'NA'))
missing_hours <- sum(is.na(raw_students$study_hours))
impossible_scores <- sum(raw_students$exam_score > 100, na.rm=TRUE)
groups <- sort(unique(raw_students$group))
