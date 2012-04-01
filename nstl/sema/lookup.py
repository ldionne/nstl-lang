"""Interface to do lexical scoped lookup based on declaration names."""


class ResolutionException(Exception):
    """Parent class of all resolution related exceptions."""
    pass


class NameNotFoundException(ResolutionException):
    """Exception raised whenever the lookup fails because
       the name can't be found."""
    pass


class Resolver(object):
    
    def resolve(self, decl_name):
        raise NameNotFoundException


if __name__ == "__main__":
    pass
