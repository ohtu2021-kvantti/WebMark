METHODS = {
    'scipy': ['NELDER-MEAD', 'COBYLA', 'POWELL', 'SLSQP', 'L-BFGS-B', 'BFGS',
              'CG', 'TNC', 'TRUST-KRYLOV', 'NEWTON-CG', 'DOGLEG', 'TRUST-NCG',
              'TRUST-EXACT', 'TRUST-CONSTR'],
    'gd': ['adam', 'adagrad', 'adamax', 'nadam', 'sgd', 'momentum', 'nesterov',
           'rmsprop', 'rmsprop-nesterov']
}


def get_methods(module: str):
    return METHODS[module]


def get_modules():
    return list(METHODS.keys())
