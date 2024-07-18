from rest_framework import serializers


class EnumField(serializers.Field):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        super().__init__(**kwargs)

    def to_representation(self, value):
        if isinstance(value, self.enum):
            return value.value

        return self.enum(int(value)).value

    def to_internal_value(self, data):
        try:
            if isinstance(data, int):
                return self.enum(data)
            elif isinstance(data, str) and data.isdigit():
                return self.enum(int(data))
            elif isinstance(data, str):
                return self.enum[data]
        except (KeyError, ValueError):
            self.fail("invalid_choice", input=data)
        return serializers.ValidationError(f"{data} is not a valid {self.enum.__name__}")
