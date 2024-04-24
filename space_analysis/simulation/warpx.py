# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/simulation/warpx.ipynb.

# %% auto 0
__all__ = ['constants', 'CustomSimulation', 'log_sim_info', 'HybridSimulation', 'log_info']

# %% ../../nbs/simulation/warpx.ipynb 1
#| default_exp simulation/warpx
#| export

# %% ../../nbs/simulation/warpx.ipynb 2
import numpy as np
from pydantic import BaseModel, ConfigDict
import json
from typing import Literal

from pywarpx.picmi import Simulation
from pywarpx import picmi

# %% ../../nbs/simulation/warpx.ipynb 3
constants = picmi.constants

# %% ../../nbs/simulation/warpx.ipynb 4
class CustomSimulation(BaseModel):

    dim: int = None
    diag: bool = True
    test: bool = True #: Test mode for quick simulation (with reduced ion mass)

    # Plasma parameters
    n0: float = None
    """plasma density (m^-3)"""

    # Plasma species parameters
    m_ion_norm: float = 400
    """Ion mass (electron masses)"""
    m_ion: float = None
    """Ion mass (kg)"""
    v_ti: float = None
    """Ion thermal velocity (m/s)"""

    # Spatial domain
    nz: int = None  #: number of cells in z direction
    nx: int = None  #: number of cells in x (and y) direction

    # Numerical parameters
    nppc: int = 64
    """Seed number of particles per cell"""
    dt_norm: float = 1 / 256
    """Time step normalized to period like ion cyclotron period"""

    diag_time_norm: float = (
        1  #: Time interval at which to output diagnostic (like ion cyclotron periods)
    )
    diag_steps: int = (
        None  #: The simulation step interval at which to output diagnostic
    )
    diag_part: bool = False  #: Output particle diagnostic
    diag_field: bool = True  #: Output field diagnostic
    diag_format: Literal["plotfile", "openpmd"] = (
        "openpmd"  #: Output format for diagnostics
    )
    diag_openpmd_backend: Literal["h5", "bp", "json"] = (
        "h5"  #: OpenPMD backend for diagnostics
    )
    # NOTE: `yt` project currently does only support `h5` backend for openPMD
    grid_kwargs: dict = dict()  #: Additional grid parameters

    _sim: Simulation = None
    _dist: picmi.AnalyticDistribution = None
    _B_ext: picmi.AnalyticInitialField = None

    model_config = ConfigDict(
        extra="allow",
    )

    def setup_init_cond(self):
        """setup initial conditions"""
        return self

    def setup_particle(self):
        """setup the particle"""
        if self._dist is not None:
            ions = picmi.Species(
                name="ions",
                charge_state=1,
                mass=self.m_ion,
                initial_distribution=self._dist,
            )

            layout = picmi.PseudoRandomLayout(
                grid=self._grid, n_macroparticles_per_cell=self.nppc
            )

            self._sim.add_species(ions, layout)

        return self

    def setup_grid(self):
        """Setup geometry and boundary conditions"""
        if self.dim == 1:
            grid_object = picmi.Cartesian1DGrid
        elif self.dim == 2:
            grid_object = picmi.Cartesian2DGrid
        else:
            grid_object = picmi.Cartesian3DGrid

        number_of_cells = [self.nx, self.nx, self.nz][-self.dim :]
        boundary_conditions = ["periodic"] * self.dim

        self._grid = grid_object(
            number_of_cells=number_of_cells,
            lower_bound=[-self.Lx / 2.0, -self.Lx / 2.0, 0][-self.dim :],
            upper_bound=[self.Lx / 2.0, self.Lx / 2.0, self.Lz][-self.dim :],
            lower_boundary_conditions=boundary_conditions,
            upper_boundary_conditions=boundary_conditions,
            **self.grid_kwargs,
        )
        return self

    def setup_field(self):
        """Setup external field"""
        if self._B_ext is not None:
            self._sim.add_applied_field(self._B_ext)
        return self

    def setup_field_solver(self):
        return self

    def setup_diag(self):
        """Setup diagnostic components."""
        self.diag_steps = int(self.diag_time_norm / self.dt_norm)
        if self.diag_field:
            field_diag = picmi.FieldDiagnostic(
                grid=self._grid,
                period=self.diag_steps,
                warpx_format=self.diag_format,
                warpx_openpmd_backend=self.diag_openpmd_backend,
            )
            self._sim.add_diagnostic(field_diag)
        if self.diag_part:
            part_diag = picmi.ParticleDiagnostic(
                period=self.diag_steps,
                warpx_format=self.diag_format,
                warpx_openpmd_backend=self.diag_openpmd_backend,
            )
            self._sim.add_diagnostic(part_diag)
        
        part_energy_diag = picmi.ReducedDiagnostic(
            name = "part_energy",
            diag_type = "ParticleEnergy", period=self.diag_steps
        )
        field_energy_diag = picmi.ReducedDiagnostic(
            name = "field_energy",
            diag_type = "FieldEnergy", period=self.diag_steps
        )
        
        self._sim.add_diagnostic(part_energy_diag)
        self._sim.add_diagnostic(field_energy_diag)
        
        return self

    def setup_run(self):
        """Setup simulation components."""
        self.setup_init_cond()
        self.setup_grid().setup_field_solver().setup_field()
        self.setup_particle()
        if self.diag:
            self.setup_diag()
        self.dump()
        self._sim.write_input_file()

    def dump(self, file="sim_parameters.json"):
        d = dict(self.model_dump())
        with open(file, "w") as f:
            json.dump(d, f)

    def model_post_init(self, __context):
        if self.test:
            # self.m_ion_norm = 100
            pass
             
        if self.m_ion is None:
            self.m_ion = self.m_ion_norm * constants.m_e

        self._sim = Simulation(
            warpx_serialize_initial_conditions=True,
        )
        return self

# %% ../../nbs/simulation/warpx.ipynb 5
def log_sim_info(sim: Simulation):
    """print out plasma parameters and numerical parameters."""
    print(
        f"Numerical parameters:\n"
        f"\tdt = {sim.time_step_size:.1e} s\n"
        f"\ttotal steps = {sim.max_steps:d}\n"
    )

# %% ../../nbs/simulation/warpx.ipynb 7
class HybridSimulation(CustomSimulation):

    beta: float = 0.1
    """Plasma beta"""  # used to calculate temperature

    B0: float = 100 * 1e-9
    """Initial magnetic field strength (T)"""

    vA: float = None
    """Alfven speed"""
    vA_over_c: float = None  #: ratio of Alfven speed and the speed of light

    # Hybrid solver parameters
    ## TODO: find a good value
    n_floor_coef: float = 0.015625   
    plasma_resistivity: float = 1e-6 #: Plasma resistivity
    plasma_hyper_resistivity: float = 1e-6 #: Plasma hyper-resistivity (to suppress spurious whistler noise in low density regions)
    substeps: int = 10  #: the number of sub-steps to take during the B-field update.

    T_plasma: float = None
    Te: float = None #: Electron temperature in (eV)

    t_ci: float = None
    """Ion cyclotron period (s)"""
    d_i: float = None
    """Ion inertial length (m)"""

    # Numerical parameters
    time_norm: float = 100.0
    """Simulation temporal length (ion cyclotron periods)"""

    Lz_norm: float = None
    Lx_norm: float = 0
    """Spatial domain length (ion skin depths)"""
    dz_norm: float = 1 / 4
    """Cell size (ion skin depths)"""

    def get_plasma_quantities(self):
        """Calculate various plasma parameters based on the simulation input."""
        # Cyclotron angular frequency (rad/s) and period (s)
        self.w_ci = constants.q_e * abs(self.B0) / self.m_ion
        self.t_ci = 2.0 * np.pi / self.w_ci

        # Alfven speed (m/s): vA = B / sqrt(mu0 * n * (M + m)) = c * omega_ci / w_pi
        if self.n0 is not None:
            self.vA = self.B0 / np.sqrt(
                constants.mu0 * self.n0 * (self.m_ion + constants.m_e)
            )
            self.vA_over_c = self.vA / constants.c
        elif self.vA_over_c is not None:
            self.vA = self.vA_over_c * constants.c
            self.n0 = (self.B0 / self.vA) ** 2 / (
                constants.mu0 * (self.m_ion + constants.m_e)
            )

        # Ion plasma frequency (rad/s)
        self.w_pi = np.sqrt(constants.q_e**2 * self.n0 / (self.m_ion * constants.ep0))

        # Skin depth (m): inertial length
        self.d_i = constants.c / self.w_pi

        # Ion thermal velocity (m/s) from beta = 2 * (v_ti / vA)**2
        self.v_ti = np.sqrt(self.beta / 2.0) * self.vA

        # Temperature (eV) from thermal speed: v_ti = sqrt(kT / M)
        self.T_plasma = self.v_ti**2 * self.m_ion / constants.q_e  # eV
        self.Te = self.T_plasma

        return self

    def model_post_init(self, __context):
        """This function is called after the object is initialized"""

        super().model_post_init(__context)

        self.get_plasma_quantities()

        self.dt = self.dt_norm * self.t_ci
        self.dz = self.dz_norm * self.d_i

        if self.nz is None:
            self.nz = int(self.Lz_norm / self.dz_norm)
        else:
            self.Lz_norm = self.nz * self.dz_norm

        if self.dim >= 2:
            if self.nx is None:
                self.nx = int(self.Lx_norm / self.dz_norm)
            else:
                self.Lx_norm = self.nx * self.dz_norm

        self.Lz = self.Lz_norm * self.d_i
        self.Lx = self.Lx_norm * self.d_i

        self._sim.max_steps = int(self.time_norm / self.dt_norm)
        self._sim.time_step_size = self.dt

        log_info(self)
        self.check_cfl()
        self.setup_run()

    def setup_run(self):
        self._sim.current_deposition_algo = "direct"
        self._sim.particle_shape = 1
        super().setup_run()

    def setup_field_solver(self):
        """Setup field solver"""

        self._sim.solver = picmi.HybridPICSolver(
            grid=self._grid,
            Te=self.Te,
            n0=self.n0,
            n_floor=self.n_floor_coef * self.n0,
            plasma_resistivity=self.plasma_resistivity,
            plasma_hyper_resistivity=self.plasma_hyper_resistivity,
            substeps=self.substeps,
        )
        return self

    @property
    def cfl_b(self):
        """Courant-Friedrichs-Lewy condition"""
        const = 2 * (np.pi) ** 2
        cfl = const * self.dt_norm / (self.dz_norm) ** 2
        return cfl / self.substeps

    def check_cfl(self):
        """Check the Courant-Friedrichs-Lewy condition"""

        if self.cfl_b > 1:
            print(
                f"CFL (with substep) condition violated: {self.cfl_b:.2f}, Substeps: {self.substeps}"
            )
            return False

# %% ../../nbs/simulation/warpx.ipynb 8
def log_info(sim: HybridSimulation):
    """print out plasma parameters and numerical parameters."""
    log_sim_info(sim._sim)
    
    print(
        f"Numerical parameters (Hybrid):\n"
        f"\ttotal simulation time = {sim.time_norm:.1f} (t_ci)\n"
        f"\ttime step = {sim.dt_norm} (t_ci)\n"
        f"\tCFL (with substeps) condition = {sim.cfl_b:.2f}\n"
    )    

    print(
        f"Initializing simulation with input parameters:\n"
        f"\tTe = {sim.Te:.3f} eV\n"
        f"\tn = {sim.n0/1e6:.1e} cm^-3\n"
        f"\tB0 = {sim.B0/1e-9:.2f} nT\n"
        f"\tM/m = {sim.m_ion_norm:.0f}\n"
    )
    print(
        f"Plasma parameters:\n"
        f"\td_i = {sim.d_i:.1e} m\n"
        f"\tt_ci = {sim.t_ci:.1e} s\n"
        f"\tv_ti = {sim.v_ti:.1e} m/s\n"
        f"\tvA = {sim.vA:.1e} m/s\n"
        f"\tvA/c = {sim.vA/constants.c}\n"
    )
