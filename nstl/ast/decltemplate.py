"""This file contains the DeclTemplate class."""

from .decl import NamedDecl
from .redeclarable import Redeclarable


class TemplateDecl(NamedDecl):
    """This is the parent class of all templated declarations.
    
    _params             The parameters to this template.
    _templated_decl     The underlying named declaration used as a template.
    
    """
    
    def __init__(self, templated_decl, parameters, name, declaration_context):
        super().__init__(name, declaration_context)
        self._templated_decl = templated_decl
        self._params = parameters
    
    @property
    def params(self):
        """Return the template parameters of this template."""
        return self._params
    
    @property
    def templated_decl(self):
        """Return the underlying named declaration."""
        return self._templated_decl


class RedeclarableTemplateDecl(TemplateDecl, Redeclarable):
    """This class represents a template declaration that can be redeclared.
    
    _member_template    A member template from which this template is
                        instantiated, or None.
    
    _is_member_spec     A boolean expressing whether this template is the
                        specialization of a member template.
    
    """
    
    def __init__(self, templated_decl, parameters, name, declaration_context):
        super().__init__(templated_decl, parameters, name, declaration_context)
        self.instantiated_from_member_template = None
        self._is_member_spec = False
    
    @property
    def instantiated_from_member_template(self):
        """Return the original member template from which a template was
           instantiated."""
        return self._member_template
    
    @instantiated_from_member_template.setter
    def instantiated_from_member_template(self, original_member_template):
        """Set the original member template from which a template was
           instantiated."""
        self._member_template = original_member_template
    
    def is_instantiated_from_member_template(self):
        """Return whether this template is instantiated from a member template.
        """
        return self.instantiated_from_member_template is not None
    
    def set_is_member_specialization(self):
        """Mark this template as a member specialization."""
        assert self.is_instantiated_from_member_template(), \
                "Only member templates can be member template specializations."
        self._is_member_spec = True
    
    def is_member_specialization(self):
        """Return whether this template is the specialization of a member
           template."""
        return self._is_member_spec


if __name__ == "__main__":
    pass
