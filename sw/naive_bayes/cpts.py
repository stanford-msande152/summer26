# Auto-generated CPT module -- do not edit by hand.
# Created by naive_bayes.py on 2026-07-22.

TARGET_COLUMN = 'win'
TARGET_STATES = ['no', 'yes']
TARGET_PRIOR = [[0.4090909090909091, 0.5909090909090909]]

FEATURES = {
    'outlook': {
        'states': ['overcast', 'rain', 'sunny'],
        'matrix': [[0.09090909090909091, 0.4666666666666667], [0.45454545454545453, 0.26666666666666666], [0.45454545454545453, 0.26666666666666666]],
    },
    'temp': {
        'states': ['cool', 'hot', 'mild'],
        'matrix': [[0.2727272727272727, 0.3333333333333333], [0.2727272727272727, 0.3333333333333333], [0.45454545454545453, 0.3333333333333333]],
    },
    'humidity': {
        'states': ['high', 'normal'],
        'matrix': [[0.6, 0.35714285714285715], [0.4, 0.6428571428571429]],
    },
    'wind': {
        'states': ['strong', 'weak'],
        'matrix': [[0.7, 0.2857142857142857], [0.3, 0.7142857142857143]],
    },
}
