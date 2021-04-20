METHODS = {
    'scipy': ['NELDER-MEAD', 'COBYLA', 'POWELL', 'SLSQP', 'L-BFGS-B', 'BFGS',
              'CG', 'TNC', 'TRUST-KRYLOV', 'NEWTON-CG', 'DOGLEG', 'TRUST-NCG',
              'TRUST-EXACT', 'TRUST-CONSTR'],
    'gd': ['adam', 'adagrad', 'adamax', 'nadam', 'sgd', 'momentum', 'nesterov',
           'rmsprop', 'rmsprop-nesterov']
}

BASIS_SET_CHOICES = ['sto-3g']


def optimizer_methods(module: str):
    return METHODS[module]


def optimizer_modules():
    return list(METHODS.keys())


def basis_set_options():
    return BASIS_SET_CHOICES
