import numpy as np
import copy as copy
import data.global_parameters as g_par
import system.cell as cl
import data.cell_dict as c_dict
import system.manifold as m_fold
import data.manifold_dict as m_fold_dict
import system.electrical_coupling as el_cpl
import data.electrical_coupling_dict as el_cpl_dict
import system.temperature_system as therm_cpl
import data.temperature_system_dict as therm_dict


class Stack:

    def __init__(self, dict_stack):
        # Handover
        self.cell_numb = dict_stack['cell_numb']
        # number of cells of the stack
        self.stoi_cat = dict_stack['stoi_cat']
        # inlet stoichiometry of the cathode header
        self.stoi_ano = dict_stack['stoi_ano']
        # inlet stoichiometry of the anode header
        nodes = g_par.dict_case['nodes']
        # node points along the x-axis
        self.alpha_env = dict_stack['alpha_env']
        # environment convection coefficient
        self.calc_temp = dict_stack['calc_temperature']
        # switch to calculate the temperature distribution
        self.calc_cd = dict_stack['calc_current_density']
        # switch to calculate the current density distribution
        self.calc_flow_dis = dict_stack['calc_flow_distribution']
        # switch to calculate the flow distribution

        self.cells = []
        # list of the stack cells
        for w in range(self.cell_numb):
            x = cl.Cell(c_dict.dict_cell)
            self.cells.append(x)
        self.set_stoichiometry(np.full(self.cell_numb, self.stoi_cat),
                               np.full(self.cell_numb, self.stoi_ano))

        # Initialize the manifolds
        self.manifold = [m_fold.Manifold(m_fold_dict.dict_mfold_cat),
                         m_fold.Manifold(m_fold_dict.dict_mfold_ano)]
        self.manifold[0].head_stoi = self.stoi_cat
        self.manifold[1].head_stoi = self.stoi_ano

        # Initialize the electrical coupling
        self.el_cpl_stack = el_cpl\
            .ElectricalCoupling(el_cpl_dict.dict_electrical_coupling)

        """boolean alarms"""
        self.v_alarm = False
        # True if :voltage loss > cell voltage
        self.break_program = False
        # True if the program aborts because of some critical impact

        """General data"""
        self.cathode_mfd_criteria = 0.
        # convergence criteria of the air manifold
        self.anode_mfd_criteria = 0.
        # convergence criteria of the h2 gas mix manifold
        self.i_cd = np.full((self.cell_numb, nodes - 1),
                            g_par.dict_case['tar_cd'])
        # current density
        self.i_cd_old = copy.deepcopy(self.i_cd)
        # current density of the last iteration
        self.i = np.full((self.cell_numb, nodes - 1), 20.)
        # current
        self.v_cell = []
        # cell voltage
        self.v_loss = []
        # cell voltage loss
        self.v_loss_cat = []
        # cathode voltage loss
        self.v_loss_ano = []
        # anode voltage loss
        self.stack_cell_r = []
        # cell resistance in z-direction
        self.q_sum_cat = []
        # molar flow at the inlet and outlet of the cathode channels
        self.q_sum_ano = []
        # molar flow  at the inlet and outlet of the anode channels
        self.m_sum_cat = []
        # mass flow at the inlet and outlet of the cathode channels
        self.m_sum_ano = []
        # mass flow at the inlet and outlet of the anode channels
        self.cp_cat = []
        # heat capacity in the cathode channels
        self.cp_ano = []
        # heat capacity in the anode channels
        self.visc_cat = []
        # viscosity at the inlet and outlet of the cathode channels
        self.visc_ano = []
        # viscosity at the inlet and outlet of the anode channels
        self.p_cat = []
        # pressure at the inlet and outlet of the cathode channels
        self.p_ano = []
        # pressure at the inlet and outlet of the anode channels
        self.r_cat = []
        # gas constant of air fluid at the inlet
        # and outlet of the cathode channels
        self.r_ano = []
        # gas constant of the hydrogen fluid at the
        # inlet and outlet of the anode channels
        self.temp_fluid_cat = []
        # inlet and outlet temperature of the cathode channel fluid
        self.temp_fluid_ano = np.zeros(self.cell_numb)
        # inlet and outlet temperature of the anode channel fluid
        self.k_alpha_env = np.full((2, 3, self.cell_numb), 0.)
        # convection conductance to the environment
        self.k_alpha_ch = None
        # convection conductance between the channel and the fluid
        self.cond_rate = np.full((2, self.cell_numb, nodes), 0.)
        # molar condensation rate
        self.omega = np.full((self.cell_numb, nodes), 0.)
        # electrical resistance of the membrane
        self.m_reac_flow_delta = np.full((self.cell_numb, nodes), 0.)
        # mass flow of the consumed oxygen in the cathode channels
        self.g_fluid = []
        # heat capacity flow of the channel fluids
        self.cp_h2 = np.full((self.cell_numb, nodes), 0.)
        k_p, k_g, k_m = [], [], []
        k_pp, k_gp, k_gm = [], [], []
        for i, item in enumerate(self.cells):
            k_p = np.hstack((k_p, self.cells[i].k_bpp_z))
            k_g = np.hstack((k_g, self.cells[i].k_gde_z))
            k_m = np.hstack((k_m, self.cells[i].k_mem_z))
            k_pp = np.hstack((k_pp, self.cells[i].k_bpp_x))
            k_gp = np.hstack((k_gp, self.cells[i].k_gp))
            k_gm = np.hstack((k_gm, self.cells[i].k_gm))
        self.k_layer = np.array([[k_m, k_g, k_p], [k_gm, k_gp, k_pp]])
        # heat conductivity of the cell layer

        """"Calculation of the environment heat conductivity"""
        # free convection geometry model
        cell_width = self.cells[0].cathode.cell_width
        cell_height = self.cells[0].cathode.cell_length
        fac = (cell_width + cell_height)\
            / (self.cells[0].cathode.channel.length
               * self.cells[0].width_channels)
        for q, item in enumerate(self.cells):
            self.k_alpha_env[0, 1, q] =\
                .5 * self.alpha_env * item.cathode.channel.dx\
                * (item.cathode.th_bpp + item.cathode.th_gde) / fac
            self.k_alpha_env[0, 0, q] =\
                .5 * (self.alpha_env * item.cathode.channel.dx
                      * (item.cathode.th_bpp + item.th_mem)) / fac
            self.k_alpha_env[0, 2, q] = \
                self.alpha_env * item.cathode.channel.dx\
                * item.cathode.th_bpp / fac
        # Initialize the thermal coupling
        therm_dict.dict_temp_sys['k_layer'] = self.k_layer
        therm_dict.dict_temp_sys['k_alpha_env'] = self.k_alpha_env
        self.temp_sys = therm_cpl.\
            TemperatureSystem(therm_dict.dict_temp_sys)

    def update(self):
        """
        This function coordinates the program sequence
        """
        for j in range(self.cell_numb):
            #self.cells[j].set_current_density(self.i_cd[j, :])
            self.cells[j].i_cd = self.i_cd[j, :]
            self.cells[j].update()
            if self.cells[j].break_program is True:
                self.break_program = True
                break
        if self.break_program is False:
            self.stack_dynamic_properties()
            if self.calc_temp is True:
                self.update_temperature_coupling()
            if self.cell_numb > 1:
                if self.calc_flow_dis is True:
                    self.update_flows()
            self.i_cd_old = copy.deepcopy(self.i_cd)
            if self.calc_cd is True:
                self.update_electrical_coupling()

    def update_flows(self):
        """
        This function updates the flow distribution of gas over the stack cells
        """
        self.manifold[0].update_values(
            m_fold_dict.manifold(self.q_sum_cat
                                 * self.cells[0].cathode.channel_numb,
                                 self.temp_fluid_cat,
                                 self.cp_cat, self.visc_cat,
                                 self.p_cat, self.r_cat,
                                 self.m_sum_f_cat
                                 * self.cells[0].cathode.channel_numb,
                                 self.m_sum_g_cat
                                 * self.cells[0].cathode.channel_numb))
        self.manifold[1].update_values(
            m_fold_dict.manifold(self.q_sum_ano[::-1]
                                 * self.cells[0].cathode.channel_numb,
                                 self.temp_fluid_ano[::-1],
                                 self.cp_ano[::-1],
                                 self.visc_ano[::-1],
                                 self.p_ano[::-1],
                                 self.r_ano[::-1],
                                 self.m_sum_f_ano[::-1]
                                 * self.cells[0].cathode.channel_numb,
                                 self.m_sum_g_ano[::-1]
                                 * self.cells[0].cathode.channel_numb))
        self.manifold[0].update()
        self.manifold[1].update()
        self.set_stoichiometry(self.manifold[0].cell_stoi,
                               self.manifold[1].cell_stoi)
        self.set_channel_outlet_pressure(self.manifold[0].head_p[-1],
                                         self.manifold[1].head_p[-1])
        self.cathode_mfd_criteria = self.manifold[0].criteria
        self.anode_mfd_criteria = self.manifold[1].criteria

    def update_electrical_coupling(self):
        """
        This function updates current distribution over the stack cells
        """

        self.el_cpl_stack.update_values(
            el_cpl_dict.electrical_coupling(self.v_loss,
                                            self.stack_cell_r))
        self.el_cpl_stack.update()
        self.i_cd = self.el_cpl_stack.i_cd

    def update_temperature_coupling(self):
        """
        This function updates the layer and fluid temperatures of the stack
        """

        current = self.i_cd * self.cells[0].active_area_dx
        n_ch = self.cells[0].cathode.channel_numb
        self.temp_sys.update_values(self.k_alpha_ch * n_ch,
                                    self.cond_rate * n_ch,
                                    self.omega,
                                    np.array([self.v_loss_cat,
                                              self.v_loss_ano]),
                                    self.g_fluid * n_ch, current)
        self.temp_sys.update()
        self.set_temperature()

    def stack_dynamic_properties(self):
        """
        This function sums up the dynamic values inside the cells
        necessary to calculate the flow distribution,
        the electrical coupling or the temperature coupling
        """

        v_alarm = []
        k_alpha_cat, k_alpha_ano = [], []
        g_fluid_cat, g_fluid_ano = [], []
        v_cell, v_loss, resistance = [], [], []
        v_loss_cat, v_loss_ano = [], []
        q_sum_cat_in, q_sum_cat_out = [], []
        q_sum_ano_in, q_sum_ano_out = [], []
        cp_cat_in, cp_cat_out = [], []
        cp_ano_in, cp_ano_out = [], []
        visc_cat_in, visc_cat_out = [], []
        visc_ano_in, visc_ano_out = [], []
        p_cat_in, p_cat_out = [], []
        p_ano_in, p_ano_out = [], []
        r_cat_in, r_cat_out = [], []
        r_ano_in, r_ano_out = [], []
        temp_fluid_cat_in, temp_fluid_cat_out = [], []
        temp_fluid_ano_in, temp_fluid_ano_out = [], []
        cond_rate_cat, cond_rate_ano = [], []
        m_sum_f_cat_in, m_sum_f_cat_out = [], []
        m_sum_f_ano_in, m_sum_f_ano_out = [], []
        m_sum_g_cat_in, m_sum_g_cat_out = [], []
        m_sum_g_ano_in, m_sum_g_ano_out = [], []
        omega = []
        for w, item in enumerate(self.cells):
            v_alarm.append(item.v_alarm)
            cond_rate_cat.append(item.cathode.cond_rate)
            cond_rate_ano.append(item.anode.cond_rate)
            k_alpha_cat.append(item.cathode.k_ht_coef_ca)
            k_alpha_ano.append(item.anode.k_ht_coef_ca)
            g_fluid_cat.append(item.cathode.g_fluid)
            g_fluid_ano.append(item.anode.g_fluid)
            v_cell.append(item.v)
            v_loss = np.hstack((v_loss, item.v_loss))
            v_loss_cat.append(item.cathode.v_loss)
            v_loss_ano.append(item.anode.v_loss)
            omega.append(item.omega)
            resistance = np.hstack((resistance, item.resistance))
            q_sum_cat_in = np.hstack((q_sum_cat_in, item.cathode.q_gas[0]))
            q_sum_cat_out = np.hstack((q_sum_cat_out, item.cathode.q_gas[-1]))
            q_sum_ano_in = np.hstack((q_sum_ano_in, item.anode.q_gas[0]))
            q_sum_ano_out = np.hstack((q_sum_ano_out, item.anode.q_gas[-1]))
            m_sum_f_cat_in = np.hstack((m_sum_f_cat_in,
                                      item.cathode.m_flow_fluid[0]))
            m_sum_f_cat_out = np.hstack((m_sum_f_cat_out,
                                       item.cathode.m_flow_fluid[-1]))
            m_sum_f_ano_in = np.hstack((m_sum_f_ano_in,
                                      item.anode.m_flow_fluid[0]))
            m_sum_f_ano_out = np.hstack((m_sum_f_ano_out,
                                       item.anode.m_flow_fluid[-1]))
            m_sum_g_cat_in = np.hstack((m_sum_g_cat_in,
                                      item.cathode.m_flow_gas[0]))
            m_sum_g_cat_out = np.hstack((m_sum_g_cat_out,
                                       item.cathode.m_flow_gas[-1]))
            m_sum_g_ano_in = np.hstack((m_sum_g_ano_in,
                                      item.anode.m_flow_gas[0]))
            m_sum_g_ano_out = np.hstack((m_sum_g_ano_out,
                                       item.anode.m_flow_gas[-1]))
            cp_cat_in = np.hstack((cp_cat_in, item.cathode.cp_fluid[0]))
            cp_cat_out = np.hstack((cp_cat_out, item.cathode.cp_fluid[-1]))
            cp_ano_in = np.hstack((cp_ano_in, item.anode.cp_fluid[0]))
            cp_ano_out = np.hstack((cp_ano_out, item.anode.cp_fluid[-1]))
            p_cat_in = np.hstack((p_cat_in, item.cathode.p[0]))
            p_cat_out = np.hstack((p_cat_out, item.cathode.p[-1]))
            p_ano_in = np.hstack((p_ano_in, item.anode.p[0]))
            p_ano_out = np.hstack((p_ano_out, item.anode.p[-1]))
            r_cat_in = np.hstack((r_cat_in, item.cathode.r_gas[0]))
            r_cat_out = np.hstack((r_cat_out, item.cathode.r_gas[-1]))
            r_ano_in = np.hstack((r_ano_in, item.anode.r_gas[0]))
            r_ano_out = np.hstack((r_ano_out, item.anode.r_gas[-1]))
            visc_cat_in = np.hstack((visc_cat_in, item.cathode.visc_gas[0]))
            visc_cat_out = np.hstack((visc_cat_out, item.cathode.visc_gas[-1]))
            visc_ano_in = np.hstack((visc_ano_in, item.anode.visc_gas[0]))
            visc_ano_out = np.hstack((visc_ano_out, item.anode.visc_gas[-1]))
            temp_fluid_cat_in = np.hstack((temp_fluid_cat_in,
                                           item.cathode.temp_fluid[0]))
            temp_fluid_cat_out = np.hstack((temp_fluid_cat_out,
                                            item.cathode.temp_fluid[-1]))
            temp_fluid_ano_in = np.hstack((temp_fluid_ano_in,
                                           item.anode.temp_fluid[0]))
            temp_fluid_ano_out = np.hstack((temp_fluid_ano_out,
                                            item.anode.temp_fluid[-1]))
        self.k_alpha_ch = np.array([k_alpha_cat, k_alpha_ano])
        self.omega = np.array(omega)
        self.cond_rate = np.array([cond_rate_cat, cond_rate_ano])
        self.g_fluid = np.array([g_fluid_cat, g_fluid_ano])
        self.v_cell, self.v_loss, self.stack_cell_r = v_cell, v_loss, resistance
        self.v_loss_cat, self.v_loss_ano = v_loss_cat, v_loss_ano
        self.q_sum_cat = np.array([q_sum_cat_in, q_sum_cat_out])
        self.q_sum_ano = np.array([q_sum_ano_in, q_sum_ano_out])
        self.m_sum_f_cat = np.array([m_sum_f_cat_in, m_sum_f_cat_out])
        self.m_sum_f_ano = np.array([m_sum_f_ano_in, m_sum_f_ano_out])
        self.m_sum_g_cat = np.array([m_sum_g_cat_in, m_sum_g_cat_out])
        self.m_sum_g_ano = np.array([m_sum_g_ano_in, m_sum_g_ano_out])
        self.cp_cat = np.array([cp_cat_in, cp_cat_out])
        self.cp_ano = np.array([cp_ano_in, cp_ano_out])
        self.visc_cat = np.array([visc_cat_in, visc_cat_out])
        self.visc_ano = np.array([visc_ano_in, visc_ano_out])
        self.p_cat = np.array([p_cat_in, p_cat_out])
        self.p_ano = np.array([p_ano_in, p_ano_out])
        self.r_cat = np.array([r_cat_in, r_cat_out])
        self.r_ano = np.array([r_ano_in, r_ano_out])
        self.temp_fluid_cat = np.array([temp_fluid_cat_in, temp_fluid_cat_out])
        self.temp_fluid_ano = np.array([temp_fluid_ano_in, temp_fluid_ano_out])
        self.v_alarm = np.array(v_alarm)

    def set_stoichiometry(self, stoi_cat, stoi_ano):
        """
        This function sets up the inlet stoichiometry
        of the cathode and anode channels.

            Manipulate:
            -.cathode.stoi
            -.anode.stoi
        """

        for w, item in enumerate(self.cells):
            item.cathode.stoi = stoi_cat[w]
            item.anode.stoi = stoi_ano[w]

    def set_channel_outlet_pressure(self, p_cat, p_ano):
        """
        This function sets up the inlet pressure
        of the cathode and the anode channels.

            Manipulate:
            -.cathode.channel.p_in
            -.anode.channel.p_in
        """

        for w, item in enumerate(self.cells):
            item.cathode.channel.p_out = p_cat[w]
            item.anode.channel.p_out = p_ano[w]

    def set_temperature(self):
        """
        This function sets up the layer and fluid temperatures in the cells.

            Manipulate:
            -.temp
            -.cathode.temp_fluid
            -.anode.temp_fluid
        """

        for w, item in enumerate(self.cells):
            item.temp = self.temp_sys.temp_layer[w][0:5, :]
            item.cathode.temp_fluid = self.temp_sys.temp_fluid[0, w]
            item.anode.temp_fluid = self.temp_sys.temp_fluid[1, w]
