import pandas as pd

from empire.utils import scale_and_shift_series


def test_scale_and_shift_series():
    series = pd.Series([1, 4, 6, 8, 3, 2], dtype=float)
    profile = series / series.max()
    scale = 10
    shift = 2

    profile_adjusted = scale_and_shift_series(profile=profile, scale=scale, shift=shift)

    (profile_adjusted * (scale + shift)).mean()

    pd.testing.assert_series_equal((profile * scale + shift), profile_adjusted * (scale + shift))
