import os

from .helpers import check_each_generator_class_has_at_least_one_exemplar_instance

from ..context import tohu
from tohu.v6.primitive_generators import Boolean, CharString, Constant, Date, DigitString, Float, \
    GeoJSONGeolocation, Integer, HashDigest, FakerGenerator, Sequential, ShapelyGeolocation, Timestamp

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, "..", "..", "..", "tohu", "data")
geojson_sample_file = os.path.join(data_dir, "admin_0_countries.geojson")


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Boolean(p=0.8),
    Integer(100, 200),
    Float(low=12.3, high=45.6),
    CharString(length=12, charset="<alphanumeric_uppercase>"),
    DigitString(length=15),
    HashDigest(length=8),
    Sequential(prefix='Foo_', digits=3),
    FakerGenerator(method="name"),
    Timestamp(start="2018-01-01 11:22:33", end="2019-04-12 20:00:05"),
    Date(start="1999-04-01", end="2000-05-02"),
    GeoJSONGeolocation(geojson_sample_file, include_attributes=['name', 'pop_est'], max_tries=500),
]


check_each_generator_class_has_at_least_one_exemplar_instance(
    'tohu.v6.primitive_generators',
    EXEMPLAR_PRIMITIVE_GENERATORS,
    exclude_classes=[ShapelyGeolocation],
)
