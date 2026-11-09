# Example solution: Export a table and read it back
# One valid approach; equivalent results are accepted.

students <- read.csv('Data/students.csv')
exported <- students[, c('student','exam_score')]
dir.create('Outputs', showWarnings=FALSE)
write.csv(exported, 'Outputs/students_export.csv', row.names=FALSE)
reopened <- read.csv('Outputs/students_export.csv')
