from enum import StrEnum


class BaseClass(StrEnum):
    def __getattribute__(self, name):
        return super().__getattribute__(name)

    @classmethod
    def to_dict(cls):
        return {member.name: member.value for member in cls}

    @classmethod
    def get_keys(cls):
        return [member.name for member in cls]

    @classmethod
    def values(cls):
        return [member.value for member in cls]

    @classmethod
    def rename(cls):
        return {member.value: member.name for member in cls}
