from __future__ import annotations

class GroupNetCDFMixin:

    def to_nc_container(self, nc):
        this_group = nc.createGroup(self.meta.name)

        if self.groups is not None:
            for group in self.groups:
                group.to_nc_container(this_group)

        for var in self.variables:
            var.to_nc_container(this_group)

        for attr, value in self.attributes:
            if value is None:
                continue
            
            try:
                setattr(this_group, attr, value)
            except TypeError:
                setattr(this_group, attr, str(value))