import abc
import copy


PARAMETER_ATTRIBUTE = "__hyperparameters"


class ParameterDecorator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parameter_name):
        self.parameter_name = parameter_name

    @abc.abstractmethod
    def execute(self, parameters):
        """
        Execute the decorator.
        This method will be called during creation of the class object
        and will update the given set of hyperparameters according
        to the implementation of the subclass.

        :param parameters: The set of parameters to append to or delete from
        :type parameters: dict[str, object]
        """
        raise NotImplementedError("Execute Method has to be overwritten by subclasses")

    def __call__(self, class_):
        if not hasattr(class_, PARAMETER_ATTRIBUTE):
            # No __hyperparameters attribute, create a new one
            setattr(class_, PARAMETER_ATTRIBUTE, {})
        # Execute the Decorator
        parameters = copy.deepcopy(getattr(class_, PARAMETER_ATTRIBUTE))
        self.execute(parameters)
        setattr(class_, PARAMETER_ATTRIBUTE, parameters)
        # Return the class object
        return class_

    def __eq__(self, other):
        if hasattr(other, "parameter_name"):
            return self.parameter_name == other.parameter_name
        return False


class ChoiceParameter(ParameterDecorator):
    # TODO: Documentation
    def __init__(self, parameter_name, choices):
        # TODO: Documentation
        super(ChoiceParameter, self).__init__(parameter_name=parameter_name)
        if not isinstance(choices, list):
            choices = [choices]
        self.__choices = choices

    def execute(self, parameters):
        parameters[self.parameter_name] = self.__choices


class NormalParameter(ParameterDecorator):
    # TODO: Documentation
    def __init__(self, parameter_name, mu, sigma):
        # TODO: Documentation
        super(NormalParameter, self).__init__(parameter_name=parameter_name)
        self.__mu = mu
        self.__sigma = sigma

    def execute(self, parameters):
        parameters[self.parameter_name] = {
            "type": "float",
            "mu": self.__mu,
            "sigma": self.__sigma
        }


class UniformParameter(ParameterDecorator):
    # TODO: Documentation
    def __init__(self, parameter_name, min_value, max_value):
        # TODO: Documentation
        super(UniformParameter, self).__init__(parameter_name=parameter_name)
        self.__min = min_value
        self.__max = max_value

    def execute(self, parameters):
        parameters[self.parameter_name] = {
            "type": "float",
            "min": self.__min,
            "max": self.__max
        }


class QNormalParameter(NormalParameter):
    # TODO: Documentation
    def __init__(self, parameter_name, mu, sigma, q):
        super(QNormalParameter, self).__init__(parameter_name=parameter_name, mu=mu, sigma=sigma)
        self.__q = q

    def execute(self, parameters):
        super(QNormalParameter, self).execute(parameters)
        parameters[self.parameter_name]["q"] = self.__q


class QUniformParameter(NormalParameter):
    # TODO: Documentation
    def __init__(self, parameter_name, mu, sigma, q):
        super(QUniformParameter, self).__init__(parameter_name=parameter_name, mu=mu, sigma=sigma)
        self.__q = q

    def execute(self, parameters):
        super(QUniformParameter, self).execute(parameters)
        parameters[self.parameter_name]["q"] = self.__q


class NoOptimizationParameter(ParameterDecorator):
    # TODO: Documentation
    def execute(self, parameters):
        if self.parameter_name in parameters.keys():
            del parameters[self.parameter_name]
