"""Pure-Python planar FK/Jacobian and damped least-squares IK teaching checks."""
from math import sin, cos, sqrt


def fk(q, lengths=(1.0, 0.8)):
    a, b = q
    l1, l2 = lengths
    return (l1*cos(a)+l2*cos(a+b), l1*sin(a)+l2*sin(a+b))


def jacobian(q, lengths=(1.0, 0.8)):
    a, b = q
    l1, l2 = lengths
    return ((-l1*sin(a)-l2*sin(a+b), -l2*sin(a+b)),
            (l1*cos(a)+l2*cos(a+b), l2*cos(a+b)))


def ik(target, q=(0.3, 0.8), damping=0.05, tolerance=1e-6):
    if sqrt(target[0]**2 + target[1]**2) > 1.8:
        return q, False
    q = list(q)
    for _ in range(300):
        p = fk(q)
        e = (target[0]-p[0], target[1]-p[1])
        if sqrt(e[0]**2+e[1]**2) < tolerance:
            return tuple(q), True
        j = jacobian(q)
        # dq = J.T @ inverse(J @ J.T + damping^2 I) @ error
        a = sum(v*v for v in j[0]) + damping*damping
        b = sum(j[0][i]*j[1][i] for i in range(2))
        d = sum(v*v for v in j[1]) + damping*damping
        det = a*d-b*b
        v = ((d*e[0]-b*e[1])/det, (-b*e[0]+a*e[1])/det)
        dq = [j[0][i]*v[0]+j[1][i]*v[1] for i in range(2)]
        q = [q[i]+max(-0.15,min(0.15,dq[i])) for i in range(2)]
    return tuple(q), False


if __name__ == '__main__':
    q, eps = (0.5, 0.9), 1e-6
    j = jacobian(q)
    largest_error = 0.0
    for column in range(2):
        plus, minus = list(q), list(q)
        plus[column] += eps; minus[column] -= eps
        fd = [(fk(plus)[r]-fk(minus)[r])/(2*eps) for r in range(2)]
        largest_error = max(largest_error, *(abs(fd[r]-j[r][column]) for r in range(2)))
    target = (1.2, 0.5)
    solution, success = ik(target)
    assert largest_error < 1e-8
    assert success and not ik((2.0, 0.0))[1]
    print('Jacobian finite-difference error:', largest_error)
    print('IK target:', target, 'achieved:', fk(solution), 'joint angles:', solution)
    print('All teaching checks passed. This example does not command a physical robot.')
