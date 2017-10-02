from collections import defaultdict
import math
from random import sample 

def argmin(f, lst):
    return min(lst, key=lambda x: f(x))

def norm(a, b):
    return math.sqrt(sum([(a[i] - b[i])**2 for i in range(len(a))]))

def vecsum(a, b):
    if a == []:
        return b
    if b == []:
        return a
    return [a[i] + b[i] for i in range(len(a))]

def vecsum_list(lst):
    if len(lst) == 0:
        return []
    head, *tail = lst
    return vecsum(head, vecsum_list(tail))

def vecmult(a, v):
    return [a*x for x in v]

def compute_climatology(outcomes):
    climatology = defaultdict(float)
    m = len(outcomes)
    for outcome in outcomes:
        climatology[outcome] += 1 / m
    return climatology

class ForecastLearner(object):
    def __init__(self, data, metric=norm):
        self.metric = metric
        self.examples = [d[0:-1] for d in data]
        self.results = [d[-1] for d in data]
        self.num_examples = len(self.examples)
        self.set_extremes()
        self.climatology = compute_climatology(self.results)
        self.set_imputed_features()

    def set_extremes(self):
        maximum = -math.inf
        minimum = math.inf
        for d in self.examples:
            minimum = min(d[0][0][1], minimum)
            maximum = max(d[-1][0][0], maximum)
        self.minimum = minimum
        self.maximum = maximum

    def set_imputed_features(self):
        imputed = []
        for d in self.examples:
            imputed.append(self.impute_example(d))
        self.imputed = imputed
    
    def impute_example(self, example):
        max_range = self.maximum
        min_range = self.minimum
        imputed = []
        for feature in example:
            lower = feature[0][0]
            upper = feature[0][1]
            prob = feature[1]
            if upper == lower:
                imputed.append(prob)
                continue
            range_vals = range(max(lower, min_range), min(upper, max_range)+ 1)
            range_prob = sum(self.climatology[k] for k in range_vals)
            conditional_climatology = defaultdict(
                float,
                {k: (self.climatology[k] / range_prob) for k in range_vals}
            )
            if lower == -math.inf:
                if upper == min_range:
                    imputed.append(prob)
                    continue
                leftover = 1 
                for val in range(min_range + 1, int(upper) + 1):  
                    imputed.append(prob * conditional_climatology[val])
                    leftover -= conditional_climatology[val]
                imputed.insert(0, prob * leftover)
            elif upper == math.inf:
                if lower == max_range:
                    imputed.append(feature[1])
                    continue
                leftover = 1 
                for val in range(lower, max_range):
                    imputed.append(prob * conditional_climatology[val])
                    leftover -= conditional_climatology[val]
                imputed.append(prob * leftover)
            else:
                for val in range(int(lower), int(upper) + 1):
                    imputed.append(prob * conditional_climatology[val])
        return [round(a, 3) for a in imputed]


    def cluster(self, k):
        # initialize random centers and clusters
        examples = self.imputed
        centers = sample(examples, k)
        while True:
            clusters = [[] for i in range(k)]
            for j in range(len(examples)):
                best_cluster = argmin(
                    lambda i: self.metric(examples[j], centers[i]),
                    range(k)
                )
                clusters[best_cluster].append(j)
            new_centers = [vecmult(1 / len(c), vecsum_list([examples[i] for i in c])) for c in clusters]
            if new_centers == centers:
                break
            centers = new_centers

        self.centers = centers
        self.cluster_climatologies = [
            compute_climatology([self.results[i] for i in cluster]) 
            for cluster in clusters
        ]
    
    def predict(self, example):
        best_cluster = argmin(
                lambda i: self.metric(example, self.centers[i]),
                range(len(self.centers))
        )
        return self.cluster_climatologies[best_cluster]


    def prettyprint_features(self):
        headers = [str(e) for e in list(range(self.minimum, self.maximum + 1))]
        headers[0] = '<={}'.format(headers[0])
        headers[-1] =  '>={}'.format(headers[-1])
        headers.append('result')
        print('\t'.join(headers))
        for i in range(self.num_examples):
            print('\t'.join(str(a) for a in self.imputed[i] + [self.results[i]]))

