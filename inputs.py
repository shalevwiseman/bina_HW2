small_inputs = [

    # 3x3 2 taxi, 2 passengers w/ 1 possible goals, low fuel
    {
        "optimal": False,
        "map": [['P', 'P', 'G'],
                ['P', 'P', 'P'],
                ['G', 'P', 'P']],
        "taxis": {'taxi 1': {"location": (0, 0), "fuel": 3, "capacity": 1},
                  'taxi 2': {"location": (0, 1), "fuel": 3, "capacity": 1}},
        "passengers": {'Dana': {"location": (0, 2), "destination": (2, 2),
                                "possible_goals": ((2, 2),), "prob_change_goal": 0.1},
                       'Dan': {"location": (2, 0), "destination": (2, 2),
                               "possible_goals": ((2, 2),), "prob_change_goal": 0.1}
                       },
        "turns to go": 100
    }
]


