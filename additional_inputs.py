additional_inputs = [
    {
        'optimal': False,
        "turns to go": 50,
        'map': [['P', 'P', 'P', 'P', 'P'],
                ['P', 'I', 'P', 'G', 'P'],
                ['P', 'P', 'I', 'P', 'P'],
                ['P', 'P', 'P', 'I', 'P']],
        'taxis': {'taxi 1': {'location': (1, 3), 'fuel': 10, 'capacity': 3}},
        'passengers': {'Michael': {'location': (3, 4), 'destination': (2, 1),
                                   "possible_goals": ((2, 1), (3, 4)), "prob_change_goal": 0.1},
                       'Freyja': {'location': (0, 0), 'destination': (2, 1),
                                  "possible_goals": ((2, 1), (0, 0)), "prob_change_goal": 0.3}}
    }
]
