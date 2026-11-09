# Example solution: Work honestly with missing values
# One valid approach; equivalent results are accepted.

scores <- c(65, NA, 85, 90)
missing_count <- sum(is.na(scores))
average_score <- mean(scores, na.rm = TRUE)
print(average_score)
