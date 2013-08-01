""" Solves the optimal control problem for the heat equation """
from dolfin import *
from dolfin_adjoint import *

# Setup 
mesh = Mesh("mesh.xml")
V = FunctionSpace(mesh, "CG", 1)
u = Function(V, name="State")
m = project(Constant(-5), V, name="Control")
v = TestFunction(V)

# Run the forward model once to create the simulation record 
F = (inner(grad(u), grad(v)) - m*v)*dx 
bc = DirichletBC(V, 0.0, "on_boundary")
solve(F == 0, u, bc)

# The functional of interest is the normed difference between desired
# and simulated temperature profile 
x = triangle.x
u_desired = exp(-1/(1-x[0]*x[0])-1/(1-x[1]*x[1]))
J = Functional((0.5*inner(u-u_desired, u-u_desired))*dx*dt[FINISH_TIME])

# Run the optimisation 
rf = ReducedFunctional(J, InitialConditionParameter(m, value=m))
ub = 0.5 
lb = interpolate(Constant(-1), V) # Test 2 different ways of imposing bounds

m_opt = minimize(rf, method="L-BFGS-B", in_euclidian_space=True,
                                  tol=2e-08, bounds=(lb, ub), options={"disp": True, "maxiter": 1})

assert min(m_opt.vector().array()) > lb((0, 0)) - 0.05 
assert max(m_opt.vector().array()) < ub + 0.05 
assert abs(rf(m_opt)) < 1e-3

info_green("Test passed")