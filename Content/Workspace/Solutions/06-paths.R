# Example solution: Find your project root
# One valid approach; equivalent results are accepted.

print(getwd())
print(list.files())
data_found <- file.exists('Data/students.csv')
root_file_found <- file.exists('students.csv')
data_files <- list.files('Data')
