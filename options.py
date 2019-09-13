import matplotlib.pyplot as plt
import numpy as np

from qiskit import BasicAer
from qiskit.aqua.algorithms import AmplitudeEstimation
from qiskit.aqua.components.uncertainty_models import LogNormalDistribution
from qiskit.aqua.components.uncertainty_problems import UnivariateProblem
from qiskit.aqua.components.uncertainty_problems import UnivariatePiecewiseLinearObjective as PwlObjective

class EuropeanCallOption:
   
    def __init__(self, value, spot_price, volatility, int_rate, days, strike_price):
        self.value = value
        # Number of qubits to represent the uncertainty
        num_uncertainty_qubits = 3

        # Parameters
        try:
            S = float(spot_price) 
            vol = float(volatility) 
            r = float(int_rate) 
            T = int(days) / 365 
        except ValueError:
           print("Some parameters wrong !!! ")

        mu = ((r - 0.5 * vol**2) * T + np.log(S))
        sigma = vol * np.sqrt(T)
        mean = np.exp(mu + sigma**2/2)
        variance = (np.exp(sigma**2) - 1) * np.exp(2*mu + sigma**2)
        stddev = np.sqrt(variance)

        low  = np.maximum(0, mean - 3*stddev)
        high = mean + 3*stddev

        # Circuit factory for uncertainty model
        self. uncertainty_model = LogNormalDistribution(num_uncertainty_qubits, mu=mu, sigma=sigma, low=low, high=high)

        try: 
            self.strike_price = float(strike_price)
        except ValueError:
            print("Some parameters wrong !!! ")

        # The approximation scaling for the payoff function
        c_approx_payoff = 0.25

        breakpoints = [self.uncertainty_model.low, self.strike_price]

        if self.value == str("call"):
            slopes_payoff = [0, 1]
        else: slopes_payoff = [-1, 0]
       
        if self.value == str("call"):
            offsets_payoff = [0, 0]
        else: offsets_payoff =[self.strike_price - self.uncertainty_model.low, 0]
        
        f_min_payoff = 0

        if self.value == str("call"):
            f_max_payoff = self.uncertainty_model.high - self.strike_price
        else: f_max_payoff = self.strike_price - self.uncertainty_model.low

        european_objective = PwlObjective(

            self.uncertainty_model.num_target_qubits, 

            self.uncertainty_model.low, 

            self.uncertainty_model.high,

            breakpoints,

            slopes_payoff,

            offsets_payoff,

            f_min_payoff,

            f_max_payoff,

            c_approx_payoff

        )

        # Circuit factory for payoff function
        self.european_payoff = UnivariateProblem(

            self.uncertainty_model,

            european_objective

        )
        

        slopes_delta = [0, 0]

        if self.value == str("call"):
            offsets_delta = [0, 1]
        else: offsets_delta = [1, 0]
        

        f_min_delta = 0

        f_max_delta = 1

        c_approx_delta = 1
        
        european_delta_objective = PwlObjective(
            self.uncertainty_model.num_target_qubits, 

            self.uncertainty_model.low, 

            self.uncertainty_model.high,

            breakpoints,

            slopes_delta,

            offsets_delta,

            f_min_delta,

            f_max_delta,

            c_approx_delta
        )

        self.european_delta = UnivariateProblem(
            self. uncertainty_model,

            european_delta_objective
        )
        
    def plot_probability_distribution(self):
        x = self.uncertainty_model.values
        y = self.uncertainty_model.probabilities
        plt.bar(x, y, width=0.2)
        plt.xticks(x, size=15, rotation=90)
        plt.yticks(size=15)
        plt.grid()
        plt.title('Underlying', size=15)
        plt.xlabel('Spot Price at Maturity $S_T$ (CHF)', size=15)
        plt.ylabel('Probability ($\%$)', size=15)
        mng = plt.get_current_fig_manager()

        mng.resize(*mng.window.maxsize())
        plt.show()
        
    def plot_payoff_function(self):
        self.x = self.uncertainty_model.values
        if self.value == str("call"):
            self.y = np.maximum(0, self.x - self.strike_price)
        else: self.y = np.maximum(0, self.strike_price - self.x)

        plt.plot(self.x, self.y, 'ro-')

        plt.grid()

        plt.title('Payoff Function', size=15)

        plt.xlabel('Spot Price', size=15)

        plt.ylabel('Payoff', size=15)

        plt.xticks(self.x, size=15, rotation=90)

        plt.yticks(size=15)
        mng = plt.get_current_fig_manager()

        mng.resize(*mng.window.maxsize())

        plt.show()
        
    def print_exact_values(self):
        self.exact_value = np.dot(self.uncertainty_model.probabilities, self.y)
        if self.value == str("call"):
            self.exact_delta = sum(self.uncertainty_model.probabilities[self.x >= self.strike_price])
        else: self.exact_delta = -sum(self.uncertainty_model.probabilities[self.x <= self.strike_price])
        
        
    def evaluate_expected_payoff(self):
        # Set number of evaluation qubits (=log(samples))
        m = 6
        
        # Amplitude estimation 
        ae = AmplitudeEstimation(m, self.european_payoff)
        
        self.result = ae.run(quantum_instance=BasicAer.get_backend('statevector_simulator'))
        
        print('---------------------------')
        print('Exact value:    \t%.4f' % self.exact_value)
        print('Estimated value:\t%.4f' % self.result['estimation'])
        print('Probability:    \t%.4f' % self.result['max_probability'])
        print('---------------------------\n')
        
    def plot_estimated_data_values(self):

        plt.bar(self.result['values'], self.result['probabilities'], width=0.5/len(self.result['probabilities']))

        plt.xticks([0, 0.25, 0.5, 0.75, 1], size=15)

        plt.yticks([0, 0.25, 0.5, 0.75, 1], size=15)

        plt.title('Payoff', size=15)

        plt.ylabel('Probability', size=15)

        plt.ylim((0,1))

        plt.grid()
        mng = plt.get_current_fig_manager()

        mng.resize(*mng.window.maxsize())
        plt.show()

        plt.bar(self.result['mapped_values'], self.result['probabilities'], width=1/len(self.result['probabilities']))

        plt.plot([self.exact_value, self.exact_value], [0,1], 'r--', linewidth=2)

        plt.xticks(size=15)

        plt.yticks([0, 0.25, 0.5, 0.75, 1], size=15)

        plt.title('Estimated Option Price', size=15)

        plt.ylabel('Probability', size=15)

        plt.ylim((0,1))

        plt.grid()
        mng = plt.get_current_fig_manager()

        mng.resize(*mng.window.maxsize())

        plt.show()

    def evaluate_delta(self):
        # Set number of evaluation qubits (=log(samples))
        m = 6
        
        # Amplitude estimation 

        ae_delta = AmplitudeEstimation(m, self.european_delta)
        self.result_delta = ae_delta.run(quantum_instance=BasicAer.get_backend('statevector_simulator'))
        print('---------------------------')
        
        print('Exact delta:   \t%.4f' % self.exact_delta)
        
        if self.value == str("call"):
            print('Estimated value:\t%.4f' % self.result_delta['estimation'])
        else: print('Estimated value:\t%.4f' % -self.result_delta['estimation'])
        
        print('Probability:   \t%.4f' % self.result_delta['max_probability'])
        
        print('---------------------------\n')
        
    def plot_estimated_delta_values(self):
        if self.value == str("call"):
            plt.bar(self.result_delta['values'], self.result_delta['probabilities'], width=0.5/len(self.result_delta['probabilities']))
        else: plt.bar(-np.array(self.result_delta['values']), self.result_delta['probabilities'], width=0.5/len(self.result_delta['probabilities']))
        

        plt.plot([self.exact_delta, self.exact_delta], [0,1], 'r--', linewidth=2)

        plt.xticks(size=15)

        plt.yticks([0, 0.25, 0.5, 0.75, 1], size=15)

        plt.title('Estimated Option Delta', size=15)

        plt.ylabel('Probability', size=15)

        plt.ylim((0,1))

        plt.grid()

        mng = plt.get_current_fig_manager()

        mng.resize(*mng.window.maxsize())
        plt.show()
