from sympy import I, Matrix as spmatrix, sympify, zeros

from naglib.startup import TOL
from naglib.exceptions import BertiniError, NonPolynomialException, NonHomogeneousException
from naglib.core.base import NAGobject, scalar_num, AffinePoint
        
class PolynomialSystem(NAGobject):
    """
    A polynomial system
    """
    def __init__(self, polynomials, variables=None, parameters=None, homvar=None):
        """
        Initialize the PolynomialSystem object
        """
        from re import sub as resub
        
        if type(polynomials) == str:
            polynomials = [polynomials]
        try:
            polynomials = list(polynomials)
        except TypeError:
            polynomials = [polynomials]
        
        self._polynomials = []
        
        # check if any polynomial is a string and contains '^'
        for p in polynomials:
            if type(p) == str:
                p = resub(r'\^', r'**', p)
            p = sympify(p)
            self._polynomials.append(p)

        self._polynomials = spmatrix(self._polynomials)
            
        # check if any given functions are actually not polynomials
        for p in self._polynomials:
            if not p.is_polynomial():
                msg = "function {0} is not a polynomial".format(p)
                raise NonPolynomialException(msg)
        
        # set parameters, if given...
        if parameters:
            try:
                parameters = list(parameters)
            except TypeError:
                parameters = [parameters]
            parameters = [sympify(p) for p in parameters]
            self._parameters = spmatrix(parameters)
        # ...otherwise, set parameters to empty matrix
        else:
            self._parameters = spmatrix()
        
        # set variables, if given...
        if variables:
            try:
                variables = list(variables)
            except TypeError:
                variables = [variables]
            variables = [sympify(v) for v in variables]
            self._variables = spmatrix(variables)
        # ...otherwise, determine variables from non-parameter free symbols
        else:
            variable_list = set()
            param_set = set(self._parameters)
            # gather free symbols from each polynomial
            free_sym = [p.free_symbols for p in self._polynomials]
            variable_list = reduce(lambda x, y: x.union(y), free_sym)
            # remove parameters from set of free symbols
            variable_list = list(variable_list.difference(param_set))
            variable_strings = [str(v) for v in variable_list]
            variable_strings.sort()
            variables = sympify(variable_strings)
            self._variables = spmatrix(variables)
            
        # set homogenizing variable, if given
        if homvar:
            homvar = sympify(homvar)
            try: # multihomogeneous?
                homvar = list(homvar)
            except TypeError:
                homvar = [homvar]
            if len(homvar) > 1:
                msg = "multihomogeneous systems not yet supported"
                raise NotImplementedError(msg)
            
            # but check to see if it's legit
            if homvar[0] not in self._variables:
                msg = "homogenizing variable {0} not in variables".format(homvar)
                raise ValueError(msg)
            
            self._homvar = spmatrix(homvar)
        else:
            self._homvar = spmatrix()
            
        d = []
        params = list(self._parameters)
        ones = [1 for param in params]
        paramsubs = zip(params,ones)
        
        # keep parameters out of degree calculation
        for poly in self._polynomials:
            p = poly.subs(paramsubs)
            if p.is_number:
                deg = 0
            else:
                deg = p.as_poly().total_degree()
            # check if polynomial is homogeneous
            if self._homvar:
                terms = p.as_ordered_terms()
                for t in terms:
                    if t.is_number and deg != 0:
                        msg = "polynomial {0} is not homogeneous".format(p)
                        raise NonHomogeneousException(msg)
                    elif t.is_number:
                        pass
                    elif t.as_poly().total_degree() != deg:
                        msg = "polynomial {0} is not homogeneous".format(p)
                        raise NonHomogeneousException(msg)
            d.append(deg)
            
        self._degree = tuple(d)
        self._num_variables = len(self._variables)
        self._num_polynomials = len(self._polynomials)
            
    def __str__(self):
        """
        x.__str__() <==> str(x)
        """
        polynomials = self._polynomials
        # even up the lengths of the polynomial strings
        pstrs = [str(p) for p in polynomials]
        #strlens = [len(f) for f in fstrs]
        #maxlen = max(strlens)
        #fstrs = [' '*(maxlen - len(f)) + f for f in fstrs]
        #fstr = '\n'.join(['[{0}]'.format(f) for f in fstrs])
        repstr = '{' + ', '.join([str(p) for p in pstrs]) + '}'
        return repstr
    
    def __repr__(self):
        """
        x.__repr__() <==> repr(x)
        """
        polynomials  = list(self._polynomials)
        variables    = list(self._variables)
        parameters   = list(self._parameters)
        homvar       = list(self._homvar)
        repstr = 'PolynomialSystem({0},{1},{2},{3})'.format(polynomials,
                                                            variables,
                                                            parameters,
                                                            homvar)
        
        return repstr
    
    def __getitem__(self, key):
        """
        x.__getitem__(y) <==> x[y]
        """
        polynomials = self._polynomials
        return polynomials[key]
    
    def __neg__(self):
        """
        x.__neg___() <==> -x
        """
        npolynomials = -self._polynomials
        variables = self._variables
        parameters = self._parameters
        homvar = self._homvar
        return PolynomialSystem(npolynomials, variables, parameters, homvar)
    
    def __add__(self, other):
        """
        x.__add__(y) <==> x + y
        """
        if not isinstance(other, PolynomialSystem):
            t = type(other)
            msg = "unsupported operand type(s) for +: 'PolynomialSystem' and '{0}'".format(t)
            raise TypeError(msg)
        
        spoly  = self._polynomials
        opoly  = other._polynomials
        spolct = len(spoly)
        opolct = len(opoly)
        
        # different sizes of systems
        if spolct != opolct:
            msg = "can't add systems of different sizes; cowardly backing out"
            raise ValueError(msg)
        
        shomvar = self._homvar
        ohomvar = other._homvar
        sdeg    = self._degree
        odeg    = other._degree
        
        # check homogenizing variables
        if shomvar and ohomvar and shomvar == ohomvar:
            # both have same homogenizing variables and degrees; all is well
            if sdeg == odeg:
                svars = set(self._variables)
                ovars = set(other._variables)
                spars = set(self._parameters)
                opars = set(other._parameters)
                
                # ensure the parameters of x are not the variables of y
                if svars.intersection(opars) or spars.intersection(ovars):
                    msg = "variables and parameters in summands overlap; cowardly backing out"
                    raise ValueError(msg)
                
                newpoly = spoly + opoly
                newpsym = [p.free_symbols for p in newpoly]
                newpsym = reduce(lambda x, y: x.union(y), newpsym)
                newvars = (svars.union(ovars)).intersection(newpsym)
                newpars = (spars.union(opars)).intersection(newpsym)
                newvars = sorted([str(v) for v in newvars])
                newpars = sorted([str(p) for p in newpars])
                newvars = sympify(newvars)
                newpars = sympify(newpars)
                
                return PolynomialSystem(newpoly, newvars, newpars, shomvar)
            else:
                msg = "multihomogeneous systems not yet supported"
                raise NotImplementedError(msg)
        elif shomvar or ohomvar:
            msg = "multihomogeneous systems not yet supported"
            raise NotImplementedError(msg)
        else: # no homogenizing variables
            svars = set(self._variables)
            ovars = set(other._variables)
            spars = set(self._parameters)
            opars = set(other._parameters)
            
            # ensure the parameters of x are not the variables of y
            if svars.intersection(opars) or spars.intersection(ovars):
                msg = "variables and parameters in summands overlap; cowardly backing out"
                raise ValueError(msg)
            
            newpoly = spoly + opoly
            newpsym = [p.free_symbols for p in newpoly]
            newpsym = reduce(lambda x, y: x.union(y), newpsym)
            newvars = (svars.union(ovars)).intersection(newpsym)
            newpars = (spars.union(opars)).intersection(newpsym)
            newvars = sorted([str(v) for v in newvars])
            newpars = sorted([str(p) for p in newpars])
            newvars = sympify(newvars)
            newpars = sympify(newpars)
            
            return PolynomialSystem(newpoly, newvars, newpars)
    
    def __sub__(self, other):
        """
        x.__sub__(y) <==> x - y
        """
        if not isinstance(other, PolynomialSystem):
            t = type(other)
            msg = "unsupported operand type(s) for +: 'PolynomialSystem' and '{0}'".format(t)
            raise TypeError(msg)
        
        other = -other
        return self + other
    
    def __mul__(self, other):
        """
        x.__mul__(y) <==> x*y
        """
        if not scalar_num(other):
            t = type(other)
            msg = "unsupported operand type(s) for *: 'PolynomialSystem' and '{0}'".format(t)
            raise TypeError(msg)
        
        polynomials = other*self._polynomials
        variables = self._variables
        parameters = self._parameters
        homvar = self._homvar
        if other == 0:
            return PolynomialSystem(polynomials)
        else:
            return PolynomialSystem(polynomials, variables, parameters, homvar)
        
    def __div__(self, other):
        """
        x.__div__(y) <==> x/y
        """
        return self.__truediv__(other)
            
    def __truediv__(self, other):
        """
        x.__truediv__(y) <==> x/y
        """
        if not scalar_num(other):
            t = type(other)
            msg = "unsupported operand type(s) for /: 'PolynomialSystem' and '{0}'".format(t)
            raise TypeError(msg)
        else:
            if other == 0:
                msg = "division by zero"
                raise ZeroDivisionError(msg)
            polynomials = self._polynomials/other
            variables = self._variables
            parameters = self._parameters
            homvar = self._homvar
            return PolynomialSystem(polynomials, variables, parameters, homvar)
        
    def assign_parameters(self, params):
        """
        Set params as parameters in self
        """
        if not hasattr(params, '__iter__'):
            params = [params]
        params = set(sympify(params))
        
        sparams = set(self._parameters).union(params)
        svars   = set(self._variables).difference(sparams)
        
        str_pars = sorted([str(p) for p in sparams])
        str_vars = sorted([str(v) for v in svars])
        
        self._parameters = spmatrix(sympify(str_pars))
        self._variables  = spmatrix(sympify(str_vars))
        
    def dehomogenize(self):
        """
        Dehomogenize the system
        
        If already nonhomogeneous, return self
        """
        hompolys = self._polynomials
        hompolys = spmatrix([p.expand() for p in hompolys])
        homvars = self._variables
        parameters = self._parameters
        degree = self._degree
        
        if not self._homvar:
            return self
        else:
            homvar = self._homvar[0] # this will change for multihomogeneous polynomials
        
        homvars = list(homvars)
        dex = homvars.index(homvar)
        homvars.pop(dex)
        variables = spmatrix(homvars)
        
        polynomials = hompolys.subs({homvar:1})
        
        return PolynomialSystem(polynomials, variables, parameters)
        
    def equals(self, other, strict=True):
        """
        x.equals(y) <==> x == y
        
        A probability-1 algorithm to determine equality
        Optional arguments:
        strict -- if True, force each system to have the same variables,
                  parameters, by name; otherwise, allow the same number
                  of variables and parameters, but not necessarily share
                  names. e.g.,
                  `F = PolynomialSystem('x**2 - 1')
                   G = PolynomialSystem('y**2 - 1')
                   F.equals(G, strict=True) == False
                   F.equals(G, strict=False) == True`
        """
        if not isinstance(other, PolynomialSystem):
            return False
        # shape test
        if self.shape != other.shape:
            return False
        
        svars = list(self._variables)
        ovars = list(other._variables)
        spars = list(self._parameters)
        opars = list(other._parameters)
        spoly = self._polynomials
        opoly = other._polynomials
        salls = svars + spars
        oalls = ovars + opars
        
        if strict and salls != oalls:
                return False
        
        from random import random as rand
        rsubs = []
        for vp in salls:
            try:
                real = rand()/rand()
                imag = rand()/rand()
            except ZeroDivisionError:
                return self == other
            rsubs.append(real + I*imag)
        
        ssubs = zip(salls, rsubs)
        osubs = zip(oalls, rsubs)
        
        res = spoly.subs(ssubs) - opoly.subs(osubs)
        return res.norm() < TOL
    
    def evalf(self, varpt, parpt=[]):
        """
        """
        variables = list(self._variables)
        parameters = list(self._parameters)
        polynomials = self._polynomials
        if len(varpt) != len(variables):
            msg = "point {0} is not in the domain of {1}".format(varpt, self)
            raise ValueError(msg)
        elif len(parpt) != len(parameters):
            msg = "point {0} is not a valid parameter for {1}".format(parpt, self)
        
        varsubs = dict(zip(variables, varpt) + zip(parameters, parpt))
        
        return AffinePoint(polynomials.evalf(subs=varsubs))
        
    def homogenize(self):
        """
        Homogenize the system
        
        If already homogeneous, return self
        """
        polynomials = [p.expand() for p in self._polynomials]
        variables = list(self._variables)
        parameters = list(self._parameters)
        degree = self.degree
        
        if self._homvar:
            return self
        
        # create a new homogenizing variable
        p0 = sympify('p')
        while p0 in variables or p0 in parameters:
            p0 = str(p0)
            p0 += '0'
            p0 = sympify(p0)
            # shouldn't last too long
        
        varsubs = [v/p0 for v in variables]
        varsubs = zip(variables, varsubs)
        
        homvars = [p0] + variables
        hompolys = []
        for p in polynomials:
            d = p.as_poly().total_degree()
            hp = (p0**d * p.subs(varsubs)).expand()
            hompolys.append(hp)
        return PolynomialSystem(hompolys, homvars, parameters, p0)
        
    def jacobian(self):
        """
        Returns the Jacobian, the polynomial system, and the variables,
        all as symbolic matrices
        """
        variables = self._variables
        polynomials = self._polynomials
        num_polynomials,num_variables = len(polynomials),len(variables)
        jac = zeros(num_polynomials,num_variables)
        for i in range(num_polynomials):
            for j in range(num_variables):
                jac[i,j] = polynomials[i].diff(variables[j])
        
        return jac,polynomials,variables
    
    def matmul(self, other):
        """
        x.matmul(y) <==> y*x
        
        (overriding __rmul__ gives strange behavior with spmatrix)
        """
        polys = self._polynomials
        res_polys = list(other * self._polynomials)
        res = PolynomialSystem(res_polys)
            
        return res
    
    def rank(self, tol=TOL):
        """
        Return a numeric value, the rank of the Jacobian at
        a 'generic' point.
        """
        from random import random as rand
        polynomials = self._polynomials
        parameters = list(self._parameters)
        variables = list(self._variables)
        if parameters:
            allvars = variables + parameters
        else:
            allvars = variables
        
        varsubs = zeros(len(allvars), 1)
        # compute sufficiently generic complex points
        for i in range(len(varsubs)):
            # rand()/rand() can vary magnitude satisfactorily
            try:
                real = rand()/rand()
                imag = rand()/rand()
            except ZeroDivisionError:
                # try again
                return self.rank()
            varsubs[i] = real + I*imag
            
        jac = self.jacobian()[0]
        jac = jac.subs(zip(allvars, varsubs))
        
        # allow user to specify tolerance (what is 'zero')
        iszero = lambda x, tol=tol: True if abs(x) < tol else False
        return jac.rank(iszero)
    
    def solve(self, start_params=None, final_params=None, start=None, usebertini=True):
        """
        Solve the system. If non-square, return the NID
        
        If the system has parameters and you don't supply
        final parameters, solve the system with random
        start parameters, return the solutions and the start parameters.
        If you do supply final parameters, solve the system with 
        random start parameters, then solve again and return the
        start parameters
        """
        rank = self.rank()
        polynomials = self._polynomials
        variables   = self._variables
        parameters  = self._parameters
        
        if usebertini:
            from tempfile import mkdtemp
            from naglib import TEMPDIR as basedir
            from naglib.bertini.sysutils import call_bertini
            from naglib.bertini.fileutils import write_input, read_points, fprint
            from naglib.bertini.data import compute_NID
            
            if rank != len(polynomials) or rank != len(variables):
                return compute_NID(self)
            elif parameters and not start_params and not final_params:
                dirname  = mkdtemp(prefix=basedir)
                filename = dirname + '/input'
                config   = {'filename': filename,
                            'TrackType': 0,
                            'ParameterHomotopy':1}
                
                write_input(self, config)
                call_bertini(filename)
                points = read_points(dirname + '/finite_solutions', as_set=False)
                sp = read_points(dirname + '/start_parameters', as_set=False)
                
                return points, sp
            elif parameters and not start_params:
                dirname  = mkdtemp(prefix=basedir)
                filename = dirname + '/input'
                config   = {'filename': filename,
                            'TrackType': 0,
                            'ParameterHomotopy':1}
                write_input(self, config)
                
                call_bertini(filename)
                
                start_params = read_points(dirname + '/start_parameters', as_set=False)
                
                config   = {'filename': filename,
                            'TrackType': 0,
                            'ParameterHomotopy':2}
                write_input(self, config)
                
                fprint(final_params, dirname + '/final_parameters')
                
                call_bertini(filename)
                
                points = read_points(dirname + '/finite_solutions', as_set=False)
                return points, start_params
            elif parameters and not final_params:
                return self.subs(zip(parameters, start_params)).solve()
            elif parameters and not start:
                raise(BertiniError("'start' does not exist!!!"))
            elif parameters: # and start_params and final_params
                dirname  = mkdtemp(prefix=basedir)
                filename = dirname + '/input'
                config   = {'filename': filename,
                            'TrackType': 0,
                            'ParameterHomotopy':2}
                
                fprint(start, dirname + '/start')
                fprint(start_params, dirname + '/start_parameters')
                fprint(final_params, dirname + '/final_parameters')

                write_input(self, config)
                call_bertini(filename)
                points = read_points(dirname + '/finite_solutions', as_set=False)
                
                return points
            else:
                dirname  = mkdtemp(prefix=basedir)
                filename = dirname + '/input'
                config   = {'filename': filename,
                            'TrackType': 0}
                
                write_input(self, config)
                call_bertini(filename)
                points = read_points(dirname + '/finite_solutions', as_set=False)
                
                return points
        else:
            msg = "nothing to use yet but Bertini"
            raise NotImplementedError(msg)
        
    def subs(self, *args, **kwargs):
        """
        Return a new PolynomialSystem with subs applied to
        each entry of 'polynomials'
        
        caution against using subs:
            this will destroy any parameter/homvar information in the system
        """
        polynomials = self._polynomials
        psubs = polynomials.subs(*args, **kwargs)
        ps = PolynomialSystem(psubs)
        
        return ps
        
    @property
    def polynomials(self):
        return self._polynomials
    @property
    def variables(self):
        return self._variables
    @property
    def parameters(self):
        return self._parameters
    @property
    def homvar(self):
        # TODO: change this for multihomogeneous systems
        if self._homvar:
            return self._homvar[0]
        else:
            return self._homvar
    @homvar.setter
    def homvar(self, h):
        if h is None:
            self._homvar = spmatrix()
            return
        h = sympify(h)
        if h not in self._variables:
            msg = "homogenizing variable {0} not found in list of variables".format(h)
            raise ValueError(msg)
        
        parameters = self._parameters
        polynomials = self._polynomials
        paramsubs = zip(parameters, [1 for p in parameters])
        for poly in polynomials:
            p = poly.subs(paramsubs)
            if p.is_number:
                deg = 0
            else:
                deg = p.as_poly().total_degree()
            # now check if polynomial is homogeneous
            terms = p.as_ordered_terms()
            for t in terms:
                if t.is_number and deg != 0:
                    msg = "polynomial {0} is not homogeneous".format(p)
                    raise NonHomogeneousException(msg)
                elif t.is_number:
                    pass
                elif t.as_poly().total_degree() != deg:
                    msg = "polynomial {0} is not homogeneous".format(p)
                    raise NonHomogeneousException(msg)
        
        if h in self._variables:
            self._homvar = spmatrix([h])
    @property
    def degree(self):
        return self._degree
    @property
    def shape(self):
        m = len(self._polynomials)
        n = len(self._variables)
        return (m,n)
    
class LinearSlice(NAGobject):
    """
    A linear system
    
    !!!Use this only for slicing!!!
    """
    def __init__(self, coeffs, variables, homvar=None):
        self._coeffs = spmatrix(coeffs)
        self._variables = spmatrix(variables)
        if homvar:
            homvar = sympify(homvar)
            if homvar not in variables:
                msg = "homogenizing variable {0} not in variables".format(homvar)
                raise ValueError(msg)
            else:
                self._homvar = homvar
        else:
            self._homvar = spmatrix()
        
        # do nothing; raise ShapeError if applicable
        mat = self._coeffs * self._variables
    
    def __repr__(self):
        """
        x.__repr__() <==> repr(x)
        """
        coeffs = self._coeffs
        variables = self._variables
        homvar = self._homvar
        repstr = 'LinearSlice({0},{1},{2})'.format(coeffs, variables, homvar)
        
        return repstr
        
    def __str__(self):
        """
        x.__str__() <==> str(x)
        """
        repstr = ''
        mat = self._coeffs * self._variables
        m = mat.shape[0]
        strmat = [str(row) for row in mat]
        maxlen = max([len(row) for row in strmat])
        for row in strmat:
            repstr += '[' + ' '*(maxlen-len(row)) + row + ']\n'
            
        return repstr
    
    def dehomogenize(self):
        """
        """
        homvar = self._homvar
        if not homvar:
            return self
        
        variables = list(self._variables)
        coeffs = self._coeffs.copy()
        
        dex = variables.index(homvar)
        variables.pop(dex)
        dehom_coeffs = coeffs.col(dex)
        coeffs.col_del(dex)
        m,n = coeffs.shape
        for i in range(m):
            coeffs[i,:] = coeffs[i,:]/dehom_coeffs[i]
            
        return LinearSlice(coeffs, variables)
            
    @property
    def codim(self):
        mat = self._coeffs
        m,n = mat.shape
        return n - m
    @property
    def coeffs(self):
        return self._coeffs
    @property
    def homvar(self):
        return self._homvar
    @property
    def mat(self):
        return self._coeffs * self._variables
    @property
    def rank(self, tol=TOL):
        iszero = lambda x, tol=tol: True if abs(x) < tol else False
        return self._coeffs.rank(iszerofunc=iszero)
    @property
    def shape(self):
        return self._coeffs.shape
    @property
    def variables(self):
        return self._variables