import pandas as pd
import numpy as np
from numpy_financial import pmt, ipmt, ppmt, npv, irr
import numpy_financial
import matplotlib.pyplot as plt

class economic_analysis:

    data_factors = np.array([[0.3, 0.5, 0.6],
                             [0.8, 0.6, 0.2],
                             [0.3, 0.3, 0.2],
                             [0.2, 0.2, 0.15],
                             [0.3, 0.3, 0.2],
                             [0.2, 0.2, 0.1],
                             [0.1, 0.1, 0.05],
                             [0.3, 0.4, 0.4],
                             [0.35, 0.25, 0.2],
                             [0.1, 0.1, 0.1]])

    Capital_factors = pd.DataFrame(data_factors,
                                   index=["fer", "fp", "fi", "fel", "fc", "fs", "fl", "OS", "D&E", "X"],
                                   columns=["Fluids", "Fluids-Solids", "Solids"])

    def boiler(self, Q, p, fm=1, installed=True):
        """Return boiler cost. Inputs:
        Vapor production (kg/h): 5000 < Q < 800000
        Pressure (bar): 			   10 < p < 70
        fm = material factor"""

        assert type(installed) == bool

        if Q < 5000 or Q > 800000:
            print(
                f"    - WARNING: boiler vapor production out of method bounds, 5000 < Q < 800000. Results may not be accurate.")

        if p < 10 or p > 70:
            print(f"    - WARNING: boiler pressure out of method bounds, 10 < p < 70. Results may not be accurate.")

        C = self.boiler_correlation(Q, p)

        if installed:
            C *= ((1 + self.Capital_factors.loc["fp"]["Fluids"]) * fm + (
                        self.Capital_factors.loc["fer"]["Fluids"] + self.Capital_factors.loc["fel"]["Fluids"]
                        + self.Capital_factors.loc["fi"]["Fluids"] + self.Capital_factors.loc["fc"]["Fluids"]
                        + self.Capital_factors.loc["fs"]["Fluids"] + self.Capital_factors.loc["fl"]["Fluids"]))

        return int(C)

    def pump(self, Q, fm=1, installed=True):
        """Return centrifuge pump cost for a caudal between 0.2 and 126 L/s. Inputs:
        phase = 'Fluids', 'Fluids - Solids' or 'Solids'
        fm = material factor"""

        assert type(installed) == bool

        if Q < 0.2 or Q > 126:
            print(f"    - WARNING: pump caudal out of method bounds, 0.2 < Q (L/s) < 126. Results may not be accurate.")

        C = self.pump_correlation(Q)

        if installed:
            C *= ((1 + self.Capital_factors.loc["fp"]["Fluids"]) * fm + (
                        self.Capital_factors.loc["fer"]["Fluids"] + self.Capital_factors.loc["fel"]["Fluids"]
                        + self.Capital_factors.loc["fi"]["Fluids"] + self.Capital_factors.loc["fc"]["Fluids"]
                        + self.Capital_factors.loc["fs"]["Fluids"] + self.Capital_factors.loc["fl"]["Fluids"]))

        return int(C)

    def steam_turbine(self, kW, fm=1, installed=True):
        """Return steam turbine cost for a power between 100 and 20000 kW. Inputs:
        fm = material factor"""

        assert type(installed) == bool

        if kW < 100 or kW > 20000:
            print(
                f"    - WARNING: steam turbine power out of method bounds, 100 < kW < 20000. Results may not be accurate.")

        C = self.turbine_correlation(kW)

        if installed:
            C *= ((1 + self.Capital_factors.loc["fp"]["Fluids"]) * fm + (
                    self.Capital_factors.loc["fer"]["Fluids"] + self.Capital_factors.loc["fel"]["Fluids"]
                    + self.Capital_factors.loc["fi"]["Fluids"] + self.Capital_factors.loc["fc"]["Fluids"]
                    + self.Capital_factors.loc["fs"]["Fluids"] + self.Capital_factors.loc["fl"]["Fluids"]))

        return int(C)

    def loan(self, quantity, interest, years):
        """Compute annual payment of a loan. Inputs:
        quantity [monetary units] == investment which will be funded
        interest [as fraction of unity] == annual interest
        years == number of years to return the loan."""

        assert quantity > 0
        assert interest >= 0 and interest <= 1
        assert years > 1

        loan_payment = pmt(interest, years, quantity)
        loan_interest = ipmt(interest, np.arange(years) + 1, years, quantity)
        loan_principal = ppmt(interest, np.arange(years) + 1, years, quantity)

        return loan_payment, loan_interest, loan_principal

    def depreciation(self, annual_percent, capex, residual_value=0):
        """Compute annual depreciation of investment. Inputs:
        annual_percent [as fraction of unity] == annual percent of depreciation.
        capex [monetary units] == capital expenditure
        residual_value[monetary units] == plant value at the end of its life."""

        assert annual_percent >= 0 and annual_percent <= 1

        annual_depreciation = []
        prev = 1

        while True:
            if prev < annual_percent:
                annual_depreciation.append(prev)
                break
            annual_depreciation.append(annual_percent)
            prev = prev - annual_percent

        depreciation_array = -1 * np.array(annual_depreciation) * (capex - residual_value)

        return depreciation_array

    def william_correlation(self, cost_ref, cap, cap_ref, n):
        """
        :param cost_ref: reference cost (maybe could be a static value)
        :param cap: cost estimation capacity
        :param cap_ref: referece capacity (maybe could be a static value)
        :param n: a factor whose values are between 0.6-1
        :return: William correlation value
        """

        cost = cost_ref * ((cap/cap_ref)**n)

        return cost

    def boiler_correlation(self, valor_production, pressure):
        if valor_production < 20000:
            correlation = 106000 + 8.7 * valor_production
        elif valor_production < 200000:
            if pressure < 15:
                correlation = 110000 + 4.5 * valor_production ** 0.9
            elif pressure < 40:
                correlation = 106000 + 8.7 * valor_production
            else:
                correlation = 110000 + 4.5 * valor_production ** 0.9
        else:
            correlation = 110000 + 4.5 * valor_production ** 0.9

        return int(correlation)

    def turbine_correlation(self, power):
        correlation = -12000 + 1630 * power ** 0.75
        return int(correlation)

    def pump_correlation(self, caudal):
        correlation = 6900 + 206 * caudal ** 0.9
        return int(correlation)

    def payback(self, cash_flow):
        cash_flow_by_years = np.asarray(cash_flow)
        years = 1
        for cash in cash_flow_by_years:
            if cash < 0:
                years = years + 1
            if cash >= 0:
                years = years
                break
        return years


    def execute(self):

        # Calculating capital costs (CAPEX)
        boiler = self.boiler(10000, 70)
        turbine = self.steam_turbine(1500)
        condenser = 400000 * (10000 / 15000) ** 0.8
        pump = self.pump(2.84)

        capex = boiler + turbine + condenser + pump

        # Calculating operational costs (OPEX)
        capacity_factor = 0.9

        water = 1.29 * 10 * 8760 * capacity_factor
        salaries = 4 * 3 * 30000

        # Calculating loan
        quantity = 0.6 * capex
        _, interest, principal = self.loan(quantity, 0.04, 10)

        # Calculating depreciation
        dep_array = self.depreciation(0.07, capex)

        # Calculating sales
        sales = 1500 * 0.05 * 8760 * capacity_factor

        # Calculating financial model
        years = 20

        investment = np.array([-capex * 0.4] + [0 for i in range(years - 1)])
        depreciation = np.hstack(([0], dep_array, [0 for i in range(years - 1 - len(dep_array))]))
        loan_prin = np.hstack(([0], principal, [0 for i in range(years - 1 - len(principal))]))
        loan_int = np.hstack(([0], interest, [0 for i in range(years - 1 - len(interest))]))

        sales_array = np.zeros(years)
        water_array = np.zeros(years)
        salaries_array = np.zeros(years)

        for i in range(years):
            if i == 0:
                sales_array[i] = 0
                water_array[i] = 0
                salaries_array[i] = 0
            elif i == 1:
                sales_array[i] = sales
                water_array[i] = -1 * water
                salaries_array[i] = -1 * salaries
            else:
                sales_array[i] = sales_array[i - 1] * 1.03
                water_array[i] = water_array[i - 1] * 1.03
                salaries_array[i] = salaries_array[i - 1] * 1.02

        ebt = np.vstack((investment, depreciation, loan_int, sales_array, water_array, salaries_array)).sum(axis=0)
        taxes = ebt * -0.3
        for i in range(len(taxes)):
            if taxes[i] > 0:
                taxes[i] = 0
        eat = ebt - taxes
        cash_flow = eat - depreciation + loan_prin
        cumulative_cash_flow = np.cumsum(cash_flow)

        data = np.vstack((investment, sales_array, depreciation, loan_prin, loan_int, salaries_array, water_array, ebt,
                          taxes, eat, cash_flow, cumulative_cash_flow))
        df = pd.DataFrame(data,
                          index=['Investment', 'Sales', 'Depreciation', 'Loan principal', 'Loan interest', 'Salaries',
                                 'Water', 'EBT', 'Taxes', 'EAT', 'Cash Flow', 'Cumulative Cash Flow'],
                          columns=[i for i in range(years)])

        # Calculating financial metrics
        discount_rate = 0.053

        npv = numpy_financial.npv(discount_rate, cash_flow)
        irr = numpy_financial.irr(cash_flow)

        npvArr = np.asarray(cash_flow)
        npvRet = []

        for n in npvArr:
            auxInt = (n/(1+discount_rate)**np.arange(0, len(npvArr)))
            npvRet.append(auxInt)

        npvDF = pd.DataFrame(npvRet,
                             index=[i for i in range(len(npvArr))],
                             columns=[i for i in range(len(npvArr))])

        # Printing results

        print("The Internal Rate of Return (IIR) is: " + str(irr))
        print("We go to see the Net Present Value as a Data Frame: ")
        print(npvRet)
        print("\nWe go to see df: ")
        print(df)
        print(
            f"The project has a net present value of {'{:,.2f}'.format(npv)}€ and an internal rate of return of {round(irr * 100, 2)}%")

        # Showing using matplotlib
        plt.plot(cumulative_cash_flow, label="Cumulative cash flow")
        plt.plot(cash_flow, 'ks', label="Cash flow")
        plt.plot(sales_array, 'bo', label="Incomings")
        plt.plot(npvArr, label="Net Present Value")
        plt.plot(loan_prin, 'r*', label="Outgoings")
        plt.xlabel("Year")
        plt.ylabel("€")
        plt.legend()
        plt.show()

        # Exportamos a Excel los resultados
        df.to_excel(r'results.xlsx', index=True)