__version__ = 0.00

#NOTE: all text in each filter must be matched. Text is case sensitive!
# each filter can contain multiple texts, e.g. ['Horse Racing', 'Hcap'] will
# find all handicap races

menu_filters = [
    ['Horse Racing'],     #filter No. 0
    ['Greyhound Racing']  #filter No. 1
]

#NOTE: these are the marketTypeCodes for get_markets()
#the list is numerous, however the following are common examples:
#Horse Racing: 'WIN', 'PLACE', 'ANTEPOST-WIN', 'SPECIAL', 'STEWARDS'
#Greyhound Racing: 'WIN', 'PLACE', 'FORECAST', 'ANTEPOST_WIN'
#Soccer: 'MATCH_ODDS', 'CORRECT_SCORE', 'OVER_UNDER_05', 'OVER_UNDER_15',
#        'OVER_UNDER_25'

market_types = [
    'WIN'
]


#Notes: bets correspond with menu_filters, so market_bets[0]
#are menu_filters[0]. If menu_filters contain 5 filters, there must
# be 5 bets in this list.
market_bets = [
    [ #bets for filter No. 0
        {'side': 'LAY', 'price': 1.01, 'stake': 2.00},
        {'side': 'LAY', 'price': 1.02, 'stake': 2.00}
    ],
    [ #bets for filter No. 2
        {'side': 'LAY', 'price': 1.01, 'stake': 2.00},
        {'side': 'LAY', 'price': 1.02, 'stake': 2.00}
    ]
    ]

#Note: this setting avoids transaction charges for placing 1000+ bets per
#hour. Do not exceed 1000. Count is only for this bot and does not include
#other bots.
max_transactions = 250


