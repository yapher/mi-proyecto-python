import numpy as np

def rbf_kernel(r, eps=1.0, kind="gaussian"):
    if kind == "gaussian":
        return np.exp(-(r/eps)**2)
    elif kind == "multiquadric":
        return np.sqrt(1.0 + (r/eps)**2)
    elif kind == "thin_plate":
        out = r**2 * np.where(r > 0, np.log(r), 0.0)
        return out
    else:
        raise ValueError("Kernel no soportado")

class RBFRegressor:
    def __init__(self, eps=1.0, kind="gaussian", lam=0.0, affine=False):
        self.eps, self.kind, self.lam, self.affine = eps, kind, lam, affine

    def fit(self, X, y):
        X = np.asarray(X, float)
        y = np.asarray(y, float).ravel()
        N, d = X.shape
        D = np.linalg.norm(X[:,None,:] - X[None,:,:], axis=2)
        A = rbf_kernel(D, self.eps, self.kind)
        A.flat[::N+1] += self.lam

        if not self.affine:
            self.w = np.linalg.solve(A, y)
            self.X = X
            self.c = None
        else:
            P = np.hstack([X, np.ones((N,1))])
            Z = np.zeros((d+1, d+1))
            M = np.block([[A, P],[P.T, Z]])
            rhs = np.concatenate([y, np.zeros(d+1)])
            sol = np.linalg.solve(M, rhs)
            self.w = sol[:N]
            self.c = sol[N:]
            self.X = X
        return self

    def predict(self, Xnew):
        Xnew = np.asarray(Xnew, float)
        D = np.linalg.norm(Xnew[:,None,:] - self.X[None,:,:], axis=2)
        Phi = rbf_kernel(D, self.eps, self.kind)
        yhat = Phi.dot(self.w)
        if self.c is not None:
            a, b = self.c[:-1], self.c[-1]
            yhat = yhat + Xnew.dot(a) + b
        return yhat

    def get_model_equation(self):
        """
        Devuelve una representación matemática de la función RBF generada.
        """
        terms = []
        if self.c is not None:
            affine_terms = "+".join([f"{a:.3f}*x{i}" for i, a in enumerate(self.c[:-1])])
            affine_terms += f"+{self.c[-1]:.3f}"
        else:
            affine_terms = ""

        for i, xi in enumerate(self.X):
            term = f"{self.w[i]:.3f}*φ(||x-{xi.tolist()}||)"
            terms.append(term)

        if affine_terms:
            terms.append(affine_terms)

        equation = " + ".join(terms)
        return equation
