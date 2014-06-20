'''
Created on Jun 17, 2014

@author: Aaron Klein
'''

import numpy as np
import matplotlib.pyplot as plt
import os
import logging


class Visualizer(object):

    def __init__(self, fanova):
        self._fanova = fanova

    def create_all_plots(self, directory, **kwargs):
        """
            Create plots for all main effects.
        """
        assert os.path.exists(directory), "directory %s doesn't exist" % directory

        #categorical parameters
        for param_name in self._fanova.get_config_space().get_categorical_parameters():
            plt.clf()
            outfile_name = os.path.join(directory, param_name.replace(os.sep, "_") + ".png")
            print "creating %s" % outfile_name
            self.plot_categorical_marginal(param_name)
            plt.savefig(outfile_name)

        #continuous and integer parameters
        params_to_plot = []
        params_to_plot.extend(self._fanova.get_config_space().get_continuous_parameters())
        params_to_plot.extend(self._fanova.get_config_space().get_integer_parameters())
        for param_name in params_to_plot:
            plt.clf()
            outfile_name = os.path.join(directory, param_name.replace(os.sep, "_") + ".png")
            print "creating %s" % outfile_name
            self.plot_marginal(param_name, **kwargs)
            plt.savefig(outfile_name)


    def plot_categorical_marginal(self, param):
        categorical_size = self._fanova.get_config_space().get_categorical_size(param)

        labels = self._fanova.get_config_space().get_categorical_values(param)
        logging.debug("LABELS:")
        logging.debug(labels)

        indices = np.asarray(range(categorical_size))
        width = 0.5
        marginals = [self._fanova.get_categorical_marginal_for_value(param, i) for i in range(categorical_size)]
        mean, std = zip(*marginals)
        plt.bar(indices, mean, width, color='red', yerr=std)
        plt.xticks(indices+width/2.0, labels)
        

    def plot_marginal(self, param, lower_bound=0, upper_bound=1, is_int=False, resolution=100):
        if isinstance(param, int):
            dim = param
            param_name = self._fanova.get_config_space().get_parameter_names()[dim]
        else:
            assert param in self._fanova.param_name2dmin, "param %s not known" % param
            dim = self._fanova.param_name2dmin[param]
            param_name = param

        grid = np.linspace(lower_bound, upper_bound, resolution)
        display_grid = [self._fanova.get_config_space().unormalize_value(param_name, value) for value in grid]

        mean = np.zeros(resolution)
        std = np.zeros(resolution)
        for i in xrange(0, resolution):
            (m, s) = self._fanova.get_marginal_for_value(dim, grid[i])
            mean[i] = m
            std[i] = s
        mean = np.asarray(mean)
        std = np.asarray(std)

        lower_curve = mean - std
        upper_curve = mean + std

        if param_name == "network/lr_policy@inv/power":
            print mean
            print std
            print display_grid
            print len(mean), len(std), len(display_grid)
        # if param_name in self._fanova.get_config_space().get_continuous_parameters():
        #     print ""
        #     print ""
        #     print param_name
        #     print np.diff(display_grid).std()
        #     print np.diff(np.log(display_grid)).std()
        if np.diff(display_grid).std() > 0.000001 and param_name in self._fanova.get_config_space().get_continuous_parameters():
            #HACK for detecting whether it's a log parameter, because the config space doesn't expose this information
            plt.semilogx(display_grid, mean, 'b')
            print "printing %s semilogx" % param_name
        else:
            plt.plot(display_grid, mean, 'b')
        plt.fill_between(display_grid, upper_curve, lower_curve, facecolor='red', alpha=0.6)
        plt.xlabel(param_name)

        plt.ylabel("Performance")
        return plt
        #plt.show()