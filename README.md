# Description
The purpose of this project is to employ basic clustering techniques to 
extend a forecast given by some forecaster for a particular event to try
predict probabilities of unforecast outcomes of that event. 

# Motivation and Method
As a toy scenario to motivate the forecasting problem: 

Suppose we live in the metro area of our city, and our local weather has all their equipment
setup at the airport outside of the city. Let M be the event of rain in the
metro area, and A the event of rain at the airport. We would like to have an
approximation of P(M), the probability of the event M, so we can make an
appropriate decision about packing a rain coat for the day. But the only
information the forecaster tells us is P(A). Obviously M and A are highly
correlated, but can we do any better than just using P(A) as our approximation
for P(M)?  The general idea is to  use the available historical data of pairs (P(A), M) (we have such a pair for each day of the year), 
and  generate a predictor that takes in P(A) and outputs P(M). 

In this case, there is an apparent naive approach: say that P(A) = 0.5. Then we
could look at our historical data and count the number of days where P(A) = 0.5, and then
 output the fraction of days where the event M. For example, if among all the
days where P(A) was forecast to be 0.5, it rained in the metro area 60 times
and did not rain 40 times, then we would output P(M) = 0.6.

Now, obviously this method isn't perfect, but it may perform quite well.
However, there are two primary complications in more general scenarios, which
are the core of what makes this problem complex and interesting:

1. Suppose our forecaster gives us very fine-grained forecast information -
   e.g., instead of seeing P(A) = 0.5, maybe we see P(A) = 0.5023. Then there
may be very few days (historically) to compute our relative frequency,
which could result in a poor prediction. In this case, how should we choose
which days to consider when computing our relative frequency? 

2. Let M_k be the event where there are at least k millimeters of rain. 
   Then on days where very little rain is anticipated, perhaps the forecaster
    would only give us the information P(A_10), and P(A_15), whereas on days
    where a lot of rain is expected, we could get P(A_50) and P(A_75). 
    In this case, it is again unclear how we should choose which days to
    consider when computing our relative frequency: We could just  select days
    for which we have forecasts for the exact same events, but this again seems
    unnecessarily limiting and could result in situation where we have very few
    days from which we draw our relative frequencies.


To solve the first problem, we use k-means clustering to group together days
where the forecasts were 'similar'. Future work is it use more interesting
metrics than the Euclidean one to complete this clustering. 

To solve the second problem, we impute probabilities for all our examples in an
'unbiased' way by conditioning the observed forecast with the historical
data. For example, if we have (in all our history) seen forecasts for A_0, A_1, ...,  A_10,
and we receive an example where we get forecasts for A_5 and A_7 on some
particular day, then we 'impute' A_4 to be #(num days where A = 4) / #(num days
where A<= 5) * P(A_5). We would use the same logic to impute the probabilities
for A_0 through A_10.
