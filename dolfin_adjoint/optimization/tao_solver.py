from dolfin import as_backend_type
from dolfin_adjoint.controls import FunctionControl, ConstantControl
from optimization_solver import OptimizationSolver
import numpy as np

from backend import *

class TAOSolver(OptimizationSolver):
    """Uses PETSc TAO to solve the given optimization problem.
       http://www.mcs.anl.gov/research/projects/tao/

       Valid methods:
         ------ Unconstrained optimisation --------
         nm:    Nelder-Mead method
         lmvm:  Limited memory, variable metric method
         nls:   Newton line-search method
         cg:    Nonlinear conjugate gradient mehtod

         ------ Bound constrained optimisation --------
         ntr:   Newton trust-region method (supports bound constraints)
         bqpib: Interior point Newton algorithm
         blmvm: Limited memory, variable metric method with bound constraints

    """

    def __init__(self, problem, parameters=None, riesz_map=None):

        try:
            from petsc4py import PETSc
        except:
            raise Exception, "Could not find petsc4py. Please install it."
        try:
            TAO = PETSc.TAO
        except:
            raise Exception, "Your petsc4py version does not support TAO. Please upgrade to petsc4py >= 3.5."

        self.PETSc = PETSc

        # Use PETSc forms
        if riesz_map is not None:
            self.riesz_map = as_backend_type(riesz_map).mat()
        else:
            self.riesz_map = None

        OptimizationSolver.__init__(self, problem, parameters)

        self.tao_problem = PETSc.TAO().create(PETSc.COMM_WORLD)

        self.__build_app_context()
        self.__set_parameters()
        self.__build_tao_problem()

    def __build_app_context(self):
        PETSc = self.PETSc
        rf = self.problem.reduced_functional

        # Map each control to a PETSc Vec...
        ctrl_vecs = []
        for control in rf.controls:
            as_vec = self.__control_as_vec(control)
            ctrl_vecs.append(as_vec)

        # ...then concatenate
        ctrl_vec = self.__petsc_vec_concatenate(ctrl_vecs)

        # Use value of control object as initial guess for the optimisation
        self.initial_vec = ctrl_vec.copy()
        #self.initial_vec = ctrl_vec.duplicate() # DSM temporary to reproduce dependency results

        class AppCtx(object):
            ''' Implements the application context for the TAO solver '''

            def __init__(self):
                # create Hessian matrix
                self.H = PETSc.Mat().create(comm=PETSc.COMM_WORLD)
                dims = (ctrl_vec.local_size, ctrl_vec.size)
                self.H.createPython((dims,dims), comm=PETSc.COMM_WORLD)
                self.H.setPythonContext(self)
                self.H.setOption(PETSc.Mat.Option.SYMMETRIC, True)
                self.H.setUp()

            def objective(self, x):
                ''' Evaluates the functional. '''
                self.update(x)
                # TODO: Multiple controls
                return rf(rf.controls[0].data())

            def objective_and_gradient(self, tao, x, G):
                ''' Evaluates the functional and gradient for the parameter choice x. '''
                j = self.objective(x)
                # TODO: Concatenated gradient vector
                gradient = rf.derivative(forget=False)[0]
                gradient_vec = as_backend_type(gradient.vector()).vec()

                G.set(0)
                G.axpy(1, gradient_vec)
                return j

            def hessian(self, tao, x, H, HP):
                ''' Updates the Hessian. '''
                print "Updating Hessian: %s" % self.stats(x)

                diff = x.copy()
                diff.axpy(-1.0, ctrl_vec)
                diffnorm = diff.norm()

                if diffnorm > 0.0:
                    info_red("Warning: rerunning rf")
                    self.objective(x)

            def stats(self, x):
                return "(min, max): (%s, %s)" % (x.min()[-1], x.max()[-1])

            def mult(self, mat, x, y):
                # TODO: Add multiple control support to Hessian stack and check for ConstantControl
                x_wrap = Function(rf.controls[0].data().function_space(), PETScVector(x))
                hes = rf.hessian(x_wrap)[0]
                hes_vec = as_backend_type(hes.vector()).vec()

                y.set(0)
                y.axpy(1, hes_vec)

            def update(self, x):
                ''' Split input vector and update all control values '''
                x.copy(ctrl_vec) # Refresh concatenated control vector first

                nvec = 0
                for i in range(0,len(rf.controls)):
                    control = rf.controls[i]

                    if isinstance(control, FunctionControl):
                        data_vec = as_backend_type(control.data().vector()).vec()

                        # Map appropriate range of input vector to control
                        ostarti, oendi = data_vec.owner_range
                        rstarti = ostarti + nvec
                        rendi = rstarti + data_vec.local_size
                        data_vec.setValues(range(ostarti, oendi), x[rstarti:rendi])
                        data_vec.assemble()
                        nvec += data_vec.size

                    elif isinstance(control, ConstantControl):
                        # Scalar case
                        if control.data().shape() == ():
                            vsize = 1
                            val = float(x[nvec])

                        # Vector case
                        elif len(control.data().shape()) == 1:
                            vsize = control.data().shape()[0]
                            val = x[nvec:nvec+vsize]

                        # Matrix case
                        else:
                            vsizex, vsizey = control.data().shape()
                            vsize = vsizex*vsizey
                            as_array = x[nvec:nvec+vsize]

                            # Sort into matrix restoring rows and columns
                            val = []
                            for row in range(0,vsizex):
                                val_inner = []

                                for column in range(0,vsizey):
                                    val_inner.append(as_array[row*vsizey + column])

                                val.append(val_inner)

                        # Replace control in rf
                        cons = Constant(val) # Loss of information? No coeff in init
                        rf.controls[i] = ConstantControl(cons)
                        nvec += vsize

        # create user application context
        self.__user = AppCtx()

    def __set_parameters(self):
        """Set some basic parameters from the parameters dictionary that the user
        passed in, if any."""

        OptDB = self.PETSc.Options(prefix="tao_")

        if self.parameters is not None:
            for param in self.parameters:

                # Support alternate parameter names
                if param == "method":
                    self.parameters["type"] = self.parameters.pop(param)
                    param = "type"

                elif param == "maximum_iterations" or param == "max_iter":
                    self.parameters["max_it"] = self.parameters.pop(param)
                    param = "max_it"

                # Unlike IPOPT and Optizelle solver, this doesn't raise ValueError on unknown option.
                # Presented as a "WARNING!" message following solve attempt.
                OptDB.setValue(param,self.parameters[param])

    def __build_tao_problem(self):
        self.tao_problem.setFromOptions()

        self.tao_problem.setObjectiveGradient(self.__user.objective_and_gradient)
        self.tao_problem.setInitial(self.initial_vec)
        self.tao_problem.setRieszMap(self.riesz_map)
        self.tao_problem.setHessian(self.__user.hessian, self.__user.H)

        # Set bounds if we have any
        if self.problem.bounds is not None:
            (lb, ub) = self.__get_bounds()
            self.tao_problem.setVariableBounds(lb, ub)

        # Similarly for constraints TODO
        if self.problem.constraints is not None:
            eval_fn = self.__get_constraints()

    def __get_bounds(self):
        """Convert bounds to PETSc vectors - TAO's accepted format"""
        bounds = self.problem.bounds
        controls = self.problem.reduced_functional.controls

        lbvecs = []
        ubvecs = []

        for (bound, control) in zip(bounds, controls):

            len_control = self.__control_as_vec(control).size
            (lb,ub) = bound # could be float, int, Constant, or Function

            if isinstance(lb, Function):
                lbvec = as_backend_type(lb.vector()).vec()
            elif isinstance(lb, (float, int, Constant)):
                lbvec = self.initial_vec.duplicate()
                lbvec.set(float(lb))
            else:
                raise TypeError("Unknown lower bound type %s" % lb.__class__)
            lbvecs.append(lbvec)

            if isinstance(ub, Function):
                ubvec = as_backend_type(ub.vector()).vec()
            elif isinstance(ub, (float, int, Constant)):
                ubvec = self.initial_vec.duplicate()
                ubvec.set(float(ub))
            else:
                raise TypeError("Unknown upper bound type %s" % ub.__class__)
            ubvecs.append(ubvec)

        lbvec = self.__petsc_vec_concatenate(lbvecs)
        ubvec = self.__petsc_vec_concatenate(ubvecs)
        return (lbvec, ubvec)

    def __get_constraints(self):
        # TODO: Implement constraints handling
        return None

    def __petsc_vec_concatenate(self, vecs):
        """Concatenates the supplied list of PETSc Vecs."""
        PETSc = self.PETSc

        # Make a Vec with appropriate local/global sizes and copy in each rank's local entries
        lsizes = [vec.sizes for vec in vecs]
        nlocal, nglobal = map(sum, zip(*lsizes))

        concat_vec = PETSc.Vec().create(PETSc.COMM_WORLD)
        concat_vec.setSizes((nlocal,nglobal))
        concat_vec.setFromOptions()
        nvec = 0
        for vec in vecs:

            # Local range indices
            ostarti, oendi = vec.owner_range
            rstarti = ostarti + nvec
            rendi = rstarti + vec.local_size

            concat_vec.setValues(range(rstarti,rendi), vec[ostarti:oendi])
            concat_vec.assemble()
            nvec += vec.size

        return concat_vec

    def __constant_as_vec(self, cons):
        """Return a PETSc Vec representing the supplied Constant"""
        PETSc = self.PETSc
        cvec = PETSc.Vec().create(PETSc.COMM_WORLD)

        # Scalar case e.g. Constant(0.1)
        if cons.shape() == ():
            cvec.setSizes((PETSc.DECIDE,1))
            cvec.setFromOptions()
            cvec.set(float(cons))

        else:

            # Vector case e.g. Constant((0.1,0.1))
            if len(cons.shape()) == 1:
                vec_length = cons.shape()[0]

            # Matrix case e.g. Constant(((1,2),(3,4)))
            else:
                vec_length = cons.shape()[0] * cons.shape()[1]

            cvec.setSizes((PETSc.DECIDE,vec_length))
            cvec.setFromOptions()

            # Can't iterate over vector calling float on each entry
            # Instead evaluate with Numpy arrays of appropriate length
            # See FEniCS Q&A #592
            vals = np.zeros(vec_length)
            cons.eval(vals, np.zeros(vec_length))

            ostarti, oendi = cvec.owner_range
            for i in range(ostarti, oendi):
                cvec.setValue(i,vals[i])

        cvec.assemble()
        return cvec

    def __control_as_vec(self, control):
        """Return a PETSc Vec representing the supplied Control"""
        if isinstance(control, FunctionControl):
            as_vec = as_backend_type(Function(control.data()).vector()).vec()
        elif isinstance(control, ConstantControl):
            as_vec = self.__constant_as_vec(Constant(control.data()))
        else:
            raise TypeError("Unknown control type %s" % control.__class__)
        return as_vec

    def get_tao(self):
        """Returns the PETSc TAO instance associated with the solver"""
        return self.tao_problem

    def solve(self):
        self.tao_problem.solve()
        sol_vec = self.tao_problem.getSolution()
        self.__user.update(sol_vec)

        # TODO: Multiple controls support
        return self.problem.reduced_functional.controls[0].data()