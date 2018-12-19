# Capstone_1 NBA Points Predictor

Over the past few years, fantasy sports, especially fantasy football and basketball is becoming more popular. As such, the need for reliable estimators of fantasy sports statistical categories is becoming more and more important. We know that the more accurate the estimator is for the week, the more the user/team owner can use this data to choose who they can play for the week depending on their projected statistical categories. Currently many users use the year-to-date averages for their sports statistics as an estimator. Our goal is to use a machine learning algorithm to project out our statistical categories.

While we would love to be able to do this for every single stat, we unfortunately do not have the time currently. We may do this later on. For now, we will be focusing on the points statistical category.

## Dataset
We scraped data from the NBA API nba_py which can be found here:
https://github.com/seemethere/nba_py

We used this two major libraries here and did several manipulations to get the data all in one folder.

## Exploratory Data Analysis

We found the following observations:
1. On average, players had a tendency to have higher points as they played more games.
2. Player position, whether they were all-stars, home vs away  had a high impact on their averages.
3. FG2M, FG2A, FG3M, FG3A, FTM, FTA were all directly correlated to a player's point scored.

## Predictive Modelling

As this is a regression problem, we focused on two main models:

1. Linear Regression
2. Random Forest Regression

We saw that random forest has a much smoother prediction than the average points per player. This may be due to the fact that we are "smoothing" our data by applying the Y-T-D averages and the 3 game average. We may want to remove these to ensure that we capture our data more clearly.

## Conclusion/Next steps
Based on our machine learning algorithms, we have concluded the following:

1. Using the metric of mean absolute error, our linear regression model was not able to predict out points as accurately as using the Y-T-D average. Especially if we were to remove multicollinearity from our resuls. 
2. Random forest regressor was much better at predicting with a mean absolute error of ~4.49 compared to the YTD mean absolute error was ~4.40. We only performed 1 stage of parameter tuning, but believe that as we do more, we should be getting better results.

Here are methods that I believe can improve our model more (which I will complete later on):

1. Have more granular data. Obviously we had to make some assumptions in our data (e.g. try and pick out who is an all-star and who is not, or who is a starter and who is not). Ideally we do not have to make any assumptions in our data gathering. We would take it for what it is. By us making these assumptions we may be incorparating some biasness in our model that is skewing our results. Thus we would have to do further exploratory data analysis to get this model correct.
2. We would have to due further parameter tuning via gridsearch methods to ensure that we are optimizing our model correctly. Unfortunately, I did not have time to do this for this iteration. But continuously optimizing our parameters is an essential step in ensuring our model is training properly.



