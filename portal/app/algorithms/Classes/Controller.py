import numpy as np
import cvxpy as cvx


class Controller(object):

    def __init__(self, d_price, b_price, h_price, Qmin, Qmax, cmax, dmax, fmax, hmax, l_eff, c_eff, d_eff, coeff_f,
                 coeff_x, coeff_h, coeff_b, n_f, n_t, n_b, T, t_res=15. / 60):
        # coeffs are fan model coefficients
        # self.prices = prices entered when solving
        self.d_price = d_price
        self.b_price = b_price
        self.h_price = h_price  # cost of deviating above THI
        self.Qmin = Qmin
        self.Qmax = Qmax
        self.cmax = cmax
        self.dmax = dmax
        self.fmax = fmax
        self.hmax = hmax
        self.l_eff = l_eff
        self.c_eff = c_eff
        self.d_eff = d_eff
        self.t_res = t_res  # data time resolution in hours
        self.coeff_f = coeff_f
        self.coeff_x = coeff_x
        self.coeff_h = coeff_h
        self.coeff_b = coeff_b.flatten()
        self.n_f = n_f  # number of fans
        self.n_t = n_t  # number of temperature sensors
        self.n_b = n_b  # number of batteries
        self.T = T  # length of optimization horizon

    def fanPrediction(self, h0, f_exo):
        # f_exo are the fan exogenous inputs for the fan model, such as outdoor temperature
        # make fan prediction

        N, T = f_exo.shape
        h = np.zeros((self.n_t, T + 1))
        f_p = np.zeros((self.n_f, T))

        h[:, 0] = h0.flatten()

        for t in range(T):
            if np.max(h[:,t]) >= self.hmax:
                f_p[:, t] = self.fmax * np.ones(self.n_f)
            else:
                f_p[:, t] = np.zeros(self.n_f)

            h[:, t + 1] = np.dot(self.coeff_h, h[:, t]) + np.dot(self.coeff_x, f_exo[:, t]) \
                          + np.dot(self.coeff_f, f_p[:, t]) + self.coeff_b

        return f_p, h

    def fanPredictionSimple(self, f_on, time_curr, f_start=8*4, f_end=21*4):
        # f_on is binary indicating if the fans are currently on or not
        # time_curr is the number of 15 minute time steps past midnight it is now
        # default assume the fans start at 8am and end at 9pm

        f_p = np.zeros((self.n_f, self.T))
        if f_on and time_curr < f_end:
            # fan is currently running -> predict will run until end
            duration = f_end - time_curr
            fan = self.fmax * np.ones((self.n_f, duration))
            start = 0
        elif f_on and time_curr >= f_end:
            # fan is on after expected time -> fan will remain on one more period
            duration = 1
            fan = self.fmax * np.ones((self.n_f, duration))
            start = 0
        elif time_curr <= f_start:
            # no fan before start -> predict fan on at start until end
            duration = f_end - f_start
            fan = self.fmax * np.ones((self.n_f, duration))
            start = f_start - time_curr
        elif time_curr >= f_start and time_curr < f_end:
            # no fan after expected time -> predict fan will run next period
            duration = f_end - time_curr - 1
            fan = self.fmax * np.ones((self.n_f, duration))
            start = 1
        elif time_curr >= f_end:
            # no fan after end time -> fan will stay off until tomorrow
            start = self.T - time_curr + f_start
            duration = self.T - start
            if duration > f_end - f_start:
                duration = f_end - f_start
            fan = self.fmax * np.ones((self.n_f, duration))
            start = self.T - time_curr + f_start

        f_p[:, start:start + duration] = fan

        return f_p

    def optimize(self, power, solar, prices, Q0, Pmax0, f_p):
        # f_p is predicted fan power consumption
        n, T = power.shape

        cmax = np.tile(self.cmax, (self.n_b, T))
        dmax = np.tile(self.dmax, (self.n_b, T))
        Qmin = np.tile(self.Qmin, (self.n_b, T + 1))
        Qmax = np.tile(self.Qmax, (self.n_b, T + 1))
        #fmax = np.tile(self.fmax, (self.n_f, T))
        #hmax = np.tile(self.hmax, (self.n_t, T + 1))
        solar = np.tile(solar, (self.n_f, 1))

        # print(solar.shape)
        # print(solar)

        c = cvx.Variable((self.n_b, T))
        d = cvx.Variable((self.n_b, T))
        #f = cvx.Variable((self.n_f, T))
        Q = cvx.Variable((self.n_b, T + 1))
        #h = cvx.Variable((self.n_t, T + 1))

        # Battery, fan, THI, Constraints
        constraints = [c <= cmax,
                       c >= 0,
                       d <= dmax,
                       d >= 0,
                       #f >= 0,
                       #f <= fmax,
                       Q[:, 0] == Q0,
                       Q[:, 1:T + 1] == self.l_eff * Q[:, 0:T]
                       + self.c_eff * c * self.t_res - self.d_eff * d * self.t_res,
                       Q >= Qmin,
                       Q <= Qmax,
                       #h[:, 0] == h0.flatten()
                       ]

        # THI vs fan power model
        #for t in range(0, T):
        #    constraints.append(
        #        h[:, t + 1] == self.coeff_h * h[:, t] + np.dot(self.coeff_x, f_exo[:, t])
        #        + self.coeff_f * f[:, t] + self.coeff_b)

        # not a constraint, just a definition
        net = cvx.hstack([power.reshape((1, power.size)) + c - d
                          + cvx.reshape(cvx.sum(cvx.pos(f_p - solar), axis=0), (1, T)) - Pmax0, np.zeros((1, 1))])

        obj = cvx.Minimize(
            cvx.sum(cvx.multiply(prices, cvx.pos(power.reshape((1, power.size))
                                                 + c - d + cvx.reshape(cvx.sum(cvx.pos(f_p - solar), axis=0),
                                                                       (1, T)))))  # cost min
            + self.d_price * cvx.max(net)  # demand charge
            + self.b_price * cvx.sum(c + d)  # battery degradation
            # attempt to make battery charge at night * doesnt do anything
            # + 0.0001 * cvx.sum_squares((power.reshape((1, power.size))
            #                            + c - d + cvx.reshape(cvx.sum(cvx.pos(f_p - solar), axis=0), (1, T)))/np.max(power))
        #   + self.h_price * cvx.sum_squares(cvx.pos(h - hmax))  # THI penalty
        )

        prob = cvx.Problem(obj, constraints)

        prob.solve(solver=cvx.ECOS)

        # calculate expected max power
        net = power + c.value - d.value + np.sum(np.clip(f_p, 0, None), axis=0) - Pmax0
        Pmax_new = np.max(net) + Pmax0
        if Pmax_new < Pmax0:
            Pmax_new = Pmax0

        return c.value, d.value, Q.value, prob.status, Pmax_new

