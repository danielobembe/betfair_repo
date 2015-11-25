#File Description: Sets rules for filtering and interacting with markets
__version__ =  0.00

menu_filters = [
    ['Horse Racing'],       #Filter No. 0
    ['Greyhound Racing']    #Filter No. 1
]

# https://developer.betfair.com/visualisers/api-ng-sports-operations/
market_types = [
    'WIN'
]

market_bets = [
    [ #bets for Filter No. 0
        {'side': 'LAY', 'price': 1.01, 'stake': 2.00},
        {'side': 'LAY', 'price': 1.02, 'stake': 2.00}
        ],
    [ #bets for Filter No. 1
        {'side': 'LAY', 'price': 1.01, 'stake': 2.00},
        {'side': 'LAY', 'price': 1.02, 'stake': 2.00}
        ]
]


max_transactions = 250

