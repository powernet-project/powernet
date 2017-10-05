from enumfields.fields import EnumFieldMixin
from rest_framework.fields import ChoiceField
from django.utils.translation import ugettext_lazy as _


class EnumField(ChoiceField):
    default_error_messages = {
        'invalid': _("No matching enum type.")
    }

    def __init__(self, **kwargs):
        self.enum_type = kwargs.pop("enum_type")
        kwargs.pop("choices", None)
        super(EnumField, self).__init__(self.enum_type.choices(), **kwargs)

    def to_internal_value(self, data):
        for choice in self.enum_type:
            if choice.name == data or choice.value == data:
                return choice
        self.fail('invalid')

    def to_representation(self, value):
        if not value:
            return None
        return value.name


class EnumFieldSerializerMixin(object):
    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super(EnumFieldSerializerMixin, self).build_standard_field(field_name, model_field)
        if field_class == ChoiceField and isinstance(model_field, EnumFieldMixin):
            field_class = EnumField
            field_kwargs['enum_type'] = model_field.enum
        return field_class, field_kwargs
