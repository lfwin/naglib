"""
Export all Latin and Greek letters as SymPy symbols, a la sympy.abc.
Caveats: 1. "lamda" takes the place of "lambda" due to namespace collision
         2. "Lamda" takes the place of "Lambda" for consistency
Other caveats: see docstring of sympy.abc

Examples
========
   >>> from naglib.abc import x, y, eta
"""

from sympy import Symbol, symbols
### Long imports with parentheses requires Python >= 2.4 ###
from sympy.abc import (A, B, C, D, E, F, G, H, I, J, K, L, M,
                       N, O, P, Q, R, S, T, U, V, W, X, Y, Z,
                       a, b, c, d, e, f, g, h, i, j, k, l, m,
                       n, o, p, q, r, s, t, u, v, w, x, y, z,
                       alpha, beta, gamma, delta, epsilon, zeta,
                       eta, theta, iota, kappa, lamda, mu, nu, xi,
                       omicron, pi, rho, sigma, tau, upsilon, phi,
                       chi, psi, omega)

Alpha, Beta, Gamma, Delta = symbols("Alpha, Beta, Gamma, Delta")
Epsilon, Zeta, Eta, Theta = symbols("Epsilon, Zeta, Eta, Theta")
Iota, Kappa, Lamda, Mu    = symbols("Iota, Kappa, Lamda, Mu")
Nu, Xi, Omicron, Pi       = symbols("Nu, Xi, Omicron, Pi")
Rho, Sigma, Tau, Upsilon  = symbols("Rho, Sigma, Tau, Upsilon")
Phi, Chi, Psi, Omega      = symbols("Phi, Chi, Psi, Omega")
