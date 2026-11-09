# Example solution: Correct and extend a table
# One valid approach; equivalent results are accepted.

raw_students <- read.csv('Data/students_extended.csv')
clean_students <- raw_students
clean_students$exam_score[clean_students$student == 'Clara'] <- 88
clean_students$study_minutes <- clean_students$study_hours * 60
with_new <- rbind(clean_students, data.frame(student='Maya', study_hours=4, exam_score=80, coffee_cups=1, group='A', study_minutes=240))
without_new <- with_new[with_new$student != 'Maya', ]
