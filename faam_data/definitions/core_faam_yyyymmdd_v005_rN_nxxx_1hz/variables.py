from faam_data.definitions import make_1hz
from faam_data.definitions.core_faam_yyyymmdd_v005_rN_nxxx.variables import (
    variables as v
)


variables = [make_1hz(i) for i in v]
