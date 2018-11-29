""" This file contains the physical settings"""

"""Electrochemistry Settings"""
# volumetric exchange current density of the cathode[A/m^3]
exchange_current_density_cathode = 2.3e3
# volumetric exchange current density of the anode [A/m^3]
exchange_current_density_anode = 0.817e9
# oxygen catalyst layer diffusion coefficient [m^2/s]
oxygen_catalyst_layer_diffusion_coefficient = 1.36e-8
# hydrogen catalyst layer diffusion coefficient [m^2/s]
hydrogen_catalyst_layer_diffusion_coefficient = 1.36e-8
# oxygen gas diffusion layer diffusion coefficient [[m^2/s]
oygen_gas_diffusion_layer_diffusion_coefficient = 2.59e-6
# hydrogen gas diffusion layer diffusion coefficient [m^2/s]
hydrogen_diffusion_layer_diffusion_coefficient = 2.59e-6
# catalyst layer proton conductivity of the cathode [Ohm^-1/m]
catalyst_layer_proton_conductivity_cathode = 3.e0
# catalyst layer proton conductivity of the anode [Ohm^-1/m]
catalyst_layer_proton_conductivity_anode = 3.e0
# tafel slope of the cathode [V]
tafel_slope_cathode = 0.03
# tafel slope of the anode [V]
tafel_slope_anode = 0.03
# thermo neutral open circuit voltage [V]
v_thermo_neutral = 1.28
# molar concentration of membrane acid groups [mol/m^3]
molar_membrane_acid_group_concentration = 1.2e3


"""Electric Settings"""
# membrane basic resistance [Ohm/m^2]
membrane_basic_resistance = 0.33
# membrane temperature slope [Ohm/(m^2K)]
membrane_temperature_resistance = 7.e-4
# bipolar plate resistivity [Ohm/m]
bipolar_plate_resistivity = 2.e-6


"""Thermal Settings"""
# thermal conductivity of the bipolar plate through plane  [W/(mK)]
thermal_conductivity_bipolar_plate_z = 1.e2
# thermal conductivity of the bipolar plate in plane  [W/(mK)]
thermal_conductivity_bipolar_plate_x = 1.e2
# thermal conductivity of the gde through plane  [W/(mK)]
thermal_conductivity_gas_diffusion_electrode_z = 1.e0
# thermal conductivity of the gde in plane  [W/(mK)]
thermal_conductivity_gas_diffusion_electrode_x = 1.e0
# thermal conductivity of the membrane through plane  [W/(mK)]
thermal_conductivity_membrane_z = .26e0
# thermal conductivity of the membrane in plane  [W/(mK)]
thermal_conductivity_membrane_x = .26e0
# heat capacity of the coolant [J/(kgK)]
heat_capacity_coolant = 4.e3
# convection coefficient between the coolant and the gas channel [W/(Km^2)]
convection_coefficient_coolant_channel = 4.e3
# convection coefficient between the stack walls and the environment [W/(Km^2)]
convection_coefficient_stack_environment = 5.e0
# latent heat of vaporization [J/mol]
enthalpy_vaporization = 45.4e3

"""Fluid Mechanic Settings"""
# geometrical pressure loss coefficient of the manifold header
manifold_pressure_loss_coefficient = 5.e5
# bend pressure loss coefficient of the channel bends
bend_pressure_loss_coefficient = 0.1
# number of channel bends
channel_bends = 48
# cathode channel gas flow direction
cathode_channel_flow_direction = True
# anode channel gas flow direction
anode_channel_flow_direction = False

"""Humidification"""
# cathode inlet gas relative humidity
inlet_humidity_cathode = 0.
# anode inlet gas relative humidity
inlet_humidity_anode = 0.

"""Species settings"""
# oxygen concentration at the cathode inlet
oxygen_inlet_concentration = 0.21
# hydrogen concentration at the anode inlet
hydrogen_inlet_concentration = 0.5

