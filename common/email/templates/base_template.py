__all__ = ["BaseTemplate"]

import json
from typing import Any


class BadTemplateError(Exception):
    pass


class BaseTemplate:
    """
    template_name:  Name of the SES Template.  This should be a constant from common.constants.email_templates
    subject:        Subject line of all emails for this template.  Use .format() methodology if it needs
                    values from self.args
                    e.g. `subject = "You have been selected for a grand prize of {prize} dollars!"`
                         then in _post_init() you can fill it in with `self.subject.format(prize=self.args["prize"])`
    required_args:  This is a list of the "required" args to be passed to the constructor in order for the template
                    to function.
    """

    template_name: str
    subject: str
    required_args: list[str] = []
    content: str
    args: dict[str, Any]  # This will be filled by the constructor

    def __init__(self, **kwargs: object) -> None:
        if not self.template_name:
            raise BadTemplateError(
                f"{self.__class__.__name__}.template_name has not been declared.  "
                f"Make sure it is a value from common.constants.email_templates!"
            )
        if not self.subject:
            raise BadTemplateError(f"{self.__class__.__name__}.subject has not been declared.")
        if not self.content:
            raise BadTemplateError(f"{self.__class__.__name__}.contentx has not been declared.")
        self.args = kwargs
        for arg in self.required_args:
            if arg not in self.args:
                raise BadTemplateError(f"{self.__class__.__name__} missing required argument '{arg}'")
        self._post_init()

    @property
    def data(self) -> str:
        """Useful property for serializing the args for SES send_templated_email()"""
        return json.dumps(self.args)

    def _post_init(self) -> None:
        """
        If you need to do anything special with the args/etc after init, you can use this function
        to perform those actions (like the example above in the docstring the templated 'subject'
        """
