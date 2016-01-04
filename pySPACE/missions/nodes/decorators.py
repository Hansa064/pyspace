import abc
import copy
import warnings

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
            # No hyper parameter attribute, create a new one
            setattr(class_, PARAMETER_ATTRIBUTE, set())
        # Deep copy the parameter attribute to avoid side-effects to super-classes
        parameters = copy.deepcopy(getattr(class_, PARAMETER_ATTRIBUTE))
        # Execute the Decorator on the copy
        self.execute(parameters)
        # And replace the attribute with the copy
        setattr(class_, PARAMETER_ATTRIBUTE, parameters)
        # Return the class object
        return class_

    def __eq__(self, other):
        if hasattr(other, "parameter_name"):
            return self.parameter_name == other.parameter_name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.parameter_name)


class AddParameterWithWarningMixIn(ParameterDecorator):

    def execute(self, parameters):
        if self in parameters:
            warnings.warn("Duplicate parameter definition for parameter '%s'! Replacing with the new definition" % self)
            parameters.remove(self)
        parameters.add(self)


class ChoiceParameter(AddParameterWithWarningMixIn):
    # TODO: Documentation
    def __init__(self, parameter_name, choices):
        # TODO: Documentation
        super(ChoiceParameter, self).__init__(parameter_name=parameter_name)
        if not isinstance(choices, list):
            choices = [choices]
        self.__choices = choices

    @property
    def choices(self):
        return self.__choices


class BooleanParameter(ChoiceParameter):
    def __init__(self, parameter_name):
        super(BooleanParameter, self).__init__(parameter_name, [True, False])


class NormalParameter(AddParameterWithWarningMixIn):
    # TODO: Documentation
    def __init__(self, parameter_name, mu, sigma):
        # TODO: Documentation
        super(NormalParameter, self).__init__(parameter_name=parameter_name)
        self.__mu = mu
        self.__sigma = sigma

    @property
    def mu(self):
        return self.__mu

    @property
    def sigma(self):
        return self.__sigma


class UniformParameter(AddParameterWithWarningMixIn):
    # TODO: Documentation
    def __init__(self, parameter_name, min_value, max_value):
        # TODO: Documentation
        super(UniformParameter, self).__init__(parameter_name=parameter_name)
        self.__min = min_value
        self.__max = max_value

    @property
    def min(self):
        return self.__min

    @property
    def max(self):
        return self.__max


class QMixin(object):
    def __init__(self, q):
        self.__q = q

    @property
    def q(self):
        return self.__q

class QNormalParameter(NormalParameter, QMixin):
    # TODO: Documentation
    def __init__(self, parameter_name, mu, sigma, q):
        super(QNormalParameter, self).__init__(parameter_name=parameter_name, mu=mu, sigma=sigma)
        QMixin.__init__(self, q=q)


class QUniformParameter(UniformParameter, QMixin):
    # TODO: Documentation
    def __init__(self, parameter_name, mu, sigma, q):
        super(QUniformParameter, self).__init__(parameter_name=parameter_name, mu=mu, sigma=sigma)
        QMixin.__init__(self, q=q)


class NoOptimizationParameter(ParameterDecorator):
    # TODO: Documentation
    def execute(self, parameters):
        if self in parameters:
            parameters.remove(self)
