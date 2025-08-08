import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from gcft_background import gcft_background, y0_gcft, t_span, t_eval, lambda_, Xi0, rho_m0

# ---- Parameters ----
k_mode = 0.1

# ---- Background Integration ----
sol_bg = solve_ivp(gcft_background, t_span, y0_gcft, t_eval=t_eval, method='RK45')
t_arr = sol_bg.t
a_arr = sol_bg.y[2]
Xi_arr = sol_bg.y[0]
Xi_dot_arr = sol_bg.y[1]

H_arr = np.gradient(np.log(a_arr), t_arr)
Vp_arr = lambda_ * (Xi_arr - Xi0)**3
Vpp_arr = lambda_ * 3 * (Xi_arr - Xi0)**2
rho_m_arr = rho_m0 / a_arr**3

# ---- Perturbation System ----
def coupled_scalar_metric(t, y):
    delta_m, delta_m_dot, delta_Xi, delta_Xi_dot, Phi = y

    H = np.interp(t, t_arr, H_arr)
    a = np.interp(t, t_arr, a_arr)
    Xi = np.interp(t, t_arr, Xi_arr)
    Xi_dot = np.interp(t, t_arr, Xi_dot_arr)
    Vp = np.interp(t, t_arr, Vp_arr)
    Vpp = np.interp(t, t_arr, Vpp_arr)
    rho_m = np.interp(t, t_arr, rho_m_arr)

    # Constraint from Poisson-like equation
    Phi_dot = 0  # Simplified: not dynamically evolved, just static Phi (fix later with better gauge)
    Phi_rhs = 4 * np.pi * (rho_m * delta_m + Xi_dot * delta_Xi_dot - Xi_dot**2 * Phi + Vp * delta_Xi)
    Phi_new = Phi_rhs / (k_mode**2 / a**2 + 1e-12)  # avoid division by zero

    delta_m_ddot = -2 * H * delta_m_dot + 4 * np.pi * rho_m * delta_m + k_mode**2 * Phi / a**2
    delta_Xi_ddot = -3 * H * delta_Xi_dot - (k_mode**2 / a**2 + Vpp) * delta_Xi + 4 * Xi_dot * Phi_dot - 2 * Vp * Phi

    return [delta_m_dot, delta_m_ddot, delta_Xi_dot, delta_Xi_ddot, 0]  # Phi static

# ---- Initial Conditions ----
delta_m0 = 1e-5
delta_m_dot0 = 0.0
delta_Xi0 = 1e-6
delta_Xi_dot0 = 0.0
Phi0 = 1e-6
y0_pert = [delta_m0, delta_m_dot0, delta_Xi0, delta_Xi_dot0, Phi0]

sol = solve_ivp(coupled_scalar_metric, (t_arr[0], t_arr[-1]), y0_pert, t_eval=t_arr, method='RK45')

# ---- Plotting ----
plt.figure(figsize=(9,5))
plt.plot(a_arr, sol.y[0] / delta_m0, label='Matter $\delta_m(a)/\delta_{m0}$')
plt.plot(a_arr, sol.y[2] / delta_Xi0, '--', label='Scalar $\delta\Xi(a)/\delta\Xi_0$')
plt.xlabel('Scale factor a')
plt.ylabel('Normalized Perturbation')
plt.xscale('log')
plt.legend()
plt.grid()
plt.title('Scalar + Matter Perturbations (GCFT Metric Coupled)')
plt.tight_layout()
plt.savefig('../results/plots/gcft_scalar_metric_coupled.png')
plt.show()
