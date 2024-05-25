# Load necessary libraries
library(readxl)
library(dplyr)
library(ggplot2)
library(caret)
library(randomForest)
# Load the data
file_path <- "C:/Users/Lenovo/Downloads/ECESISdata2024/Assignment 3 - timeseries_data.xlsx"
data <- read_excel(file_path)
data <- data %>% rename(RTLMP = `HB_NORTH (RTLMP)`)
# Split the data into training and testing sets
set.seed(0)
trainIndex <- createDataPartition(data[[target]], p = 0.8, list = FALSE)
trainData <- data[trainIndex, ]
testData <- data[-trainIndex, ]

# Convert DATETIME to datetime format
data$DATETIME <- as.POSIXct(data$DATETIME, format="%Y-%m-%d %H:%M:%S")
rownames(data) <- data$DATETIME
train_datetime <-data[, which(names(trainData) == "DATETIME")]
test_datetime <-data[, which(names(testData) == "DATETIME")]

# Feature Engineering
data <- data %>%
  mutate(HOUR = as.numeric(format(DATETIME, "%H")),
         DAY_OF_WEEK = as.numeric(format(DATETIME, "%u")),
         MONTH = as.numeric(format(DATETIME, "%m")))

# Create lagged features
lags <- 24
for (lag in 1:lags) {
  data <- data %>%
    mutate(!!paste0("RTLMP_LAG_", lag) := lag(`HB_NORTH (RTLMP)`, lag),
           !!paste0("WIND_RTI_LAG_", lag) := lag(`ERCOT (WIND_RTI)`, lag),
           !!paste0("SOLAR_RT_LAG_", lag) := lag(`ERCOT (GENERATION_SOLAR_RT)`, lag),
           !!paste0("RTLOAD_LAG_", lag) := lag(`ERCOT (RTLOAD)`, lag))
}

# Drop rows with NA values created by lagging
data <- na.omit(data)

# Correlation Analysis
data <- data[, -which(names(data) == "DATETIME")]
numeric_cols <- sapply(data, is.numeric)
correlation_matrix <- cor(data[, numeric_cols])
correlation_rtlmp <- sort(correlation_matrix[, "HB_NORTH (RTLMP)"], decreasing = TRUE)
print(correlation_rtlmp)

# Define features and target variable
features <- grep("LAG|HOUR|DAY_OF_WEEK|MONTH", names(data), value = TRUE)
target <- "HB_NORTH (RTLMP)"


# Train the Linear Regression model
model <- train(trainData[, features], trainData[[target]], method = "lm")

# Make predictions
trainPred <- predict(model, trainData[, features])
testPred <- predict(model, testData[, features])

# Evaluate the model
train_mae <- mean(abs(trainPred - trainData[[target]]))
train_rmse <- sqrt(mean((trainPred - trainData[[target]])^2))
test_mae <- mean(abs(testPred - testData[[target]]))
test_rmse <- sqrt(mean((testPred - testData[[target]])^2))

cat("Train MAE:", train_mae, "\n")
cat("Train RMSE:", train_rmse, "\n")
cat("Test MAE:", test_mae, "\n")
cat("Test RMSE:", test_rmse, "\n")

