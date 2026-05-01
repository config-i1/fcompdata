"""Basic tests for fcompdata package."""

import numpy as np
import pytest


class TestImports:
    """Test that package imports correctly."""

    def test_import_package(self):
        import fcompdata
        assert hasattr(fcompdata, "__version__")

    def test_import_datasets(self):
        from fcompdata import M1, M3, Tourism
        assert M1 is not None
        assert M3 is not None
        assert Tourism is not None

    def test_import_loaders(self):
        from fcompdata import load_m1, load_m3, load_tourism
        assert callable(load_m1)
        assert callable(load_m3)
        assert callable(load_tourism)

    def test_import_classes(self):
        from fcompdata import MCompDataset, MCompSeries
        assert MCompDataset is not None
        assert MCompSeries is not None


class TestM3Dataset:
    """Test M3 dataset loading and access."""

    def test_load_m3(self):
        from fcompdata import load_m3
        m3 = load_m3()
        assert len(m3) == 3003

    def test_lazy_m3_length(self):
        from fcompdata import M3
        assert len(M3) == 3003

    def test_m3_keys(self):
        from fcompdata import M3
        keys = M3.keys()
        assert keys[0] == 1  # 1-based indexing
        assert len(keys) == 3003

    def test_m3_first_series(self):
        from fcompdata import M3
        series = M3[1]
        assert series is not None
        assert series.sn is not None

    def test_m3_subset(self):
        from fcompdata import M3
        yearly = M3.subset("yearly")
        assert len(yearly) == 645


class TestM1Dataset:
    """Test M1 dataset loading and access."""

    def test_load_m1(self):
        from fcompdata import load_m1
        m1 = load_m1()
        assert len(m1) == 1001

    def test_lazy_m1_length(self):
        from fcompdata import M1
        assert len(M1) == 1001

    def test_m1_first_series(self):
        from fcompdata import M1
        series = M1[1]
        assert series is not None


class TestTourismDataset:
    """Test Tourism dataset loading and access."""

    def test_load_tourism(self):
        from fcompdata import load_tourism
        tourism = load_tourism()
        assert len(tourism) == 1311

    def test_lazy_tourism_length(self):
        from fcompdata import Tourism
        assert len(Tourism) == 1311

    def test_tourism_first_series(self):
        from fcompdata import Tourism
        series = Tourism[1]
        assert series is not None


class TestMCompSeries:
    """Test MCompSeries attributes and access patterns."""

    @pytest.fixture
    def sample_series(self):
        from fcompdata import M3
        return M3[1]

    def test_series_has_required_attributes(self, sample_series):
        assert hasattr(sample_series, "sn")
        assert hasattr(sample_series, "x")
        assert hasattr(sample_series, "xx")
        assert hasattr(sample_series, "h")
        assert hasattr(sample_series, "period")
        assert hasattr(sample_series, "type")
        assert hasattr(sample_series, "n")
        assert hasattr(sample_series, "description")

    def test_series_x_is_numpy_array(self, sample_series):
        assert isinstance(sample_series.x, np.ndarray)

    def test_series_xx_is_numpy_array(self, sample_series):
        assert isinstance(sample_series.xx, np.ndarray)

    def test_series_h_is_int(self, sample_series):
        assert isinstance(sample_series.h, int)
        assert sample_series.h > 0

    def test_series_n_matches_x_length(self, sample_series):
        assert sample_series.n == len(sample_series.x)

    def test_series_dict_style_access(self, sample_series):
        # Both attribute and dict-style access should work
        assert sample_series["x"] is sample_series.x
        assert sample_series["xx"] is sample_series.xx
        assert sample_series["h"] == sample_series.h
        assert sample_series["sn"] == sample_series.sn

    def test_series_keys(self, sample_series):
        keys = sample_series.keys()
        assert "x" in keys
        assert "xx" in keys
        assert "h" in keys
        assert "sn" in keys
        assert "period" in keys
        assert "type" in keys
        assert "n" in keys
        assert "description" in keys

    def test_series_repr(self, sample_series):
        repr_str = repr(sample_series)
        assert "MCompSeries" in repr_str
        assert sample_series.sn in repr_str

    def test_series_y_concatenates_x_and_xx(self, sample_series):
        expected = np.concatenate([sample_series.x, sample_series.xx])
        assert np.array_equal(sample_series.y, expected)
        assert len(sample_series.y) == sample_series.n + sample_series.h
        # Dict-style access works for the property
        assert np.array_equal(sample_series["y"], expected)
        assert "y" in sample_series.keys()


class TestMCompDataset:
    """Test MCompDataset operations."""

    @pytest.fixture
    def dataset(self):
        from fcompdata import load_m3
        return load_m3()

    def test_dataset_getitem_valid(self, dataset):
        series = dataset[1]
        assert series is not None

    def test_dataset_getitem_invalid(self, dataset):
        with pytest.raises(KeyError):
            _ = dataset[99999]

    def test_dataset_iteration(self, dataset):
        count = 0
        for series in dataset:
            count += 1
            if count >= 5:  # Only check first 5 to keep test fast
                break
        assert count == 5

    def test_dataset_items(self, dataset):
        for idx, series in dataset.items():
            assert isinstance(idx, int)
            assert series is not None
            break  # Only check first one

    def test_dataset_repr(self, dataset):
        repr_str = repr(dataset)
        assert "M3" in repr_str
        assert "3003" in repr_str

    def test_subset_returns_dataset(self, dataset):
        from fcompdata import MCompDataset
        subset = dataset.subset("monthly")
        assert isinstance(subset, MCompDataset)

    def test_subset_filters_correctly(self, dataset):
        monthly = dataset.subset("monthly")
        for series in monthly:
            assert series.type == "monthly"
            break  # Only check first one


class TestM4Imports:
    """Test M4 imports and error handling."""

    def test_import_m4(self):
        from fcompdata import M4
        assert M4 is not None

    def test_import_load_m4(self):
        from fcompdata import load_m4
        assert callable(load_m4)

    def test_load_m4_without_download_raises_error(self):
        from fcompdata import load_m4
        from fcompdata.download import get_m4_path
        # Skip if data already exists (e.g., from previous test runs)
        if get_m4_path("hourly") is not None:
            pytest.skip("M4 hourly data already downloaded")
        # M4 requires downloading first, so this should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            load_m4("hourly")

    def test_load_m4_invalid_frequency(self):
        from fcompdata import load_m4
        with pytest.raises(ValueError, match="Unknown frequency"):
            load_m4("invalid")


class TestDownloadModule:
    """Test download module functions."""

    def test_import_download_module(self):
        from fcompdata.download import download_m4, get_data_home, get_m4_path, clear_cache
        assert callable(download_m4)
        assert callable(get_data_home)
        assert callable(get_m4_path)
        assert callable(clear_cache)

    def test_get_data_home_returns_path(self):
        from pathlib import Path
        from fcompdata.download import get_data_home
        data_home = get_data_home()
        assert isinstance(data_home, Path)
        assert data_home.name == ".fcompdata"

    def test_get_m4_path_returns_none_when_not_downloaded(self):
        from fcompdata.download import get_m4_path
        # Should return None if not downloaded
        path = get_m4_path("yearly")
        # Path is None or exists (if previously downloaded)
        assert path is None or path.exists()

    def test_get_m4_path_invalid_frequency(self):
        from fcompdata.download import get_m4_path
        with pytest.raises(ValueError, match="Unknown frequency"):
            get_m4_path("invalid")

    def test_m4_urls_defined(self):
        from fcompdata.download import M4_URLS, M4_FILENAMES
        expected_frequencies = ["yearly", "quarterly", "monthly", "weekly", "daily", "hourly"]
        for freq in expected_frequencies:
            assert freq in M4_URLS
            assert freq in M4_FILENAMES

    def test_download_m4_invalid_frequency(self):
        from fcompdata.download import download_m4
        with pytest.raises(ValueError, match="Unknown frequency"):
            download_m4("invalid")


class TestIndividualSeries:
    """Test the bundled individual time series (AirPassengers, BJsales, Seatbelts, taylor)."""

    def test_imports(self):
        from fcompdata import (
            AirPassengers, BJsales, PromoData, Seatbelts, load_individual, taylor,
        )
        assert callable(load_individual)
        for s in (AirPassengers, BJsales, Seatbelts, taylor, PromoData):
            assert s is not None

    def test_load_individual(self):
        from fcompdata import load_individual
        ds = load_individual()
        assert len(ds) == 5
        assert {ds[i].sn for i in ds.keys()} == {
            "AirPassengers", "BJsales", "Seatbelts", "taylor", "PromoData",
        }

    def test_airpassengers(self):
        from fcompdata import AirPassengers
        assert AirPassengers.sn == "AirPassengers"
        assert AirPassengers.h == 12
        assert AirPassengers.period == 12
        assert AirPassengers.type == "monthly"
        assert AirPassengers.x.shape == (132,)
        assert AirPassengers.xx.shape == (12,)
        assert AirPassengers.n == 132
        assert AirPassengers.xreg is None
        assert AirPassengers.xregx is None
        assert AirPassengers.xregxx is None
        # First training value (R: AirPassengers[1] = 112)
        assert AirPassengers.x[0] == 112

    def test_bjsales(self):
        from fcompdata import BJsales
        assert BJsales.sn == "BJsales"
        assert BJsales.h == 12
        assert BJsales.period == 12
        assert BJsales.type == "monthly"
        assert BJsales.x.shape == (138,)
        assert BJsales.xx.shape == (12,)
        # xreg carries the leading indicator with its R name preserved
        assert BJsales.xreg is not None
        assert BJsales.xreg.dtype.names == ("BJsales.lead",)
        assert len(BJsales.xreg) == 150
        assert len(BJsales.xregx) == 138
        assert len(BJsales.xregxx) == 12
        # First lead value matches R's BJsales.lead[1] = 10.01
        assert BJsales.xreg["BJsales.lead"][0] == pytest.approx(10.01)

    def test_seatbelts(self):
        from fcompdata import Seatbelts
        assert Seatbelts.sn == "Seatbelts"
        assert Seatbelts.h == 12
        assert Seatbelts.period == 12
        assert Seatbelts.type == "monthly"
        assert Seatbelts.x.shape == (180,)
        assert Seatbelts.xx.shape == (12,)
        assert Seatbelts.xreg is not None
        assert Seatbelts.xreg.dtype.names == ("kms", "PetrolPrice", "law")
        assert len(Seatbelts.xreg) == 192
        assert len(Seatbelts.xregx) == 180
        assert len(Seatbelts.xregxx) == 12
        # The seat-belt law was in force from Feb 1983; total months under law = 23
        assert Seatbelts.xreg["law"].sum() == 23.0
        # Recarray attribute access also works
        assert np.array_equal(Seatbelts.xreg.kms, Seatbelts.xreg["kms"])

    def test_taylor(self):
        from fcompdata import taylor
        assert taylor.sn == "taylor"
        assert taylor.h == 336
        assert taylor.period == 336
        assert taylor.type == "halfhourly"
        assert taylor.x.shape == (3696,)
        assert taylor.xx.shape == (336,)
        assert taylor.xreg is None

    def test_xreg_concat_invariant(self):
        """xreg must equal the row-wise concatenation of xregx and xregxx."""
        from fcompdata import BJsales, Seatbelts
        for s in (BJsales, Seatbelts):
            assert np.array_equal(
                s.xreg, np.concatenate([s.xregx, s.xregxx])
            )
            # Field names survive the slice
            assert s.xregx.dtype.names == s.xreg.dtype.names
            assert s.xregxx.dtype.names == s.xreg.dtype.names

    def test_dict_and_attribute_access_equivalent(self):
        from fcompdata import AirPassengers, BJsales
        assert AirPassengers["x"] is AirPassengers.x
        assert AirPassengers["h"] == AirPassengers.h
        assert BJsales["xreg"] is BJsales.xreg

    def test_keys_includes_xreg(self):
        from fcompdata import AirPassengers
        keys = AirPassengers.keys()
        for required in ("xreg", "xregx", "xregxx"):
            assert required in keys

    def test_promodata(self):
        from fcompdata import PromoData
        assert PromoData.sn == "PromoData"
        assert PromoData.h == 13
        assert PromoData.period == 52
        assert PromoData.type == "weekly"
        assert PromoData.x.shape == (143,)
        assert PromoData.xx.shape == (13,)
        assert PromoData.xreg is not None
        assert PromoData.xreg.dtype.names == ("Promo1", "Promo2")
        assert len(PromoData.xreg) == 156
        assert len(PromoData.xregx) == 143
        assert len(PromoData.xregxx) == 13
        # Promo flags are binary 0/1
        assert set(np.unique(PromoData.xreg["Promo1"]).tolist()) <= {0.0, 1.0}
        assert set(np.unique(PromoData.xreg["Promo2"]).tolist()) <= {0.0, 1.0}

    def test_y_property_through_proxy(self):
        """y must work via the _LazySeries proxy for every individual series."""
        from fcompdata import AirPassengers, BJsales, PromoData, Seatbelts, taylor
        for s in (AirPassengers, BJsales, Seatbelts, taylor, PromoData):
            expected = np.concatenate([s.x, s.xx])
            assert np.array_equal(s.y, expected), s.sn
            assert len(s.y) == s.n + s.h, s.sn
            assert "y" in s.keys(), s.sn
